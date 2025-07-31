from celery import current_task
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from uuid import UUID
import asyncio

from app.tasks.celery_app import celery_app
from app.db.session import get_async_session
from app.models.appointment import Appointment, AppointmentStatusEnum
from app.models.test_order import TestOrder, TestOrderStatusEnum

@celery_app.task(bind=True)
def send_appointment_reminder(self, appointment_id: str, reminder_type: str = "24h"):
    """Send appointment reminder notification."""
    try:
        # This would integrate with notification service
        # For now, just log the reminder
        print(f"Sending {reminder_type} reminder for appointment {appointment_id}")
        
        # Update task progress
        current_task.update_state(
            state="PROGRESS",
            meta={"current": 50, "total": 100, "status": "Sending reminder..."}
        )
        
        # Simulate notification sending
        import time
        time.sleep(2)
        
        return {
            "status": "completed",
            "appointment_id": appointment_id,
            "reminder_type": reminder_type,
            "sent_at": datetime.utcnow().isoformat()
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60, max_retries=3)

@celery_app.task(bind=True)
def process_appointment_completion(self, appointment_id: str):
    """Process appointment completion tasks."""
    try:
        async def _process():
            async with get_async_session() as db:
                # Get appointment
                result = await db.execute(
                    select(Appointment).where(Appointment.id == UUID(appointment_id))
                )
                appointment = result.scalar_one_or_none()
                
                if not appointment:
                    return {"error": "Appointment not found"}
                
                # Update related test order status
                if appointment.test_order_id:
                    test_order_result = await db.execute(
                        select(TestOrder).where(TestOrder.id == appointment.test_order_id)
                    )
                    test_order = test_order_result.scalar_one_or_none()
                    
                    if test_order:
                        test_order.status = TestOrderStatusEnum.COMPLETED
                        await db.commit()
                
                return {"status": "completed", "appointment_id": appointment_id}
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_process())
        loop.close()
        
        return result
        
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60, max_retries=3)

@celery_app.task
def cleanup_expired_appointments():
    """Clean up expired appointments that were never confirmed."""
    try:
        async def _cleanup():
            async with get_async_session() as db:
                # Find appointments older than 24 hours that are still scheduled
                cutoff_time = datetime.utcnow() - timedelta(hours=24)
                
                result = await db.execute(
                    select(Appointment).where(
                        and_(
                            Appointment.appointment_datetime < cutoff_time,
                            Appointment.status == AppointmentStatusEnum.SCHEDULED
                        )
                    )
                )
                expired_appointments = result.scalars().all()
                
                count = 0
                for appointment in expired_appointments:
                    appointment.status = AppointmentStatusEnum.CANCELLED
                    count += 1
                
                await db.commit()
                return {"cleaned_up": count}
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(_cleanup())
        loop.close()
        
        return result
        
    except Exception as exc:
        print(f"Cleanup task failed: {exc}")
        return {"error": str(exc)}

# Periodic task scheduling
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "cleanup-expired-appointments": {
        "task": "app.tasks.appointment_tasks.cleanup_expired_appointments",
        "schedule": crontab(hour=2, minute=0),  # Run daily at 2 AM
    },
}