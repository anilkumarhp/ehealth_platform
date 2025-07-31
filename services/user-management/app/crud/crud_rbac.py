import uuid
from sqlalchemy.orm import Session
from typing import List

from app.db import models
from app.api.v1.schemas import rbac as rbac_schema
from app.core.exceptions import DetailException

def get_all_permissions(db: Session) -> list[models.Permission]:
    return db.query(models.Permission).order_by(models.Permission.name).all()

def get_role_by_id(db: Session, role_id: uuid.UUID, org_id: uuid.UUID) -> models.Role | None:
    return db.query(models.Role).filter(models.Role.id == role_id, models.Role.organization_id == org_id).first()

def get_role_by_name(db: Session, name: str, org_id: uuid.UUID) -> models.Role | None:
    return db.query(models.Role).filter(models.Role.name == name, models.Role.organization_id == org_id).first()

def get_roles_by_organization(db: Session, org_id: uuid.UUID) -> list[models.Role]:
    return db.query(models.Role).filter(models.Role.organization_id == org_id).order_by(models.Role.name).all()

def create_role(db: Session, role_in: rbac_schema.RoleCreate, org_id: uuid.UUID) -> models.Role:
    db_role = models.Role(name=role_in.name, description=role_in.description, organization_id=org_id)
    if role_in.permission_ids:
        permissions = db.query(models.Permission).filter(models.Permission.id.in_(role_in.permission_ids)).all()
        db_role.permissions.extend(permissions)
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def update_role(db: Session, role: models.Role, role_in: rbac_schema.RoleUpdate) -> models.Role:
    role.name = role_in.name
    role.description = role_in.description
    if role_in.permission_ids is not None:
        permissions = db.query(models.Permission).filter(models.Permission.id.in_(role_in.permission_ids)).all()
        role.permissions = permissions
    db.add(role)
    db.commit()
    db.refresh(role)
    return role
    
def assign_roles_to_user(db: Session, user: models.User, role_ids: List[uuid.UUID]) -> models.User:
    roles = db.query(models.Role).filter(models.Role.id.in_(role_ids)).all()
    if any(role.organization_id != user.organization_id for role in roles):
        raise DetailException(detail="Cannot assign roles from a different organization.")
    user.roles = roles
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def delete_role(db: Session, role: models.Role):
    """Deletes a role from the database."""
    db.delete(role)
    db.commit()
    return True


    
