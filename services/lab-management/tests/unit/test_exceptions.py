import pytest
from fastapi import status
from datetime import datetime

from app.core.exceptions import (
    BaseLabException,
    ValidationError,
    NotFoundError,
    ConflictError,
    AuthorizationError,
    BusinessLogicError,
    ExternalServiceError,
    RateLimitError,
    AppointmentConflictError,
    LabCapacityExceededError,
    InvalidTestOrderStatusError,
    LabServiceInactiveError,
    FileUploadError,
    create_error_response,
    handle_database_error,
    handle_external_api_error
)


class TestBaseLabException:
    """Unit tests for BaseLabException."""

    def test_base_exception_creation(self):
        """Test creating base lab exception."""
        exc = BaseLabException(
            message="Test error",
            status_code=status.HTTP_400_BAD_REQUEST,
            details={"field": "value"}
        )
        
        assert exc.message == "Test error"
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.details == {"field": "value"}
        assert str(exc) == "Test error"

    def test_base_exception_defaults(self):
        """Test base exception with default values."""
        exc = BaseLabException("Test error")
        
        assert exc.message == "Test error"
        assert exc.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exc.details == {}


class TestSpecificExceptions:
    """Unit tests for specific exception types."""

    def test_validation_error(self):
        """Test ValidationError creation."""
        exc = ValidationError("Invalid input", field="email")
        
        assert exc.message == "Invalid input"
        assert exc.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert exc.details["field"] == "email"

    def test_not_found_error(self):
        """Test NotFoundError creation."""
        exc = NotFoundError("User", "123")
        
        assert "User not found" in exc.message
        assert "123" in exc.message
        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.details["resource"] == "User"
        assert exc.details["identifier"] == "123"

    def test_not_found_error_without_identifier(self):
        """Test NotFoundError without identifier."""
        exc = NotFoundError("User")
        
        assert exc.message == "User not found"
        assert exc.details["identifier"] is None

    def test_conflict_error(self):
        """Test ConflictError creation."""
        exc = ConflictError("Resource already exists", resource="appointment")
        
        assert exc.message == "Resource already exists"
        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.details["resource"] == "appointment"

    def test_authorization_error(self):
        """Test AuthorizationError creation."""
        exc = AuthorizationError("Access denied", action="delete_appointment")
        
        assert exc.message == "Access denied"
        assert exc.status_code == status.HTTP_403_FORBIDDEN
        assert exc.details["action"] == "delete_appointment"

    def test_authorization_error_default_message(self):
        """Test AuthorizationError with default message."""
        exc = AuthorizationError()
        
        assert exc.message == "Insufficient permissions"
        assert exc.status_code == status.HTTP_403_FORBIDDEN

    def test_business_logic_error(self):
        """Test BusinessLogicError creation."""
        exc = BusinessLogicError("Invalid operation", rule="appointment_scheduling")
        
        assert exc.message == "Invalid operation"
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.details["business_rule"] == "appointment_scheduling"

    def test_external_service_error(self):
        """Test ExternalServiceError creation."""
        exc = ExternalServiceError("payment_service", "Service timeout")
        
        assert "Service timeout" in exc.message
        assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert exc.details["service"] == "payment_service"

    def test_external_service_error_default_message(self):
        """Test ExternalServiceError with default message."""
        exc = ExternalServiceError("payment_service")
        
        assert "payment_service is unavailable" in exc.message
        assert exc.details["service"] == "payment_service"

    def test_rate_limit_error(self):
        """Test RateLimitError creation."""
        exc = RateLimitError(100, 3600, reset_time=1234567890)
        
        assert "100 requests per 3600 seconds" in exc.message
        assert exc.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert exc.details["limit"] == 100
        assert exc.details["window"] == 3600
        assert exc.details["reset_time"] == 1234567890


