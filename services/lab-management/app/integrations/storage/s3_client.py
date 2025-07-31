# app/integrations/storage/s3_client.py

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile
from uuid import uuid4

from app.core.config import settings

class S3Client:
    """
    A client for interacting with an S3-compatible storage service.
    """
    def __init__(self):
        self.s3 = boto3.client(
            "s3",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        self.bucket_name = settings.S3_BUCKET_NAME

    def upload_file(self, file: UploadFile, folder: str = "reports") -> str:
        """
        Uploads a file to S3 and returns the storage key.
        """
        file_extension = file.filename.split(".")[-1]
        storage_key = f"{folder}/{uuid4()}.{file_extension}"

        try:
            self.s3.upload_fileobj(file.file, self.bucket_name, storage_key)
        except ClientError as e:
            # In a real app, you'd have more robust error logging here
            print(f"Failed to upload file to S3: {e}")
            return None
        return storage_key

    def generate_presigned_url(self, storage_key: str, expiration: int = 3600) -> str:
        """
        Generates a temporary, secure URL to download a private file from S3.
        """
        try:
            response = self.s3.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": storage_key},
                ExpiresIn=expiration,
            )
        except ClientError as e:
            print(f"Failed to generate presigned URL: {e}")
            return None
        return response

# Instantiate the client for use in the application
s3_client = S3Client()