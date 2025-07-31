from fastapi import HTTPException, status
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

class BaseLabException(Exception):
    """Base exception for lab management service."""
    
    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(BaseLabException):
    """Validation error exception."""
    
    def __init__(self, message: str, field: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            details=details or {}
        )
        if field:
            self.details["field"] = field

class NotFoundError(BaseLabException):
    """Resource not found exception."""
    
    def __init__(self, resource: str, identifier: str = None):
        message = f"{resource} not found"
        if identifier:
            message += f" with identifier: {identifier}"
        
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            details={"resource": resource, "identifier": identifier}
        )

class ConflictError(BaseLabException):
    """Resource conflict exception."""
    
    def __init__(self, message: str, resource: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_409_CONFLICT,
            details=details or {}
        )
        if resource:
            self.details["resource"] = resource

class AuthorizationError(BaseLabException):
    """Authorization error exception."""
    
    def __init__(self, message: str = "Insufficient permissions", action: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            details={"action": action} if action else {}
        )

class BusinessLogicError(BaseLabException):
    """Business logic violation exception."""
    
    def __init__(self, message: str, rule: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details or {}
        )
        if rule:
            self.details["business_rule"] = rule

class ExternalServiceError(BaseLabException):
    """External service error exception."""
    
    def __init__(self, service: str, message: str = None, details: Dict[str, Any] = None):
        message = message or f"External service {service} is unavailable"
        super().__init__(
            message=message,
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            details=details or {}
        )
        self.details["service"] = service

class RateLimitError(BaseLabException):
    """Rate limit exceeded exception."""
    
    def __init__(self, limit: int, window: int, reset_time: int = None):
        super().__init__(
            message=f"Rate limit exceeded: {limit} requests per {window} seconds",
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            details={
                "limit": limit,
                "window": window,
                "reset_time": reset_time
            }
        )

# Specific lab management exceptions
class AppointmentConflictError(ConflictError):
    """Appointment scheduling conflict."""
    
    def __init__(self, datetime_str: str, lab_id: str = None):
        super().__init__(
            message=f"Appointment slot conflict at {datetime_str}",
            resource="appointment",
            details={
                "datetime": datetime_str,
                "lab_id": lab_id,
                "conflict_type": "time_slot"
            }
        )

class LabCapacityExceededError(ConflictError):
    """Lab capacity exceeded."""
    
    def __init__(self, current_count: int, max_capacity: int, datetime_str: str):
        super().__init__(
            message=f"Lab capacity exceeded: {current_count}/{max_capacity} at {datetime_str}",
            resource="lab_capacity",
            details={
                "current_count": current_count,
                "max_capacity": max_capacity,
                "datetime": datetime_str
            }
        )

class InvalidTestOrderStatusError(BusinessLogicError):
    """Invalid test order status transition."""
    
    def __init__(self, current_status: str, target_status: str):
        super().__init__(
            message=f"Invalid status transition from {current_status} to {target_status}",
            rule="test_order_status_transition",
            details={
                "current_status": current_status,
                "target_status": target_status
            }
        )

class LabServiceInactiveError(BusinessLogicError):
    """Lab service is inactive."""
    
    def __init__(self, service_name: str, service_id: str):
        super().__init__(
            message=f"Lab service '{service_name}' is currently inactive",
            rule="active_service_required",
            details={
                "service_name": service_name,
                "service_id": service_id
            }
        )

class FileUploadError(BaseLabException):
    """File upload error."""
    
    def __init__(self, message: str, filename: str = None, details: Dict[str, Any] = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            details=details or {}
        )
        if filename:
            self.details["filename"] = filename

# Exception handlers
def create_error_response(exc: BaseLabException) -> Dict[str, Any]:
    """Create standardized error response."""
    
    error_response = {
        "error": {
            "type": exc.__class__.__name__,
            "message": exc.message,
            "status_code": exc.status_code,
            "timestamp": __import__('datetime').datetime.utcnow().isoformat()
        }
    }
    
    if exc.details:
        error_response["error"]["details"] = exc.details
    
    # Log error for monitoring
    logger.error(
        f"Lab service error: {exc.__class__.__name__} - {exc.message}",
        extra={
            "error_type": exc.__class__.__name__,
            "status_code": exc.status_code,
            "details": exc.details
        }
    )
    
    return error_response

def handle_database_error(exc: Exception) -> BaseLabException:
    """Convert database exceptions to lab exceptions."""
    
    error_message = str(exc)
    
    # Handle common database errors
    if "duplicate key" in error_message.lower():
        return ConflictError("Resource already exists", details={"db_error": error_message})
    
    if "foreign key" in error_message.lower():
        return ValidationError("Invalid reference to related resource", details={"db_error": error_message})
    
    if "null" in error_message.lower() and "not" in error_message.lower():
        return ValidationError("Required field is missing", details={"db_error": error_message})
    
    if "cannot be null" in error_message.lower():
        return ValidationError("Required field is missing", details={"db_error": error_message})
    
    # Generic database error
    logger.error(f"Database error: {error_message}")
    return BaseLabException(
        "Database operation failed",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        details={"db_error": error_message}
    )

def handle_external_api_error(service: str, status_code: int, response_text: str) -> ExternalServiceError:
    """Handle external API errors."""
    
    return ExternalServiceError(
        service=service,
        message=f"External API error: {status_code}",
        details={
            "status_code": status_code,
            "response": response_text[:500]  # Limit response size
        }
    )