class TestDomainSpecificExceptions:
    """Unit tests for domain-specific exceptions."""

    def test_appointment_conflict_error(self):
        """Test AppointmentConflictError creation."""
        datetime_str = "2024-01-15T10:00:00"
        lab_id = "lab123"
        
        exc = AppointmentConflictError(datetime_str, lab_id)
        
        assert datetime_str in exc.message
        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.details["datetime"] == datetime_str
        assert exc.details["lab_id"] == lab_id
        assert exc.details["conflict_type"] == "time_slot"

    def test_lab_capacity_exceeded_error(self):
        """Test LabCapacityExceededError creation."""
        exc = LabCapacityExceededError(5, 3, "2024-01-15T10:00:00")
        
        assert "5/3" in exc.message
        assert exc.status_code == status.HTTP_409_CONFLICT
        assert exc.details["current_count"] == 5
        assert exc.details["max_capacity"] == 3

    def test_invalid_test_order_status_error(self):
        """Test InvalidTestOrderStatusError creation."""
        exc = InvalidTestOrderStatusError("PENDING", "COMPLETED")
        
        assert "PENDING" in exc.message
        assert "COMPLETED" in exc.message
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.details["current_status"] == "PENDING"
        assert exc.details["target_status"] == "COMPLETED"

    def test_lab_service_inactive_error(self):
        """Test LabServiceInactiveError creation."""
        exc = LabServiceInactiveError("Blood Test", "service123")
        
        assert "Blood Test" in exc.message
        assert "inactive" in exc.message
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.details["service_name"] == "Blood Test"
        assert exc.details["service_id"] == "service123"

    def test_file_upload_error(self):
        """Test FileUploadError creation."""
        exc = FileUploadError("File too large", filename="test.pdf")
        
        assert exc.message == "File too large"
        assert exc.status_code == status.HTTP_400_BAD_REQUEST
        assert exc.details["filename"] == "test.pdf"


class TestErrorHandlers:
    """Unit tests for error handling functions."""

    def test_create_error_response(self):
        """Test creating standardized error response."""
        exc = ValidationError("Invalid input", field="email")
        
        response = create_error_response(exc)
        
        assert "error" in response
        assert response["error"]["type"] == "ValidationError"
        assert response["error"]["message"] == "Invalid input"
        assert response["error"]["status_code"] == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert "timestamp" in response["error"]
        assert response["error"]["details"]["field"] == "email"

    def test_handle_database_error_duplicate_key(self):
        """Test handling duplicate key database error."""
        db_error = Exception("duplicate key value violates unique constraint")
        
        lab_exception = handle_database_error(db_error)
        
        assert isinstance(lab_exception, ConflictError)
        assert "already exists" in lab_exception.message
        assert lab_exception.status_code == status.HTTP_409_CONFLICT

    def test_handle_database_error_foreign_key(self):
        """Test handling foreign key database error."""
        db_error = Exception("foreign key constraint fails")
        
        lab_exception = handle_database_error(db_error)
        
        assert isinstance(lab_exception, ValidationError)
        assert "Invalid reference" in lab_exception.message
        assert lab_exception.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_handle_database_error_not_null(self):
        """Test handling not null database error."""
        db_error = Exception("column cannot be null")
        
        lab_exception = handle_database_error(db_error)
        
        assert isinstance(lab_exception, ValidationError)
        assert "Required field" in lab_exception.message
        assert lab_exception.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_handle_database_error_generic(self):
        """Test handling generic database error."""
        db_error = Exception("unknown database error")
        
        lab_exception = handle_database_error(db_error)
        
        assert isinstance(lab_exception, BaseLabException)
        assert "Database operation failed" in lab_exception.message
        assert lab_exception.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    def test_handle_external_api_error(self):
        """Test handling external API error."""
        service = "payment_service"
        status_code = 503
        response_text = "Service temporarily unavailable"
        
        exc = handle_external_api_error(service, status_code, response_text)
        
        assert isinstance(exc, ExternalServiceError)
        assert service in exc.message or exc.details["service"] == service
        assert exc.details["status_code"] == status_code
        assert response_text in exc.details["response"]

    def test_handle_external_api_error_long_response(self):
        """Test handling external API error with long response."""
        service = "payment_service"
        status_code = 500
        response_text = "A" * 1000  # Very long response
        
        exc = handle_external_api_error(service, status_code, response_text)
        
        # Response should be truncated to 500 characters
        assert len(exc.details["response"]) == 500
        assert exc.details["response"] == "A" * 500