from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as notification_router
import socketio
import redis
import json
import asyncio
import threading
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)
from app.grpc_server import serve as serve_grpc

app = FastAPI(title="Notification Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Socket.IO setup
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins=['http://localhost:3000'])
socket_app = socketio.ASGIApp(sio)

# Redis client for pub/sub
redis_url = os.getenv("REDIS_URL", "redis://redis:6379/0")
try:
    redis_client = redis.Redis.from_url(redis_url)
    pubsub = redis_client.pubsub()
    print(f"Connected to Redis at {redis_url}")
except Exception as e:
    print(f"Failed to connect to Redis: {str(e)}")
    raise

# Include routers
app.include_router(notification_router, prefix="/api/v1")

# Mount Socket.IO
app.mount("/ws", socket_app)

# Socket.IO events
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")

@sio.event
async def disconnect(sid):
    print(f"Client disconnected: {sid}")

@sio.event
async def subscribe(sid, data):
    user_id = data.get('userId')
    if user_id:
        sio.enter_room(sid, f"user:{user_id}")
        print(f"User {user_id} subscribed to notifications")

# Background task to listen for Redis messages and forward to Socket.IO
async def redis_listener():
    try:
        pubsub = redis_client.pubsub()
        pubsub.psubscribe('notifications:*')
        logger.info("Redis listener started, subscribed to notifications:*")
        
        for message in pubsub.listen():
            try:
                if message['type'] == 'pmessage':
                    channel = message['channel'].decode('utf-8')
                    data = json.loads(message['data'].decode('utf-8'))
                    logger.debug(f"Received message on channel {channel}")
                    
                    # If it's a user-specific notification
                    if channel.startswith('notifications:user:'):
                        user_id = channel.split(':')[-1]
                        await sio.emit('notification', data, room=f"user:{user_id}")
                        logger.debug(f"Emitted notification to user {user_id}")
                    
                    # If it's a service-wide notification
                    elif channel.startswith('notifications:'):
                        await sio.emit('notification', data)
                        logger.debug(f"Emitted notification to all connected clients")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode message: {str(e)}")
            except Exception as e:
                logger.error(f"Error processing Redis message: {str(e)}")
    except Exception as e:
        logger.error(f"Redis listener error: {str(e)}")
        # Attempt to reconnect after a delay
        await asyncio.sleep(5)
        asyncio.create_task(redis_listener())

@app.on_event("startup")
async def startup_event():
    try:
        # Start Redis listener in background
        asyncio.create_task(redis_listener())
        logger.info("Redis listener task created")
        
        # Start gRPC server in a separate thread
        grpc_thread = threading.Thread(target=lambda: asyncio.run(serve_grpc()))
        grpc_thread.daemon = True
        grpc_thread.start()
        logger.info("gRPC server thread started")
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8004, reload=True)