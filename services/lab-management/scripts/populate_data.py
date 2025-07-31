#!/usr/bin/env python3
"""
Data population script for Lab Management Service.
Creates sample data following the API flow with proper foreign key relationships.
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import uuid
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.models.lab_service import LabService
from app.models.test_definition import TestDefinition
from app.models.test_order import TestOrder, TestOrderStatusEnum
from app.models.appointment import Appointment, AppointmentStatusEnum


# Predefined UUIDs for consistent relationships
LAB_IDS = [
    uuid.UUID("10000000-1000-4000-8000-100000000001"),
    uuid.UUID("10000000-1000-4000-8000-100000000002"),
    uuid.UUID("10000000-1000-4000-8000-100000000003"),
]

PATIENT_IDS = [
    uuid.UUID("20000000-2000-4000-8000-200000000001"),
    uuid.UUID("20000000-2000-4000-8000-200000000002"),
    uuid.UUID("20000000-2000-4000-8000-200000000003"),
]

DOCTOR_IDS = [
    uuid.UUID("30000000-3000-4000-8000-300000000001"),
    uuid.UUID("30000000-3000-4000-8000-300000000002"),
    uuid.UUID("30000000-3000-4000-8000-300000000003"),
]


async def create_lab_services(session: AsyncSession):
    """Create lab services with test definitions."""
    print("Creating lab services...")
    
    services_data = [
        {
            "name": "Complete Blood Count (CBC)",
            "description": "Comprehensive blood analysis including cell counts",
            "price": Decimal("85.00"),
            "lab_id": LAB_IDS[0],
            "test_definitions": [
                {"name": "White Blood Cell Count", "unit": "cells/mcL", "reference_range": "4,000-11,000"},
                {"name": "Red Blood Cell Count", "unit": "million cells/mcL", "reference_range": "4.5-5.5"},
                {"name": "Hemoglobin", "unit": "g/dL", "reference_range": "12.0-15.5"},
                {"name": "Hematocrit", "unit": "%", "reference_range": "36-46"},
            ]
        },
        {
            "name": "Basic Metabolic Panel",
            "description": "Essential metabolic markers",
            "price": Decimal("65.00"),
            "lab_id": LAB_IDS[0],
            "test_definitions": [
                {"name": "Glucose", "unit": "mg/dL", "reference_range": "70-100"},
                {"name": "Sodium", "unit": "mEq/L", "reference_range": "136-145"},
                {"name": "Potassium", "unit": "mEq/L", "reference_range": "3.5-5.0"},
                {"name": "Creatinine", "unit": "mg/dL", "reference_range": "0.6-1.2"},
            ]
        },
        {
            "name": "Lipid Panel",
            "description": "Cholesterol and lipid analysis",
            "price": Decimal("75.00"),
            "lab_id": LAB_IDS[1],
            "test_definitions": [
                {"name": "Total Cholesterol", "unit": "mg/dL", "reference_range": "<200"},
                {"name": "HDL Cholesterol", "unit": "mg/dL", "reference_range": ">40"},
                {"name": "LDL Cholesterol", "unit": "mg/dL", "reference_range": "<100"},
                {"name": "Triglycerides", "unit": "mg/dL", "reference_range": "<150"},
            ]
        },
        {
            "name": "Thyroid Function Panel",
            "description": "Comprehensive thyroid hormone analysis",
            "price": Decimal("95.00"),
            "lab_id": LAB_IDS[1],
            "test_definitions": [
                {"name": "TSH", "unit": "mIU/L", "reference_range": "0.4-4.0"},
                {"name": "Free T4", "unit": "ng/dL", "reference_range": "0.8-1.8"},
                {"name": "Free T3", "unit": "pg/mL", "reference_range": "2.3-4.2"},
            ]
        },
        {
            "name": "Liver Function Panel",
            "description": "Liver enzyme and function tests",
            "price": Decimal("80.00"),
            "lab_id": LAB_IDS[2],
            "test_definitions": [
                {"name": "ALT", "unit": "U/L", "reference_range": "7-56"},
                {"name": "AST", "unit": "U/L", "reference_range": "10-40"},
                {"name": "Bilirubin Total", "unit": "mg/dL", "reference_range": "0.3-1.2"},
                {"name": "Albumin", "unit": "g/dL", "reference_range": "3.5-5.0"},
            ]
        }
    ]
    
    created_services = []
    
    for service_data in services_data:
        # Create lab service
        lab_service = LabService(
            name=service_data["name"],
            description=service_data["description"],
            price=service_data["price"],
            lab_id=service_data["lab_id"],
            is_active=True
        )
        session.add(lab_service)
        await session.flush()
        await session.refresh(lab_service)
        
        # Create test definitions
        for test_def_data in service_data["test_definitions"]:
            test_definition = TestDefinition(
                name=test_def_data["name"],
                unit=test_def_data["unit"],
                reference_range=test_def_data["reference_range"],
                service_id=lab_service.id
            )
            session.add(test_definition)
        
        created_services.append(lab_service)
        print(f"  Created service: {lab_service.name}")
    
    await session.flush()
    return created_services


async def create_test_orders(session: AsyncSession, lab_services):
    """Create test orders for patients."""
    print("Creating test orders...")
    
    orders_data = [
        {
            "patient_id": PATIENT_IDS[0],
            "doctor_id": DOCTOR_IDS[0],
            "lab_id": LAB_IDS[0],
            "service": lab_services[0],  # CBC
            "clinical_notes": "Routine annual checkup - complete blood work requested"
        },
        {
            "patient_id": PATIENT_IDS[0],
            "doctor_id": DOCTOR_IDS[0],
            "lab_id": LAB_IDS[0],
            "service": lab_services[1],  # Basic Metabolic Panel
            "clinical_notes": "Follow-up for diabetes management"
        },
        {
            "patient_id": PATIENT_IDS[1],
            "doctor_id": DOCTOR_IDS[1],
            "lab_id": LAB_IDS[1],
            "service": lab_services[2],  # Lipid Panel
            "clinical_notes": "Cardiovascular risk assessment"
        },
        {
            "patient_id": PATIENT_IDS[1],
            "doctor_id": DOCTOR_IDS[1],
            "lab_id": LAB_IDS[1],
            "service": lab_services[3],  # Thyroid Panel
            "clinical_notes": "Fatigue and weight gain symptoms"
        },
        {
            "patient_id": PATIENT_IDS[2],
            "doctor_id": DOCTOR_IDS[2],
            "lab_id": LAB_IDS[2],
            "service": lab_services[4],  # Liver Function
            "clinical_notes": "Elevated liver enzymes follow-up"
        }
    ]
    
    created_orders = []
    
    for order_data in orders_data:
        test_order = TestOrder(
            patient_user_id=order_data["patient_id"],
            requesting_entity_id=order_data["doctor_id"],
            organization_id=order_data["lab_id"],
            lab_service_id=order_data["service"].id,
            status=TestOrderStatusEnum.PENDING_CONSENT,
            clinical_notes=order_data["clinical_notes"]
        )
        session.add(test_order)
        created_orders.append(test_order)
        print(f"  Created order: {order_data['service'].name} for patient {order_data['patient_id']}")
    
    await session.flush()
    return created_orders


async def create_appointments(session: AsyncSession, test_orders):
    """Create appointments for some test orders."""
    print("Creating appointments...")
    
    # Create appointments for first 3 orders
    base_time = datetime.now() + timedelta(days=1)
    
    for i, test_order in enumerate(test_orders[:3]):
        appointment_time = base_time + timedelta(hours=i*2)
        
        appointment = Appointment(
            patient_user_id=test_order.patient_user_id,
            lab_id=test_order.organization_id,
            lab_service_id=test_order.lab_service_id,
            test_order_id=test_order.id,
            appointment_time=appointment_time,
            status=AppointmentStatusEnum.SCHEDULED
        )
        session.add(appointment)
        print(f"  Created appointment: {appointment_time} for order {test_order.id}")
        
        # Update test order status
        test_order.status = TestOrderStatusEnum.AWAITING_APPOINTMENT
    
    await session.flush()


async def populate_database():
    """Main function to populate the database with sample data."""
    print("🚀 Starting database population...")
    
    # Create async engine and session
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(bind=engine, expire_on_commit=False)
    
    # Create all tables
    print("📋 Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully!")
    
    try:
        async with async_session() as session:
            # Create data in proper order
            lab_services = await create_lab_services(session)
            test_orders = await create_test_orders(session, lab_services)
            await create_appointments(session, test_orders)
            
            # Commit all changes
            await session.commit()
            print("✅ Database population completed successfully!")
            
            # Print summary
            print(f"\n📊 Summary:")
            print(f"  - Lab Services: {len(lab_services)}")
            print(f"  - Test Orders: {len(test_orders)}")
            print(f"  - Appointments: 3")
            print(f"  - Labs: {len(LAB_IDS)}")
            print(f"  - Patients: {len(PATIENT_IDS)}")
            print(f"  - Doctors: {len(DOCTOR_IDS)}")
            
    except Exception as e:
        print(f"❌ Error populating database: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    asyncio.run(populate_database())