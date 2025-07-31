"""add image urls to user

Revision ID: add_image_urls_to_user
Revises: 
Create Date: 2023-07-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_image_urls_to_user'
down_revision = 'b6e299cb0abb'  # Previous migration ID
branch_labels = None
depends_on = None


def upgrade():
    # Add profile_photo_url and s3_bucket_name columns to users table
    op.add_column('users', sa.Column('profile_photo_url', sa.String(500), nullable=True))
    op.add_column('users', sa.Column('s3_bucket_name', sa.String(255), nullable=True))


def downgrade():
    # Remove the columns
    op.drop_column('users', 'profile_photo_url')
    op.drop_column('users', 's3_bucket_name')