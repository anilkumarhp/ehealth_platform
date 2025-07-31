"""Add file attachments table

Revision ID: add_file_attachments
Revises: a48744b73ac9
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'add_file_attachments'
down_revision = 'a48744b73ac9'
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Create file_attachments table
    op.create_table('file_attachments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('file_category', sa.String(length=50), nullable=False),
        sa.Column('test_order_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('appointment_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('uploaded_by', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('upload_datetime', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id'], ),
        sa.ForeignKeyConstraint(['test_order_id'], ['test_orders.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_file_attachments_appointment_id'), 'file_attachments', ['appointment_id'], unique=False)
    op.create_index(op.f('ix_file_attachments_file_category'), 'file_attachments', ['file_category'], unique=False)
    op.create_index(op.f('ix_file_attachments_test_order_id'), 'file_attachments', ['test_order_id'], unique=False)
    op.create_index(op.f('ix_file_attachments_uploaded_by'), 'file_attachments', ['uploaded_by'], unique=False)

def downgrade() -> None:
    # Drop file_attachments table
    op.drop_index(op.f('ix_file_attachments_uploaded_by'), table_name='file_attachments')
    op.drop_index(op.f('ix_file_attachments_test_order_id'), table_name='file_attachments')
    op.drop_index(op.f('ix_file_attachments_file_category'), table_name='file_attachments')
    op.drop_index(op.f('ix_file_attachments_appointment_id'), table_name='file_attachments')
    op.drop_table('file_attachments')