import httpx
import uuid
from datetime import datetime

async def send_notification(notification_data):
    """Send a notification to the notification service"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://notification-api:8004/api/v1/notifications/",
            json=notification_data
        )
        return response.json()

# Example: Prescription ready notification
async def send_prescription_ready_notification(patient_id, medication_name, pharmacy_name):
    notification = {
        "id": str(uuid.uuid4()),
        "service": "pharma_management",
        "type": "success",
        "title": "Prescription Ready",
        "message": f"Your prescription for {medication_name} is ready for pickup at {pharmacy_name}",
        "user_id": patient_id,
        "created_at": datetime.now().isoformat(),
        "data": {"medication_name": medication_name, "pharmacy_name": pharmacy_name}
    }
    return await send_notification(notification)

# Example: Medication refill reminder notification
async def send_refill_reminder_notification(patient_id, medication_name, days_remaining):
    notification = {
        "id": str(uuid.uuid4()),
        "service": "pharma_management",
        "type": "warning",
        "title": "Medication Refill Reminder",
        "message": f"Your {medication_name} will run out in {days_remaining} days. Please refill soon.",
        "user_id": patient_id,
        "created_at": datetime.now().isoformat(),
        "data": {"medication_name": medication_name, "days_remaining": days_remaining}
    }
    return await send_notification(notification)

# Example: Medication interaction warning notification
async def send_interaction_warning_notification(patient_id, medication1, medication2, severity):
    notification = {
        "id": str(uuid.uuid4()),
        "service": "pharma_management",
        "type": "error",
        "title": "Medication Interaction Warning",
        "message": f"Potential {severity} interaction detected between {medication1} and {medication2}",
        "user_id": patient_id,
        "created_at": datetime.now().isoformat(),
        "data": {"medication1": medication1, "medication2": medication2, "severity": severity}
    }
    return await send_notification(notification)