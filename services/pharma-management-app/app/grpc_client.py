import grpc
import uuid
from datetime import datetime
from google.protobuf.timestamp_pb2 import Timestamp

# Import generated protobuf code
# Note: You'll need to generate these files from the proto definition
from app.protos.notification_pb2 import (
    NotificationRequest, NotificationType, ServiceType
)
from app.protos.notification_pb2_grpc import NotificationServiceStub

class NotificationClient:
    def __init__(self):
        self.channel = grpc.insecure_channel('notification-api:50051')
        self.stub = NotificationServiceStub(self.channel)
    
    def send_notification(self, notification_data):
        """Send a notification using gRPC"""
        # Create timestamp
        created_at = Timestamp()
        created_at.FromDatetime(datetime.now())
        
        # Create request
        request = NotificationRequest(
            id=str(uuid.uuid4()),
            service=ServiceType.PHARMA_MANAGEMENT,
            type=self._get_notification_type(notification_data.get('type', 'info')),
            title=notification_data.get('title', ''),
            message=notification_data.get('message', ''),
            user_id=notification_data.get('user_id', ''),
            created_at=created_at
        )
        
        # Add expires_at if present
        if notification_data.get('expires_at'):
            expires_at = Timestamp()
            expires_at.FromDatetime(notification_data.get('expires_at'))
            request.expires_at.CopyFrom(expires_at)
        
        # Add data if present
        if notification_data.get('data'):
            for k, v in notification_data.get('data').items():
                request.data[k] = str(v)
        
        # Send request
        response = self.stub.SendNotification(request)
        return {
            'notification_id': response.notification_id,
            'success': response.success,
            'error_message': response.error_message
        }
    
    def _get_notification_type(self, type_str):
        """Convert string type to enum value"""
        type_map = {
            'info': NotificationType.INFO,
            'success': NotificationType.SUCCESS,
            'warning': NotificationType.WARNING,
            'error': NotificationType.ERROR
        }
        return type_map.get(type_str.lower(), NotificationType.INFO)

# Example usage
async def send_prescription_ready_notification(patient_id, medication_name, pharmacy_name):
    client = NotificationClient()
    notification = {
        'type': 'success',
        'title': 'Prescription Ready',
        'message': f'Your prescription for {medication_name} is ready for pickup at {pharmacy_name}',
        'user_id': patient_id,
        'data': {
            'medication_name': medication_name,
            'pharmacy_name': pharmacy_name
        }
    }
    return client.send_notification(notification)

async def send_refill_reminder_notification(patient_id, medication_name, days_remaining):
    client = NotificationClient()
    notification = {
        'type': 'warning',
        'title': 'Medication Refill Reminder',
        'message': f'Your {medication_name} will run out in {days_remaining} days. Please refill soon.',
        'user_id': patient_id,
        'data': {
            'medication_name': medication_name,
            'days_remaining': str(days_remaining)
        }
    }
    return client.send_notification(notification)