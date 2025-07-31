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

# Example: Lab test results ready notification
async def send_test_results_notification(patient_id, test_name, test_id):
    notification = {
        "id": str(uuid.uuid4()),
        "service": "lab_management",
        "type": "success",
        "title": "Lab Results Ready",
        "message": f"Your {test_name} results are now available",
        "user_id": patient_id,
        "created_at": datetime.now().isoformat(),
        "data": {"test_id": test_id}
    }
    return await send_notification(notification)

# Example: Lab test scheduled notification
async def send_test_scheduled_notification(patient_id, test_name, appointment_date, lab_name):
    notification = {
        "id": str(uuid.uuid4()),
        "service": "lab_management",
        "type": "info",
        "title": "Lab Test Scheduled",
        "message": f"Your {test_name} is scheduled for {appointment_date} at {lab_name}",
        "user_id": patient_id,
        "created_at": datetime.now().isoformat(),
        "data": {"test_name": test_name, "appointment_date": appointment_date, "lab_name": lab_name}
    }
    return await send_notification(notification)

# Example: Lab test reminder notification
async def send_test_reminder_notification(patient_id, test_name, appointment_date, lab_name):
    notification = {
        "id": str(uuid.uuid4()),
        "service": "lab_management",
        "type": "warning",
        "title": "Lab Test Reminder",
        "message": f"Reminder: Your {test_name} is scheduled for tomorrow at {lab_name}",
        "user_id": patient_id,
        "created_at": datetime.now().isoformat(),
        "data": {"test_name": test_name, "appointment_date": appointment_date, "lab_name": lab_name}
    }
    return await send_notification(notification)