"""Initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create pharmacies table
    op.create_table('pharmacies',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('license_number', sa.String(length=100), nullable=False),
        sa.Column('registration_number', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('phone', sa.String(length=20), nullable=False),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('address_line1', sa.String(length=255), nullable=False),
        sa.Column('address_line2', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('state', sa.String(length=100), nullable=False),
        sa.Column('postal_code', sa.String(length=20), nullable=False),
        sa.Column('country', sa.String(length=100), nullable=False),
        sa.Column('latitude', sa.Numeric(precision=10, scale=8), nullable=True),
        sa.Column('longitude', sa.Numeric(precision=11, scale=8), nullable=True),
        sa.Column('operating_hours', sa.JSON(), nullable=True),
        sa.Column('delivery_radius_km', sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column('home_delivery_available', sa.Boolean(), nullable=False),
        sa.Column('dea_number', sa.String(length=50), nullable=True),
        sa.Column('state_license_expiry', sa.String(length=20), nullable=True),
        sa.Column('certifications', sa.JSON(), nullable=True),
        sa.Column('owner_name', sa.String(length=255), nullable=False),
        sa.Column('pharmacist_in_charge', sa.String(length=255), nullable=False),
        sa.Column('tax_id', sa.String(length=50), nullable=True),
        sa.Column('auto_refill_enabled', sa.Boolean(), nullable=False),
        sa.Column('generic_substitution_allowed', sa.Boolean(), nullable=False),
        sa.Column('insurance_accepted', sa.JSON(), nullable=True),
        sa.Column('verification_status', sa.String(length=50), nullable=False),
        sa.Column('operational_status', sa.String(length=50), nullable=False),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create medicines table
    op.create_table('medicines',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('generic_name', sa.String(length=255), nullable=False),
        sa.Column('brand_name', sa.String(length=255), nullable=True),
        sa.Column('manufacturer', sa.String(length=255), nullable=False),
        sa.Column('ndc_number', sa.String(length=50), nullable=True),
        sa.Column('fda_approval_number', sa.String(length=100), nullable=True),
        sa.Column('drug_schedule', sa.String(length=10), nullable=True),
        sa.Column('active_ingredients', sa.JSON(), nullable=False),
        sa.Column('strength', sa.String(length=100), nullable=False),
        sa.Column('dosage_form', sa.String(length=100), nullable=False),
        sa.Column('route_of_administration', sa.String(length=100), nullable=False),
        sa.Column('therapeutic_class', sa.String(length=255), nullable=True),
        sa.Column('pharmacological_class', sa.String(length=255), nullable=True),
        sa.Column('atc_code', sa.String(length=20), nullable=True),
        sa.Column('prescription_required', sa.Boolean(), nullable=False),
        sa.Column('controlled_substance', sa.Boolean(), nullable=False),
        sa.Column('storage_temperature_min', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('storage_temperature_max', sa.Numeric(precision=5, scale=2), nullable=True),
        sa.Column('storage_conditions', sa.Text(), nullable=True),
        sa.Column('unit_price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('insurance_copay', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('generic_alternatives', sa.JSON(), nullable=True),
        sa.Column('brand_alternatives', sa.JSON(), nullable=True),
        sa.Column('contraindications', sa.JSON(), nullable=True),
        sa.Column('drug_interactions', sa.JSON(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('side_effects', sa.JSON(), nullable=True),
        sa.Column('warnings', sa.JSON(), nullable=True),
        sa.Column('created_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('updated_by', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    op.drop_table('medicines')
    op.drop_table('pharmacies')