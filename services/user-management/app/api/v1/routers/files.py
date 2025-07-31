from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends, Header
from jose import jwt, JWTError
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
import uuid
import os
import shutil
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel
import boto3
from botocore.exceptions import ClientError
import io

from app.integrations.s3_client import s3_client
from app.api.v1 import deps
from app.db.models.user import User
from app.crud import crud_user

router = APIRouter()

# Simple enum for file types
class FileType(str, Enum):
    PROFILE_PHOTO = "profile_photo"
    INSURANCE_DOCUMENT = "insurance_document"
    MEDICAL_RECORD = "medical_record"
    OTHER = "other"

# Response models
class FileUploadResponse(BaseModel):
    file_id: str
    file_url: str
    file_type: str
    content_type: str
    size: int
    s3_url: Optional[str] = None

# Configure upload directory for local storage fallback
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "/app/uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=FileUploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    file_type: str = Form("other"),
    user_id: Optional[str] = Form(None),
    db: Session = Depends(deps.get_public_db),
    authorization: Optional[str] = Header(None)
):
    """
    Upload a file to S3 or local storage.
    If user_id is provided or user is authenticated, the file will be stored in a user-specific location.
    """
    try:
        # Generate unique identifiers
        file_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{file_id}_{timestamp}_{file.filename}"
        
        # First save locally as a fallback
        type_dir = os.path.join(UPLOAD_DIR, file_type)
        os.makedirs(type_dir, exist_ok=True)
        file_path = os.path.join(type_dir, filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Generate local URL
        local_url = f"/api/v1/files/{file_type}/{filename}"
        
        # Try to upload to S3
        s3_url = None
        target_user = None
        
        # Get user from JWT token or user_id parameter
        target_user = None
        print(f"File upload - user_id parameter: {user_id}")
        print(f"File upload - authorization header: {'Present' if authorization else 'None'}")
        
        # Try to get user from JWT token first
        if authorization and not user_id:
            try:
                from jose import jwt
                from app.core.config import settings
                
                scheme, token = authorization.split()
                if scheme.lower() == 'bearer':
                    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
                    email = payload.get("sub")
                    if email:
                        target_user = crud_user.get_user_by_email(db, email=email)
                        if target_user:
                            print(f"Found user from JWT token: {target_user.email}")
            except Exception as jwt_error:
                print(f"Failed to extract user from JWT: {str(jwt_error)}")
        
        # Fallback to user_id parameter
        if not target_user and user_id:
            try:
                user_uuid = uuid.UUID(user_id)
                target_user = crud_user.get_user_by_id(db, user_uuid)
                print(f"Found target user by ID: {target_user.email if target_user else 'None'}")
            except ValueError as e:
                print(f"Invalid user_id format: {e}")
        
        if not target_user:
            print("No user found for file upload - saving without user association")
        
        # If we have AWS credentials configured, upload to S3
        if os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
            try:
                # If we have a user, create/use their bucket
                if target_user:
                    user_name = f"{target_user.personal_info.get('first_name', '')}-{target_user.personal_info.get('last_name', '')}"
                    if not user_name.strip('-'):
                        user_name = target_user.email.split('@')[0]
                    
                    # Use existing bucket if available, otherwise create a new one
                    user_bucket = target_user.s3_bucket_name or s3_client.create_user_bucket(str(target_user.id), user_name)
                    
                    # Save bucket name to user if not already saved
                    if not target_user.s3_bucket_name:
                        # Update user with bucket name
                        crud_user.update_user(
                            db=db,
                            user=target_user,
                            updates={"s3_bucket_name": user_bucket}
                        )
                    
                    # Reset file pointer to beginning
                    file.file.seek(0)
                    
                    # Upload to S3
                    s3_url = s3_client.upload_file_object(
                        file.file, 
                        user_bucket, 
                        file_type, 
                        file.filename
                    )
                    
                    # If this is a profile photo, update the user's profile
                    if file_type == "profile_photo":
                        crud_user.update_user_profile_photo(
                            db=db,
                            user=target_user,
                            photo_url=s3_url,
                            s3_bucket=user_bucket
                        )
                        print(f"Updated user profile photo: {s3_url}")
                else:
                    # Use default bucket if no user
                    file.file.seek(0)
                    s3_url = s3_client.upload_file_object(
                        file.file, 
                        s3_client.bucket_name, 
                        file_type, 
                        file.filename
                    )
            except Exception as s3_error:
                # Log the error but continue with local storage
                print(f"S3 upload failed: {str(s3_error)}")
        
        return FileUploadResponse(
            file_id=file_id,
            file_url=local_url,
            file_type=file_type,
            content_type=file.content_type,
            size=os.path.getsize(file_path),
            s3_url=s3_url
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )

@router.get("/secure/{file_path:path}")
async def get_secure_file(
    file_path: str,
    current_user: User = Depends(deps.get_current_user_from_db),
    db: Session = Depends(deps.get_public_db)
):
    """Serve files securely - only to the file owner"""
    try:
        # Extract user folder from file path
        if not file_path.startswith("users/"):
            raise HTTPException(status_code=404, detail="File not found")
        
        # Check if user owns this file by checking the path contains their user ID
        user_id_str = str(current_user.id)
        if user_id_str not in file_path:
            raise HTTPException(status_code=403, detail="Access denied")
        
        # Try to get file from S3 first
        if os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
            try:
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.environ.get('AWS_REGION', 'us-east-1')
                )
                
                bucket_name = os.environ.get('AWS_S3_BUCKET_NAME', 'ehealth-platform-files')
                
                # Get file from S3
                response = s3.get_object(Bucket=bucket_name, Key=file_path)
                file_content = response['Body'].read()
                content_type = response.get('ContentType', 'application/octet-stream')
                
                return StreamingResponse(
                    io.BytesIO(file_content),
                    media_type=content_type,
                    headers={"Cache-Control": "private, max-age=3600"}
                )
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchKey':
                    raise HTTPException(status_code=500, detail="Error accessing file")
        
        # Fallback to local file if S3 fails or file not found
        local_file_path = os.path.join("/app/uploads", file_path.replace("users/", ""))
        if os.path.exists(local_file_path):
            with open(local_file_path, "rb") as f:
                file_content = f.read()
            
            # Determine content type based on file extension
            content_type = "application/octet-stream"
            if file_path.lower().endswith(('.jpg', '.jpeg')):
                content_type = "image/jpeg"
            elif file_path.lower().endswith('.png'):
                content_type = "image/png"
            elif file_path.lower().endswith('.gif'):
                content_type = "image/gif"
            
            return StreamingResponse(
                io.BytesIO(file_content),
                media_type=content_type,
                headers={"Cache-Control": "private, max-age=3600"}
            )
        
        raise HTTPException(status_code=404, detail="File not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error serving file: {str(e)}"
        )

