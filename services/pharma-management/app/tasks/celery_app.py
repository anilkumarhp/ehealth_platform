"""
Celery application configuration
"""

from celery import Celery
from app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "pharma_management",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.tasks.prescription_tasks",
        "app.tasks.notification_tasks",
        "app.tasks.inventory_tasks",
        "app.tasks.compliance_tasks"
    ]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Beat schedule for periodic tasks
celery_app.conf.beat_schedule = {
    "check-expired-prescriptions": {
        "task": "app.tasks.prescription_tasks.check_expired_prescriptions",
        "schedule": 3600.0,  # Every hour
    },
    "check-expiring-medicines": {
        "task": "app.tasks.inventory_tasks.check_expiring_medicines",
        "schedule": 86400.0,  # Daily
    },
    "send-order-reminders": {
        "task": "app.tasks.notification_tasks.send_order_reminders",
        "schedule": 1800.0,  # Every 30 minutes
    },
    "cleanup-old-audit-logs": {
        "task": "app.tasks.compliance_tasks.cleanup_old_audit_logs",
        "schedule": 604800.0,  # Weekly
    },
}