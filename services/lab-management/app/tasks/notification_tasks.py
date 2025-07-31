from celery import current_task
from datetime import datetime
from typing import Dict, Any
import httpx

from app.tasks.celery_app import celery_app
from app.core.config import settings

@celery_app.task(bind=True)
def send_notification_to_service(
    self, 
    notification_type: str,
    recipient_id: str,
    message: str,
    metadata: Dict[str, Any] = None
):
    """Send notification to notification microservice."""
    try:
        # Prepare notification payload
        payload = {
            "type": notification_type,
            "recipient_id": recipient_id,
            "message": message,
            "service": "lab-management",
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        # Update task progress
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 25, "total": 100, "status": "Preparing notification..."}
        )
        
        # Send to notification service (when available)
        # For now, simulate the call
        notification_service_url = getattr(settings, 'NOTIFICATION_SERVICE_URL', None)
        
        if notification_service_url:
            with httpx.Client() as client:
                response = client.post(
                    f"{notification_service_url}/api/v1/notifications/send",
                    json=payload,
                    timeout=30
                )
                response.raise_for_status()
                result = response.json()
        else:
            # Fallback: log notification
            print(f"NOTIFICATION: {notification_type} to {recipient_id}: {message}")
            result = {
                "status": "logged",
                "notification_id": f"log_{datetime.utcnow().timestamp()}"
            }
        
        current_task.update_state(
            state="SUCCESS",
            meta={"current": 100, "total": 100, "status": "Notification sent"}
        )
        
        return result
        
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60, max_retries=3)

@celery_app.task
def send_appointment_confirmation(appointment_id: str, patient_id: str):
    """Send appointment confirmation notification."""
    return send_notification_to_service.delay(
        notification_type="appointment_confirmation",
        recipient_id=patient_id,
        message=f"Your appointment has been confirmed. ID: {appointment_id}",
        metadata={"appointment_id": appointment_id}
    )

@celery_app.task
def send_test_results_ready(test_order_id: str, patient_id: str):
    """Send test results ready notification."""
    return send_notification_to_service.delay(
        notification_type="test_results_ready",
        recipient_id=patient_id,
        message="Your test results are ready for review.",
        metadata={"test_order_id": test_order_id}
    )

@celery_app.task
def send_appointment_reminder(appointment_id: str, patient_id: str, reminder_time: str):
    """Send appointment reminder notification."""
    return send_notification_to_service.delay(
        notification_type="appointment_reminder",
        recipient_id=patient_id,
        message=f"Reminder: You have an appointment in {reminder_time}.",
        metadata={"appointment_id": appointment_id, "reminder_time": reminder_time}
    )