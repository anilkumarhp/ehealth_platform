"""
Populate database with test data for pharma management service
"""

import asyncio
import pandas as pd
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4
import json

from app.db.session import AsyncSessionLocal
from app.models.pharmacy import Pharmacy
from app.models.medicine import Medicine, MedicineBatch
from app.models.staff import PharmacyStaff
from app.models.prescription import Prescription, PrescriptionItem
from app.models.order import Order, OrderItem
from app.models.inventory import InventoryItem
from app.models.billing import Invoice, Payment
from app.models.compliance import AuditLog


# Test data
PHARMACIES_DATA = [
    {"name": "Apollo Pharmacy", "city": "Bangalore", "state": "Karnataka", "license_number": "KA001", "registration_number": "REG001", "email": "apollo.blr@example.com", "phone": "+91 9876543210"},
    {"name": "MedPlus", "city": "Hyderabad", "state": "Telangana", "license_number": "TS002", "registration_number": "REG002", "email": "medplus.hyd@example.com", "phone": "+91 9876543211"},
    {"name": "Wellness Forever", "city": "Mumbai", "state": "Maharashtra", "license_number": "MH003", "registration_number": "REG003", "email": "wellness.mum@example.com", "phone": "+91 9876543212"},
    {"name": "Netmeds", "city": "Chennai", "state": "Tamil Nadu", "license_number": "TN004", "registration_number": "REG004", "email": "netmeds.che@example.com", "phone": "+91 9876543213"},
    {"name": "PharmEasy", "city": "Delhi", "state": "Delhi", "license_number": "DL005", "registration_number": "REG005", "email": "pharmeasy.del@example.com", "phone": "+91 9876543214"},
    {"name": "1mg", "city": "Gurgaon", "state": "Haryana", "license_number": "HR006", "registration_number": "REG006", "email": "1mg.gur@example.com", "phone": "+91 9876543215"},
    {"name": "Cipla Health", "city": "Pune", "state": "Maharashtra", "license_number": "MH007", "registration_number": "REG007", "email": "cipla.pune@example.com", "phone": "+91 9876543216"},
    {"name": "Sun Pharma", "city": "Ahmedabad", "state": "Gujarat", "license_number": "GJ008", "registration_number": "REG008", "email": "sun.ahm@example.com", "phone": "+91 9876543217"},
    {"name": "Dr. Reddy's", "city": "Kolkata", "state": "West Bengal", "license_number": "WB009", "registration_number": "REG009", "email": "reddy.kol@example.com", "phone": "+91 9876543218"},
    {"name": "Lupin Pharmacy", "city": "Jaipur", "state": "Rajasthan", "license_number": "RJ010", "registration_number": "REG010", "email": "lupin.jai@example.com", "phone": "+91 9876543219"}
]

MEDICINES_DATA = [
    {"name": "Paracetamol", "generic_name": "Acetaminophen", "manufacturer": "Cipla", "strength": "500mg", "dosage_form": "Tablet", "unit_price": 2.50},
    {"name": "Amoxicillin", "generic_name": "Amoxicillin", "manufacturer": "Sun Pharma", "strength": "250mg", "dosage_form": "Capsule", "unit_price": 15.00},
    {"name": "Metformin", "generic_name": "Metformin HCl", "manufacturer": "Dr. Reddy's", "strength": "500mg", "dosage_form": "Tablet", "unit_price": 8.75},
    {"name": "Amlodipine", "generic_name": "Amlodipine Besylate", "manufacturer": "Lupin", "strength": "5mg", "dosage_form": "Tablet", "unit_price": 12.30},
    {"name": "Omeprazole", "generic_name": "Omeprazole", "manufacturer": "Ranbaxy", "strength": "20mg", "dosage_form": "Capsule", "unit_price": 18.50},
    {"name": "Atorvastatin", "generic_name": "Atorvastatin Calcium", "manufacturer": "Pfizer", "strength": "10mg", "dosage_form": "Tablet", "unit_price": 25.00},
    {"name": "Losartan", "generic_name": "Losartan Potassium", "manufacturer": "Torrent", "strength": "50mg", "dosage_form": "Tablet", "unit_price": 14.75},
    {"name": "Cetirizine", "generic_name": "Cetirizine HCl", "manufacturer": "Glenmark", "strength": "10mg", "dosage_form": "Tablet", "unit_price": 6.25},
    {"name": "Azithromycin", "generic_name": "Azithromycin", "manufacturer": "Zydus", "strength": "500mg", "dosage_form": "Tablet", "unit_price": 45.00},
    {"name": "Insulin Glargine", "generic_name": "Insulin Glargine", "manufacturer": "Sanofi", "strength": "100IU/ml", "dosage_form": "Injection", "unit_price": 850.00}
]

