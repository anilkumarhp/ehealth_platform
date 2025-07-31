from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Any
from pydantic import EmailStr, BaseModel
import uuid

from app.api.v1 import deps
from app.db import models
from app.crud import crud_organization, crud_user, crud_rbac
from app.api.v1.schemas import organization as org_schema
from app.api.v1.schemas import user as user_schema
from app.tasks.email_tasks import send_invitation_email

# --- Permission Dependency ---
def require_org_admin(current_user: models.User = Depends(deps.get_current_user)):
    """
    Dependency that checks if the current user has the 'Org Admin' role.
    """
    # --- THIS IS THE FIX ---
    # Check for "Org Admin" (with a space) to match what we create during registration.
    if "Org Admin" not in {role.name for role in current_user.roles}:
         raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This action requires ORG_ADMIN role")
    return current_user

router = APIRouter()

# --- Schemas for this router ---
class UserInviteRequest(BaseModel):
    email: EmailStr
    role: str = "PATIENT"

# --- Endpoints ---

@router.get("/organization/profile", response_model=org_schema.OrganizationRead)
def get_my_organization_profile(
    current_user: models.User = Depends(require_org_admin)
) -> Any:
    return current_user.organization

@router.put("/organization/profile", response_model=org_schema.OrganizationRead)
def update_my_organization_profile(
    *,
    db: Session = Depends(deps.get_db),
    org_in: org_schema.OrganizationUpdate,
    current_user: models.User = Depends(require_org_admin)
) -> Any:
    current_org = current_user.organization
    update_data = org_in.model_dump(exclude_unset=True)
    updated_org = crud_organization.update_organization(db=db, org=current_org, updates=update_data)
    return updated_org

@router.get("/organization/users", response_model=List[user_schema.UserRead])
def get_users_in_my_organization(
    role: str | None = None,
    is_active: bool | None = None,
    search: str | None = None,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(require_org_admin)
) -> Any:
    users = crud_organization.get_users_by_organization(
        db=db, org_id=current_user.organization_id, role=role, is_active=is_active, search=search
    )
    return users

@router.post("/organization/users/invite", response_model=user_schema.UserInviteResponse, status_code=status.HTTP_201_CREATED)
def invite_user_to_organization(
    *,
    db: Session = Depends(deps.get_public_db),
    # THIS IS THE CORRECTED SIGNATURE - 'invite_in' is now defined
    invite_in: UserInviteRequest,
    current_user: models.User = Depends(require_org_admin)
) -> Any:
    """
    ORG_ADMIN invites a new user to their organization.
    Creates an inactive user and dispatches an invitation email task.
    """
    user = crud_user.get_user_by_email(db, email=invite_in.email)
    if user:
        if user.organization_id == current_user.organization_id:
            raise HTTPException(status_code=400, detail="User with this email already exists in this organization.")
        else:
            raise HTTPException(status_code=409, detail="User with this email already exists in another organization.")

    invited_user = crud_user.create_invited_user(
        db=db, 
        email=invite_in.email, 
        role=invite_in.role, 
        organization_id=current_user.organization_id
    )

    # Dispatch the email sending to our background worker
    send_invitation_email.delay(
        email_to=invited_user.email, token=invited_user.invitation_token
    )
    
    print(f"Dispatched invitation email task for {invited_user.email}.")
    
    return invited_user

# Endpoint for assigning roles (PUT /organization/users/{user_id}/assign-roles) would go here
# ... (imports, router setup, schemas, other endpoints) ...

@router.put("/organization/users/{user_id}/assign-roles", response_model=user_schema.UserRead)
def assign_roles_to_a_user(
    user_id: uuid.UUID,
    role_ids: List[uuid.UUID], # Pass a list of role IDs in the request body
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(require_org_admin)
):
    """
    Assign a list of roles to a specific user in the organization.
    """
    user_to_update = crud_user.get_user_by_id(db, user_id=user_id)
    if not user_to_update or user_to_update.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="User not found in this organization.")

    return crud_rbac.assign_roles_to_user(db, user=user_to_update, role_ids=role_ids)


@router.put("/organization/users/{user_id}", response_model=user_schema.UserRead)
def update_user_in_organization(
    user_id: uuid.UUID,
    user_in: user_schema.UserUpdateByAdmin,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(require_org_admin)
):
    """
    Update a user's properties within the organization (e.g., active status).
    """
    user_to_update = crud_user.get_user_by_id(db, user_id=user_id)
    if not user_to_update or user_to_update.organization_id != current_user.organization_id:
        raise HTTPException(status_code=404, detail="User not found in this organization.")
    
    update_data = user_in.model_dump(exclude_unset=True)
    return crud_user.update_user(db, user=user_to_update, updates=update_data)