import uuid
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Dict, Any

from app.db import models
from app.api.v1.schemas import organization as org_schema

def get_organization_by_id(db: Session, org_id: uuid.UUID) -> models.Organization | None:
    """Gets an organization by its ID."""
    return db.query(models.Organization).filter(models.Organization.id == org_id).first()

def create_organization(db: Session, organization: org_schema.OrganizationCreate) -> models.Organization:
    # Create organization with optional ID
    db_organization = models.Organization(
        id=organization.id if organization.id else uuid.uuid4(),
        name=organization.name,
        type=organization.type,
        registration_number=organization.registration_number,
        abha_facility_id=organization.abha_facility_id,
        license_details=organization.license_details,
        address=organization.address.model_dump() if organization.address else None,
        contact_info=organization.contact_info.model_dump() if organization.contact_info else None,
        subscription_tier=organization.subscription_tier or "FREE"
    )
    db.add(db_organization)
    # The commit is handled by the calling function in a transaction
    return db_organization

def update_organization(db: Session, *, org: models.Organization, updates: Dict[str, Any]) -> models.Organization:
    # ... (no changes)
    for key, value in updates.items():
        setattr(org, key, value)
    db.add(org)
    db.commit()
    db.refresh(org)
    return org

def get_users_by_organization(db: Session, *, org_id: uuid.UUID, role: str | None = None, is_active: bool | None = None, search: str | None = None) -> list[models.User]:
    # ... (no changes)
    query = db.query(models.User).filter(models.User.organization_id == org_id)
    if is_active is not None:
        query = query.filter(models.User.is_active == is_active)
    if role:
        query = query.join(models.User.roles).filter(models.Role.name == role)
    if search:
        search_term = f"%{search.lower()}%"
        query = query.filter(or_(models.User.email.ilike(search_term), models.User.personal_info['first_name'].astext().ilike(search_term), models.User.personal_info['last_name'].astext().ilike(search_term)))
    return query.order_by(models.User.created_at.desc()).all()