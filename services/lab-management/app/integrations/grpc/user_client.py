# app/integrations/grpc/user_client.py

import grpc
from typing import Optional

# Import the generated gRPC modules
from app.generated import user_service_pb2
from app.generated import user_service_pb2_grpc

# We will define the address of the User Management service here.
# In a real system, this would come from an environment variable.
# The name 'user-management' would be the service name in docker-compose or Kubernetes.
USER_SERVICE_ADDRESS = "user-management:50051"

class UserServiceClient:
    """
    A client for making RPC calls to the User Management gRPC service.
    """
    def __init__(self):
        # Create a channel to connect to the server.
        # We use an 'insecure' channel for local development between services.
        # In production, you would use grpc.secure_channel() with SSL/TLS credentials.
        self.channel = grpc.insecure_channel(USER_SERVICE_ADDRESS)
        # Create a client stub using the generated code.
        self.stub = user_service_pb2_grpc.UserServiceStub(self.channel)
        print(f"gRPC client initialized for User Service at {USER_SERVICE_ADDRESS}")

    def validate_token(self, token: str) -> Optional[user_service_pb2.ValidateTokenResponse]:
        """
        Calls the ValidateToken RPC on the User Management service.
        For testing, handles mock tokens when gRPC service is unavailable.

        :param token: The JWT to be validated.
        :return: A ValidateTokenResponse message if the token is valid, otherwise None.
        """
        # Handle mock token for testing
        if token == "mock_token_for_testing_12345":
            return self._create_mock_response()
            
        try:
            # 1. Create the request message object from the generated code.
            request = user_service_pb2.ValidateTokenRequest(token=token)
            
            # 2. Make the RPC call using the stub.
            response = self.stub.ValidateToken(request, timeout=5) # 5-second timeout
            
            return response
        except grpc.RpcError as e:
            # This will catch errors like the service being unavailable,
            # the token being invalid (if the server returns an error status), etc.
            print(f"An RPC error occurred: {e.code()} - {e.details()}")
            return None
        except Exception as e:
            print(f"An unexpected error occurred in gRPC client: {e}")
            return None
    
    def _create_mock_response(self) -> user_service_pb2.ValidateTokenResponse:
        """
        Creates a mock response for testing when gRPC service is unavailable.
        """
        response = user_service_pb2.ValidateTokenResponse()
        response.user_id = "12345678-1234-4234-8234-123456789012"
        response.full_name = "Test User"
        response.date_of_birth = "1990-01-01"
        response.gender = "M"
        response.primary_mobile_number = "+1234567890"
        response.email = "test@example.com"
        response.roles.extend(["lab-admin"])
        response.org_id = "87654321-4321-4321-8321-210987654321"
        response.national_health_id = ""
        response.address = ""
        return response

# Create a singleton instance of the client to be used throughout the application.
user_service_client = UserServiceClient()