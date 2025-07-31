"""Create default patients organization

Revision ID: 12345678abcd
Revises: (use the latest revision ID from your alembic versions)
Create Date: 2023-07-21 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Define the fixed UUID for the Patients organization
PATIENTS_ORG_UUID = uuid.UUID('11111111-1111-1111-1111-111111111111')

# revision identifiers, used by Alembic
revision = '12345678abcd'
down_revision = None  # Update this to your latest migration
branch_labels = None
depends_on = None

def upgrade():
    # Check if the Patients organization already exists
    conn = op.get_bind()
    result = conn.execute(
        sa.text("SELECT id FROM organizations WHERE name = 'Patients'")
    ).fetchone()
    
    if not result:
        # Insert the Patients organization with the fixed UUID
        op.execute(
            sa.text(
                "INSERT INTO organizations (id, name, is_active, subscription_tier, created_at, updated_at) "
                "VALUES (:id, :name, :is_active, :subscription_tier, NOW(), NOW())"
            ),
            {
                "id": PATIENTS_ORG_UUID,
                "name": "Patients",
                "is_active": True,
                "subscription_tier": "FREE"
            }
        )
        print("Created default 'Patients' organization with fixed UUID")
    else:
        print("'Patients' organization already exists")

def downgrade():
    # We don't want to remove the Patients organization on downgrade
    pass