"""Add created_at and updated_at to roles table

Revision ID: add_timestamps_to_roles
Revises: c31503c45029
Create Date: 2023-07-10 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_timestamps_to_roles'
down_revision = 'c31503c45029'
branch_labels = None
depends_on = None


def upgrade():
    # Add created_at and updated_at columns to roles table
    op.add_column('roles', sa.Column('created_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False))
    op.add_column('roles', sa.Column('updated_at', sa.TIMESTAMP(timezone=True), server_default=sa.text('NOW()'), nullable=False))


def downgrade():
    # Remove created_at and updated_at columns from roles table
    op.drop_column('roles', 'updated_at')
    op.drop_column('roles', 'created_at')