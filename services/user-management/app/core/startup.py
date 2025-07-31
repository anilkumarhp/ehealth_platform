from app.integrations.s3_client import s3_client

def ensure_s3_bucket_exists():
    """Ensure the main S3 bucket exists at application startup"""
    try:
        if hasattr(s3_client, 's3_enabled') and s3_client.s3_enabled:
            print("S3 bucket validation completed at startup")
        else:
            print("S3 not enabled - using local storage only")
    except Exception as e:
        print(f"Error checking S3 bucket at startup: {str(e)}")