from sqlalchemy.orm import Session
import uuid

from app.crud import crud_user, crud_organization
from app.db import models
from app.api.v1.schemas import user as user_schema
from app.api.v1.schemas import organization as org_schema

def test_create_user(db_session: Session):
    """
    Unit test for creating a new user.
    """
    # 1. Create an organization and COMMIT it to get a real ID
    org = crud_organization.create_organization(db_session, organization=org_schema.OrganizationCreate(name="Test Org for User"))
    db_session.commit()
    db_session.refresh(org)
    
    assert org.id is not None

    # 2. Now create the user with the valid organization ID
    user_in = user_schema.UserCreate(
        email=f"unit_test_{uuid.uuid4()}@test.com",
        password="pw",
        primary_phone=str(uuid.uuid4().int)[:10]
    )
    created_user = crud_user.create_user(db_session, user=user_in, organization_id=org.id)
    db_session.commit()
    db_session.refresh(created_user)

    # 3. Assert the user was created correctly
    assert created_user is not None
    assert created_user.email == user_in.email
    assert created_user.organization_id == org.id
    assert created_user.is_active is True