STAFF_DATA = [
    {"first_name": "Dr. Rajesh", "last_name": "Kumar", "email": "rajesh.kumar@example.com", "phone": "+91 9876543220", "role": "pharmacist", "license_number": "PH001"},
    {"first_name": "Priya", "last_name": "Sharma", "email": "priya.sharma@example.com", "phone": "+91 9876543221", "role": "pharmacy_technician", "license_number": "PT001"},
    {"first_name": "Amit", "last_name": "Singh", "email": "amit.singh@example.com", "phone": "+91 9876543222", "role": "store_manager", "license_number": "SM001"},
    {"first_name": "Sneha", "last_name": "Patel", "email": "sneha.patel@example.com", "phone": "+91 9876543223", "role": "cashier", "license_number": "CA001"},
    {"first_name": "Ravi", "last_name": "Gupta", "email": "ravi.gupta@example.com", "phone": "+91 9876543224", "role": "delivery_person", "license_number": "DP001"},
    {"first_name": "Dr. Meera", "last_name": "Nair", "email": "meera.nair@example.com", "phone": "+91 9876543225", "role": "pharmacist", "license_number": "PH002"},
    {"first_name": "Kiran", "last_name": "Reddy", "email": "kiran.reddy@example.com", "phone": "+91 9876543226", "role": "pharmacy_technician", "license_number": "PT002"},
    {"first_name": "Suresh", "last_name": "Yadav", "email": "suresh.yadav@example.com", "phone": "+91 9876543227", "role": "admin", "license_number": "AD001"},
    {"first_name": "Kavya", "last_name": "Iyer", "email": "kavya.iyer@example.com", "phone": "+91 9876543228", "role": "cashier", "license_number": "CA002"},
    {"first_name": "Vikram", "last_name": "Joshi", "email": "vikram.joshi@example.com", "phone": "+91 9876543229", "role": "delivery_person", "license_number": "DP002"}
]


async def populate_database():
    """Populate database with test data"""
    async with AsyncSessionLocal() as db:
        try:
            # Create pharmacies
            pharmacy_ids = []
            for i, data in enumerate(PHARMACIES_DATA):
                pharmacy_id = uuid4()
                pharmacy_ids.append(pharmacy_id)
                
                pharmacy = Pharmacy(
                    id=pharmacy_id,
                    name=data["name"],
                    license_number=data["license_number"],
                    registration_number=data["registration_number"],
                    email=data["email"],
                    phone=data["phone"],
                    address_line1=f"{i+1}, Main Street",
                    city=data["city"],
                    state=data["state"],
                    postal_code=f"5600{i:02d}",
                    country="India",
                    owner_name=f"Owner {i+1}",
                    pharmacist_in_charge=f"Pharmacist {i+1}",
                    verification_status="verified",
                    operational_status="active",
                    delivery_radius_km=10.0,
                    home_delivery_available=True
                )
                db.add(pharmacy)
            
            # Create medicines
            medicine_ids = []
            for i, data in enumerate(MEDICINES_DATA):
                medicine_id = uuid4()
                medicine_ids.append(medicine_id)
                
                medicine = Medicine(
                    id=medicine_id,
                    name=data["name"],
                    generic_name=data["generic_name"],
                    manufacturer=data["manufacturer"],
                    strength=data["strength"],
                    dosage_form=data["dosage_form"],
                    route_of_administration="oral",
                    active_ingredients=[data["generic_name"]],
                    unit_price=Decimal(str(data["unit_price"])),
                    prescription_required=True,
                    controlled_substance=False
                )
                db.add(medicine)
            
            await db.commit()
            
            # Create staff members
            for i, data in enumerate(STAFF_DATA):
                staff = PharmacyStaff(
                    id=uuid4(),
                    pharmacy_id=pharmacy_ids[i % len(pharmacy_ids)],
                    user_id=uuid4(),
                    first_name=data["first_name"],
                    last_name=data["last_name"],
                    email=data["email"],
                    phone=data["phone"],
                    role=data["role"],
                    license_number=data["license_number"],
                    hire_date=date.today() - timedelta(days=30*i),
                    can_validate_prescriptions=data["role"] == "pharmacist",
                    can_dispense_controlled_substances=data["role"] == "pharmacist",
                    can_manage_inventory=data["role"] in ["pharmacist", "store_manager"],
                    can_process_payments=data["role"] in ["cashier", "pharmacist"]
                )
                db.add(staff)
            
            await db.commit()
            print("✅ Database populated successfully!")
            
            # Save to Excel
            await save_to_excel(pharmacy_ids, medicine_ids)
            
        except Exception as e:
            await db.rollback()
            print(f"❌ Error populating database: {e}")
            raise


async def save_to_excel(pharmacy_ids, medicine_ids):
    """Save test data to Excel file"""
    
    # Prepare data for Excel
    excel_data = {}
    
    # Pharmacies sheet
    pharmacies_df = pd.DataFrame([
        {
            "ID": str(pharmacy_ids[i]),
            "Name": data["name"],
            "City": data["city"],
            "State": data["state"],
            "License Number": data["license_number"],
            "Registration Number": data["registration_number"],
            "Email": data["email"],
            "Phone": data["phone"]
        }
        for i, data in enumerate(PHARMACIES_DATA)
    ])
    excel_data["Pharmacies"] = pharmacies_df
    
    # Medicines sheet
    medicines_df = pd.DataFrame([
        {
            "ID": str(medicine_ids[i]),
            "Name": data["name"],
            "Generic Name": data["generic_name"],
            "Manufacturer": data["manufacturer"],
            "Strength": data["strength"],
            "Dosage Form": data["dosage_form"],
            "Unit Price": data["unit_price"]
        }
        for i, data in enumerate(MEDICINES_DATA)
    ])
    excel_data["Medicines"] = medicines_df
    
    # Staff sheet
    staff_df = pd.DataFrame([
        {
            "First Name": data["first_name"],
            "Last Name": data["last_name"],
            "Email": data["email"],
            "Phone": data["phone"],
            "Role": data["role"],
            "License Number": data["license_number"],
            "Pharmacy": PHARMACIES_DATA[i % len(PHARMACIES_DATA)]["name"]
        }
        for i, data in enumerate(STAFF_DATA)
    ])
    excel_data["Staff"] = staff_df
    
    # Save to Excel in logs directory (mounted volume)
    excel_path = "/app/logs/pharma_test_data.xlsx"
    with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
        for sheet_name, df in excel_data.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
    
    print(f"📊 Test data saved to {excel_path}")


if __name__ == "__main__":
    asyncio.run(populate_database())