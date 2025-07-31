import boto3
import os
import base64
import io
from botocore.exceptions import ClientError
from fastapi import HTTPException
import uuid
from app.core.config import settings
from app.utils.file_compressor import file_compressor

class S3Client:
    def __init__(self):
        """Initialize S3 client with credentials from environment variables"""
        # Check if AWS credentials are properly configured
        aws_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
        aws_secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
        
        if not aws_access_key or aws_access_key == 'dummy-key':
            print("WARNING: AWS_ACCESS_KEY_ID not configured or using dummy value")
            self.s3_enabled = False
            return
            
        if not aws_secret_key or aws_secret_key == 'dummy-secret':
            print("WARNING: AWS_SECRET_ACCESS_KEY not configured or using dummy value")
            self.s3_enabled = False
            return
            
        self.s3_client = boto3.client(
            's3',
            aws_access_key_id=aws_access_key,
            aws_secret_access_key=aws_secret_key,
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
        )
        self.bucket_name = os.environ.get('AWS_S3_BUCKET_NAME', 'ehealth-platform-files')
        self.s3_enabled = True
        
        print(f"S3 Client initialized with bucket: {self.bucket_name}")
        print(f"AWS Region: {os.environ.get('AWS_REGION', 'us-east-1')}")
        print(f"Using Access Key: {aws_access_key[:8]}...{aws_access_key[-4:]}")
        print(f"Secret Key configured: {'Yes' if aws_secret_key else 'No'}")
        
        # Validate credentials and bucket access
        self._validate_aws_setup()
    
    def create_user_bucket(self, user_id, user_name):
        """Create a user folder in the main bucket"""
        if not self.s3_enabled:
            raise HTTPException(
                status_code=500,
                detail="S3 storage not properly configured"
            )
            
        # Sanitize user name for folder usage (lowercase, no spaces, etc.)
        sanitized_name = user_name.lower().replace(' ', '-')
        
        # Create user folder
        return self._create_user_folder(user_id, sanitized_name)
    
    def _validate_aws_setup(self):
        """Validate AWS credentials and bucket access"""
        if not self.s3_enabled:
            return False
            
        try:
            # Test AWS credentials by listing buckets
            response = self.s3_client.list_buckets()
            print(f"AWS credentials valid. Found {len(response['Buckets'])} buckets in your account")
            
            # Show account owner info
            print(f"AWS Account Owner: {response.get('Owner', {}).get('DisplayName', 'Unknown')}")
            print(f"AWS Account ID: {response.get('Owner', {}).get('ID', 'Unknown')[:12]}...")
            
            # List all buckets with regions
            print("All buckets in your account:")
            for bucket in response['Buckets']:
                try:
                    bucket_region = self.s3_client.get_bucket_location(Bucket=bucket['Name'])['LocationConstraint']
                    if bucket_region is None:
                        bucket_region = 'us-east-1'
                    print(f"  - {bucket['Name']} (region: {bucket_region})")
                except:
                    print(f"  - {bucket['Name']} (region: unknown)")
            
            # Check if our bucket exists in the user's account
            bucket_exists = any(bucket['Name'] == self.bucket_name for bucket in response['Buckets'])
            
            if bucket_exists:
                print(f"✓ Bucket '{self.bucket_name}' found in your AWS account")
                return True
            else:
                print(f"✗ Bucket '{self.bucket_name}' NOT found in your AWS account")
                return self._create_bucket_in_account()
                
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'InvalidAccessKeyId':
                print("ERROR: Invalid AWS Access Key ID")
            elif error_code == 'SignatureDoesNotMatch':
                print("ERROR: Invalid AWS Secret Access Key")
            elif error_code == 'AccessDenied':
                print("ERROR: AWS credentials don't have permission to list buckets")
            else:
                print(f"ERROR: AWS error - {error_code}: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            print(f"ERROR: Unexpected error validating AWS setup: {str(e)}")
            return False
    
    def _create_bucket_in_account(self):
        """Create bucket in the user's AWS account"""
        try:
            region = os.environ.get('AWS_REGION', 'us-east-1')
            
            if region == 'us-east-1':
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            else:
                self.s3_client.create_bucket(
                    Bucket=self.bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': region}
                )
            
            print(f"Successfully created bucket '{self.bucket_name}' in your AWS account")
            return True
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            if error_code == 'BucketAlreadyExists':
                print(f"ERROR: Bucket '{self.bucket_name}' already exists globally (owned by someone else)")
                print("Please choose a different bucket name in AWS_S3_BUCKET_NAME environment variable")
            elif error_code == 'BucketAlreadyOwnedByYou':
                print(f"Bucket '{self.bucket_name}' already exists in your account")
                return True
            else:
                print(f"ERROR: Failed to create bucket - {error_code}: {e.response['Error']['Message']}")
            return False
        except Exception as e:
            print(f"ERROR: Unexpected error creating bucket: {str(e)}")
            return False
    
    def _create_user_folder(self, user_id, sanitized_name):
        """Create a user folder in the main bucket"""
        user_folder = f"users/{sanitized_name}_{user_id}/"
        try:
            # Create an empty object to represent the folder
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=user_folder
            )
            return f"{self.bucket_name}/{user_folder}"
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create user storage: {str(e)}"
            )
    
    def upload_file(self, file_path, user_bucket, file_type, original_filename=None):
        """Upload a file to S3 and return the URL"""
        try:
            # Generate a unique filename
            filename = original_filename or os.path.basename(file_path)
            
            # Extract user folder path from user_bucket
            user_folder = ""
            if "/" in user_bucket:
                _, user_folder = user_bucket.split("/", 1)
            
            # Create file key with user folder path
            file_key = f"{user_folder}{file_type}/{uuid.uuid4()}-{filename}"
            
            # Upload the file to the main bucket
            with open(file_path, 'rb') as file_data:
                self.s3_client.upload_fileobj(
                    file_data, 
                    self.bucket_name, 
                    file_key
                )
            
            # Generate the URL
            url = f"https://{self.bucket_name}.s3.amazonaws.com/{file_key}"
            return url
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file to S3: {str(e)}"
            )
    
    def upload_file_object(self, file_object, user_bucket, file_type, filename):
        """Upload a file object to S3 and return the URL"""
        try:
            # Compress file based on type
            print(f"Compressing file: {filename}")
            file_object = file_compressor.compress_file_by_type(file_object, filename)
            
            # Extract user folder path from user_bucket
            user_folder = ""
            if "/" in user_bucket:
                _, user_folder = user_bucket.split("/", 1)
            
            # Generate a unique filename
            file_key = f"{user_folder}{file_type}/{uuid.uuid4()}-{filename}"
            
            # Upload the file to the main bucket
            self.s3_client.upload_fileobj(
                file_object, 
                self.bucket_name, 
                file_key
            )
            
            # Generate public URL for images
            url = f"/files/public/{file_key}"
            return url
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload file to S3: {str(e)}"
            )
            
    def upload_base64_image(self, base64_data, user_bucket, file_type="profile_photo", extension="jpg"):
        """Upload a base64 encoded image to S3 and return the S3 key"""
        try:
            print(f"Starting S3 upload - bucket: {self.bucket_name}")
            print(f"User bucket: {user_bucket}")
            print(f"File type: {file_type}")
            
            # Compress image before upload
            print("Compressing image...")
            compressed_base64 = file_compressor.compress_image(
                base64_data, 
                max_size_kb=500  # 500KB max
            )
            
            # Remove data URL prefix if present
            if "," in compressed_base64:
                compressed_base64 = compressed_base64.split(",", 1)[1]
                
            # Decode compressed base64 data
            image_data = base64.b64decode(compressed_base64)
            file_object = io.BytesIO(image_data)
            print(f"Compressed image size: {len(image_data)} bytes")
            
            # Extract user folder path from user_bucket
            user_folder = ""
            if "/" in user_bucket:
                _, user_folder = user_bucket.split("/", 1)
            
            # Generate a unique filename
            filename = f"{uuid.uuid4()}.{extension}"
            file_key = f"{user_folder}{file_type}/{filename}"
            print(f"Generated file key: {file_key}")
            
            # Upload the file to the main bucket
            print(f"Uploading to S3 bucket: {self.bucket_name}")
            self.s3_client.upload_fileobj(
                file_object, 
                self.bucket_name, 
                file_key,
                ExtraArgs={'ContentType': f'image/{extension}'}
            )
            print(f"Successfully uploaded to S3: {file_key}")
            
            # Verify the file exists
            try:
                self.s3_client.head_object(Bucket=self.bucket_name, Key=file_key)
                print(f"Verified file exists in S3: {file_key}")
            except Exception as verify_error:
                print(f"WARNING: Could not verify file in S3: {verify_error}")
            
            # Return S3 key for presigned URL generation
            return file_key
        except Exception as e:
            print(f"ERROR in upload_base64_image: {str(e)}")
            print(f"Error type: {type(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload base64 image to S3: {str(e)}"
            )
    
    def generate_presigned_url(self, file_key, expiration=3600):
        """Generate a presigned URL for secure file access"""
        try:
            print(f"Generating presigned URL for: {file_key}")
            response = self.s3_client.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket_name, 'Key': file_key},
                ExpiresIn=expiration
            )
            print(f"Generated presigned URL: {response[:50]}...")
            return response
        except Exception as e:
            print(f"ERROR generating presigned URL: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to generate presigned URL: {str(e)}"
            )

# Create a singleton instance
s3_client = S3Client()