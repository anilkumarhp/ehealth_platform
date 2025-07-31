# app/api/deps.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID

from app.integrations.grpc.user_client import user_service_client
from app.core.security import TokenPayload

# Configure OAuth2 scheme for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v1/auth/token",
    description="Enter your Bearer token from the user management service"
)

def get_current_user(token: str = Depends(oauth2_scheme)) -> TokenPayload:
    """
    Validates a token via gRPC and returns the rich user payload.
    Works with Swagger UI Bearer token authentication.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Call gRPC service to validate token
        grpc_response = user_service_client.validate_token(token)
        
        if not grpc_response:
            raise credentials_exception

        # Map all fields from the gRPC response to our Pydantic model
        return TokenPayload(
            sub=UUID(grpc_response.user_id),
            full_name=grpc_response.full_name,
            date_of_birth=grpc_response.date_of_birth,
            gender=grpc_response.gender,
            primary_mobile_number=grpc_response.primary_mobile_number,
            email=grpc_response.email,
            roles=list(grpc_response.roles),
            org_id=UUID(grpc_response.org_id) if grpc_response.org_id else None,
            national_health_id=grpc_response.national_health_id or None,
            address=grpc_response.address or None
        )
    except Exception as e:
        # Log error for debugging
        print(f"gRPC Authentication error: {e}")
        raise credentials_exception