@router.get("/public/{file_path:path}")
async def get_public_file(
    file_path: str
):
    """Serve files publicly - no authentication required"""
    try:
        # Try to get file from S3 first
        if os.environ.get('AWS_ACCESS_KEY_ID') and os.environ.get('AWS_SECRET_ACCESS_KEY'):
            try:
                s3 = boto3.client(
                    's3',
                    aws_access_key_id=os.environ.get('AWS_ACCESS_KEY_ID'),
                    aws_secret_access_key=os.environ.get('AWS_SECRET_ACCESS_KEY'),
                    region_name=os.environ.get('AWS_REGION', 'us-east-1')
                )
                
                bucket_name = os.environ.get('AWS_S3_BUCKET_NAME', 'ehealth-platform-files')
                
                # Get file from S3
                response = s3.get_object(Bucket=bucket_name, Key=file_path)
                file_content = response['Body'].read()
                content_type = response.get('ContentType', 'application/octet-stream')
                
                return StreamingResponse(
                    io.BytesIO(file_content),
                    media_type=content_type,
                    headers={"Cache-Control": "public, max-age=3600"}
                )
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchKey':
                    raise HTTPException(status_code=500, detail="Error accessing file")
        
        # Fallback to local file if S3 fails or file not found
        local_file_path = os.path.join("/app/uploads", file_path.replace("users/", ""))
        if os.path.exists(local_file_path):
            with open(local_file_path, "rb") as f:
                file_content = f.read()
            
            # Determine content type based on file extension
            content_type = "application/octet-stream"
            if file_path.lower().endswith(('.jpg', '.jpeg')):
                content_type = "image/jpeg"
            elif file_path.lower().endswith('.png'):
                content_type = "image/png"
            elif file_path.lower().endswith('.gif'):
                content_type = "image/gif"
            
            return StreamingResponse(
                io.BytesIO(file_content),
                media_type=content_type,
                headers={"Cache-Control": "public, max-age=3600"}
            )
        
        raise HTTPException(status_code=404, detail="File not found")
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error serving file: {str(e)}"
        )