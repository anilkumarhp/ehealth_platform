import grpc
import asyncio
from concurrent import futures
from google.protobuf.timestamp_pb2 import Timestamp
import time
import uuid
from datetime import datetime

# Import generated protobuf code
from app.protos.notification_pb2 import (
    NotificationResponse, UserNotificationsResponse, MarkAsReadResponse,
    Notification as NotificationMessage
)
from app.protos.notification_pb2_grpc import (
    NotificationServiceServicer, add_NotificationServiceServicer_to_server
)

# Import Redis service
from app.services.notification_service import NotificationService
from app.models.notification import Notification, NotificationType, NotificationService as ServiceEnum

class NotificationServicer(NotificationServiceServicer):
    def __init__(self):
        self.notification_service = NotificationService()
    
    async def SendNotification(self, request, context):
        try:
            # Convert gRPC request to our model
            notification = Notification(
                id=request.id or str(uuid.uuid4()),
                service=ServiceEnum(request.service.name.lower()),
                type=NotificationType(request.type.name.lower()),
                title=request.title,
                message=request.message,
                user_id=request.user_id,
                created_at=datetime.fromtimestamp(request.created_at.seconds + request.created_at.nanos / 1e9),
                expires_at=datetime.fromtimestamp(request.expires_at.seconds + request.expires_at.nanos / 1e9) if request.HasField('expires_at') else None,
                data={k: v for k, v in request.data.items()},
                read=False
            )
            
            # Publish notification
            await self.notification_service.publish_notification(notification)
            
            return NotificationResponse(
                notification_id=notification.id,
                success=True,
                error_message=""
            )
        except Exception as e:
            return NotificationResponse(
                notification_id="",
                success=False,
                error_message=str(e)
            )
    
    async def GetUserNotifications(self, request, context):
        try:
            # Get notifications from Redis
            notifications = await self.notification_service.get_user_notifications(request.user_id)
            
            # Filter if needed
            if not request.include_read:
                notifications = [n for n in notifications if not n.get('read', False)]
            
            # Apply pagination
            if request.limit > 0:
                start = request.offset
                end = start + request.limit
                notifications = notifications[start:end]
            
            # Convert to gRPC messages
            notification_messages = []
            for n in notifications:
                created_at = Timestamp()
                created_at.FromDatetime(datetime.fromisoformat(n['created_at']))
                
                notification_msg = NotificationMessage(
                    id=n['id'],
                    service=n['service'],
                    type=n['type'],
                    title=n['title'],
                    message=n['message'],
                    user_id=n['user_id'],
                    created_at=created_at,
                    read=n.get('read', False)
                )
                
                # Add expires_at if present
                if n.get('expires_at'):
                    expires_at = Timestamp()
                    expires_at.FromDatetime(datetime.fromisoformat(n['expires_at']))
                    notification_msg.expires_at.CopyFrom(expires_at)
                
                # Add data if present
                if n.get('data'):
                    for k, v in n['data'].items():
                        notification_msg.data[k] = str(v)
                
                notification_messages.append(notification_msg)
            
            # Count unread
            unread_count = sum(1 for n in notifications if not n.get('read', False))
            
            return UserNotificationsResponse(
                notifications=notification_messages,
                total_count=len(notifications),
                unread_count=unread_count
            )
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return UserNotificationsResponse()
    
    async def MarkNotificationAsRead(self, request, context):
        try:
            success = await self.notification_service.mark_as_read(
                request.user_id, request.notification_id
            )
            return MarkAsReadResponse(
                success=success,
                error_message="" if success else "Notification not found"
            )
        except Exception as e:
            return MarkAsReadResponse(
                success=False,
                error_message=str(e)
            )

async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    add_NotificationServiceServicer_to_server(NotificationServicer(), server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    print("gRPC server started on port 50051")
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())