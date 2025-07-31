import json
import redis
import os
import logging
from app.models.notification import Notification
from datetime import datetime
import uuid

# Import Redis async client based on availability
try:
    import aioredis
except ImportError:
    from redis import asyncio as aioredis

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
        self.redis = redis.Redis.from_url(self.redis_url)
        self.async_redis = None
        logger.info(f"NotificationService initialized with Redis URL: {self.redis_url}")
    
    async def get_async_redis(self):
        if self.async_redis is None:
            try:
                self.async_redis = await aioredis.from_url(self.redis_url)
                logger.info("Async Redis connection established")
            except Exception as e:
                logger.error(f"Failed to connect to Redis: {str(e)}")
                raise
        return self.async_redis
    
    async def publish_notification(self, notification: Notification):
        """Publish notification to appropriate channels"""
        try:
            # Convert notification to JSON
            notification_json = notification.json()
            
            # Publish to service-specific channel
            self.redis.publish(f"notifications:{notification.service}", notification_json)
            logger.debug(f"Published to service channel: notifications:{notification.service}")
            
            # Publish to user-specific channel if user_id is provided
            if notification.user_id:
                self.redis.publish(f"notifications:user:{notification.user_id}", notification_json)
                logger.debug(f"Published to user channel: notifications:user:{notification.user_id}")
                
                # Store notification in Redis for retrieval
                notification_id = f"{notification.service}:{notification.id}"
                key = f"user:{notification.user_id}:notifications"
                self.redis.hset(key, notification_id, notification_json)
                logger.debug(f"Stored notification in Redis: {key} -> {notification_id}")
                
                # Set expiration if needed
                if notification.expires_at:
                    expiry_timestamp = int(notification.expires_at.timestamp())
                    expiry_key = f"user:{notification.user_id}:notifications:{notification_id}"
                    self.redis.expireat(expiry_key, expiry_timestamp)
                    logger.debug(f"Set expiration for {expiry_key} at {notification.expires_at}")
            else:
                logger.warning(f"Notification {notification.id} has no user_id, skipping user-specific storage")
                
            return True
        except Exception as e:
            logger.error(f"Error publishing notification: {str(e)}")
            raise
    
    async def get_user_notifications(self, user_id: str):
        """Get all notifications for a user"""
        try:
            redis_client = await self.get_async_redis()
            key = f"user:{user_id}:notifications"
            notifications = await redis_client.hgetall(key)
            logger.debug(f"Retrieved {len(notifications)} notifications for user {user_id}")
            
            result = []
            for notif in notifications.values():
                try:
                    result.append(json.loads(notif))
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode notification: {str(e)}")
            
            return result
        except Exception as e:
            logger.error(f"Error getting user notifications: {str(e)}")
            raise
    
    async def mark_as_read(self, user_id: str, notification_id: str):
        """Mark a notification as read"""
        try:
            redis_client = await self.get_async_redis()
            notification_key = f"user:{user_id}:notifications"
            
            # Get the notification
            notification_json = await redis_client.hget(notification_key, notification_id)
            if not notification_json:
                logger.warning(f"Notification {notification_id} not found for user {user_id}")
                return False
            
            try:
                # Update the notification
                notification = json.loads(notification_json)
                notification["read"] = True
                
                # Save it back
                await redis_client.hset(notification_key, notification_id, json.dumps(notification))
                logger.debug(f"Marked notification {notification_id} as read for user {user_id}")
                return True
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode notification {notification_id}: {str(e)}")
                return False
        except Exception as e:
            logger.error(f"Error marking notification as read: {str(e)}")
            raise