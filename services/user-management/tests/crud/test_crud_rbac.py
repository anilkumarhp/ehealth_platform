from sqlalchemy.orm import Session
import uuid

from app.crud import crud_rbac, crud_user, crud_organization
from app.db import models
from app.api.v1.schemas import rbac as rbac_schema
from app.api.v1.schemas import user as user_schema
from app.api.v1.schemas import organization as org_schema

def test_create_role(db_session: Session):
    """
    Unit test for creating a new role.
    """
    org = crud_organization.create_organization(db_session, organization=org_schema.OrganizationCreate(name="Test Org for Roles"))
    db_session.commit()
    db_session.refresh(org)
    assert org.id is not None, "Organization ID should not be None after commit"

    role_in = rbac_schema.RoleCreate(name="Test Role", description="A test role")
    created_role = crud_rbac.create_role(db_session, role_in=role_in, org_id=org.id)
    db_session.commit()

    assert created_role is not None
    assert created_role.name == "Test Role"
    
    db_role = db_session.query(models.Role).filter(models.Role.id == created_role.id).first()
    assert db_role is not None
    assert db_role.name == "Test Role"

def test_assign_roles_to_user(db_session: Session):
    """
    Unit test for assigning roles to a user, with explicit transaction management.
    """
    # STEP 1: Create Organization and commit to get its ID
    org = crud_organization.create_organization(db_session, organization=org_schema.OrganizationCreate(name="Test Org for Assignment"))
    db_session.commit()
    db_session.refresh(org)
    assert org.id is not None, "Organization ID should not be None"

    # STEP 2: Create a User and commit to get its ID
    user_in = user_schema.UserCreate(email=f"test_assign_{uuid.uuid4()}@test.com", password="pw", primary_phone=str(uuid.uuid4().int)[:10])
    user = crud_user.create_user(db_session, user=user_in, organization_id=org.id)
    db_session.commit()
    db_session.refresh(user)
    assert user.id is not None, "User ID should not be None"

    # STEP 3: Create a Role and commit to get its ID
    role_in = rbac_schema.RoleCreate(name="Assignee Role", description="A role to be assigned")
    role = crud_rbac.create_role(db_session, role_in=role_in, org_id=org.id)
    db_session.commit()
    db_session.refresh(role)
    assert role.id is not None, "Role ID should not be None"

    # STEP 4: Now, assign the role to the user
    updated_user = crud_rbac.assign_roles_to_user(db_session, user=user, role_ids=[role.id])
    
    # Assert the assignment
    assert updated_user is not None
    assert len(updated_user.roles) == 1
    assert updated_user.roles[0].name == "Assignee Role"
