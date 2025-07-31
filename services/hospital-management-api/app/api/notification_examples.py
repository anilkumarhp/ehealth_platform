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

# Example: Appointment confirmation notification
async def send_appointment_confirmation(patient_id, doctor_name, specialty, appointment_date, hospital_name):
    notification = {
        "id": str(uuid.uuid4()),
        "service": "hospital_management",
        "type": "success",
        "title": "Appointment Confirmed",
        "message": f"Your appointment with {doctor_name} ({specialty}) is confirmed for {appointment_date} at {hospital_name}",
        "user_id": patient_id,
        "created_at": datetime.now().isoformat(),
        "data": {
            "doctor_name": doctor_name,
            "specialty": specialty,
            "appointment_date": appointment_date,
            "hospital_name": hospital_name
        }
    }
    return await send_notification(notification)

# Example: Appointment reminder notification
async def send_appointment_reminder(patient_id, doctor_name, appointment_date, hospital_name):
    notification = {
        "id": str(uuid.uuid4()),
        "service": "hospital_management",
        "type": "info",
        "title": "Appointment Reminder",
        "message": f"Reminder: Your appointment with {doctor_name} is tomorrow at {hospital_name}",
        "user_id": patient_id,
        "created_at": datetime.now().isoformat(),
        "data": {
            "doctor_name": doctor_name,
            "appointment_date": appointment_date,
            "hospital_name": hospital_name
        }
    }
    return await send_notification(notification)

# Example: Doctor availability notification
async def send_doctor_availability_notification(patient_id, doctor_name, specialty, available_date):
    notification = {
        "id": str(uuid.uuid4()),
        "service": "hospital_management",
        "type": "info",
        "title": "Doctor Availability",
        "message": f"Dr. {doctor_name} ({specialty}) now has availability on {available_date}",
        "user_id": patient_id,
        "created_at": datetime.now().isoformat(),
        "data": {
            "doctor_name": doctor_name,
            "specialty": specialty,
            "available_date": available_date
        }
    }
    return await send_notification(notification)