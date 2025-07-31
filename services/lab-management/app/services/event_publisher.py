from typing import Dict, Any
from uuid import UUID
import json
from datetime import datetime


class EventPublisher:
    """Service for publishing events to other microservices."""

    async def publish_test_order_created(self, order_data: Dict[str, Any]) -> None:
        """Publish test order created event."""
        event = {
            "event_type": "test_order_created",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "order_id": str(order_data.get("id")),
                "patient_id": str(order_data.get("patient_user_id")),
                "lab_service_id": str(order_data.get("lab_service_id")),
                "status": order_data.get("status"),
                "requesting_entity_id": str(order_data.get("requesting_entity_id"))
            }
        }
        
        # TODO: Implement actual message queue publishing
        # await self._publish_to_queue("test_orders", event)
        print(f"Event published: {json.dumps(event, indent=2)}")

    async def publish_consent_approved(self, consent_data: Dict[str, Any]) -> None:
        """Publish consent approved event."""
        event = {
            "event_type": "consent_approved",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "order_id": str(consent_data.get("order_id")),
                "patient_id": str(consent_data.get("patient_id")),
                "approved_at": datetime.utcnow().isoformat()
            }
        }
        
        # TODO: Implement actual message queue publishing
        print(f"Event published: {json.dumps(event, indent=2)}")

    async def publish_appointment_scheduled(self, appointment_data: Dict[str, Any]) -> None:
        """Publish appointment scheduled event."""
        event = {
            "event_type": "appointment_scheduled",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "appointment_id": str(appointment_data.get("id")),
                "patient_id": str(appointment_data.get("patient_user_id")),
                "appointment_datetime": appointment_data.get("appointment_datetime"),
                "lab_id": str(appointment_data.get("lab_id"))
            }
        }
        
        print(f"Event published: {json.dumps(event, indent=2)}")

    async def publish_test_completed(self, test_data: Dict[str, Any]) -> None:
        """Publish test completed event."""
        event = {
            "event_type": "test_completed",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "appointment_id": str(test_data.get("appointment_id")),
                "patient_id": str(test_data.get("patient_id")),
                "test_order_id": str(test_data.get("test_order_id")),
                "completed_at": datetime.utcnow().isoformat()
            }
        }
        
        print(f"Event published: {json.dumps(event, indent=2)}")

    async def publish_payment_required(self, payment_data: Dict[str, Any]) -> None:
        """Publish payment required event."""
        event = {
            "event_type": "payment_required",
            "timestamp": datetime.utcnow().isoformat(),
            "data": {
                "appointment_id": str(payment_data.get("appointment_id")),
                "patient_id": str(payment_data.get("patient_id")),
                "amount": payment_data.get("amount"),
                "currency": payment_data.get("currency", "USD")
            }
        }
        
        print(f"Event published: {json.dumps(event, indent=2)}")


# Singleton instance
event_publisher = EventPublisher()