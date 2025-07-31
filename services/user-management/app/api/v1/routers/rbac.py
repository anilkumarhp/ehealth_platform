from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db import models
import uuid

from app.api.v1 import deps
from app.crud import crud_rbac
from app.api.v1.schemas import rbac as rbac_schema

# Use the powerful permission dependency we created
require_role_management = deps.require_permission("role:manage") # Placeholder for now

router = APIRouter()

@router.get("/permissions", response_model=List[rbac_schema.PermissionRead])
def list_all_permissions(db: Session = Depends(deps.get_public_db)):
    """Get a list of all possible permissions in the system."""
    return crud_rbac.get_all_permissions(db)

@router.get("/roles", response_model=List[rbac_schema.RoleRead])
def get_organization_roles(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user) # Using get_current_user to get org_id
):
    """List all roles for the current user's organization."""
    return crud_rbac.get_roles_by_organization(db, org_id=current_user.organization_id)

@router.post("/roles", response_model=rbac_schema.RoleRead, status_code=status.HTTP_201_CREATED)
def create_role(
    role_in: rbac_schema.RoleCreate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user) # Placeholder for proper permission check
):
    """Create a new custom role within the admin's organization."""
    if crud_rbac.get_role_by_name(db, name=role_in.name, org_id=current_user.organization_id):
        raise HTTPException(status_code=400, detail="A role with this name already exists.")
    return crud_rbac.create_role(db=db, role_in=role_in, org_id=current_user.organization_id)

@router.put("/roles/{role_id}", response_model=rbac_schema.RoleRead)
def update_role(
    role_id: uuid.UUID,
    role_in: rbac_schema.RoleUpdate,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user)
):
    """Update a role's name, description, and permissions."""
    role = crud_rbac.get_role_by_id(db, role_id=role_id, org_id=current_user.organization_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")
    return crud_rbac.update_role(db, role=role, role_in=role_in)


# ... (imports and other endpoints) ...

@router.delete("/roles/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_role(
    role_id: uuid.UUID,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_user) # Add appropriate permission check
):
    """
    Delete a custom role within the organization.
    """
    role = crud_rbac.get_role_by_id(db, role_id=role_id, org_id=current_user.organization_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found.")
    if role.name == "Org Admin": # Prevent deletion of the default admin role
        raise HTTPException(status_code=400, detail="Cannot delete the default admin role.")
        
    crud_rbac.delete_role(db, role=role)
    return