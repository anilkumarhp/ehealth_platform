import pytest
from datetime import datetime, date, timedelta
from pydantic import ValidationError

from app.schemas.validators import HealthcareValidators


class TestHealthcareValidators:
    """Test healthcare-specific validation functions."""

    def test_validate_phone_number_valid(self):
        """Test valid phone number formats."""
        # US format
        result = HealthcareValidators.validate_phone_number("(555) 123-4567")
        assert result == "+15551234567"
        
        # International format
        result = HealthcareValidators.validate_phone_number("+1-555-123-4567")
        assert result == "+15551234567"
        
        # Digits only
        result = HealthcareValidators.validate_phone_number("5551234567")
        assert result == "+15551234567"

    def test_validate_phone_number_invalid(self):
        """Test invalid phone number formats."""
        with pytest.raises(ValueError, match="Phone number must be 10-15 digits"):
            HealthcareValidators.validate_phone_number("123")  # Too short
        
        with pytest.raises(ValueError, match="Phone number must be 10-15 digits"):
            HealthcareValidators.validate_phone_number("12345678901234567890")  # Too long

    def test_validate_email_valid(self):
        """Test valid email formats."""
        result = HealthcareValidators.validate_email("test@example.com")
        assert result == "test@example.com"
        
        result = HealthcareValidators.validate_email("USER@DOMAIN.COM")
        assert result == "user@domain.com"  # Should be lowercase

    def test_validate_email_invalid(self):
        """Test invalid email formats."""
        with pytest.raises(ValueError, match="Invalid email format"):
            HealthcareValidators.validate_email("invalid-email")
        
        with pytest.raises(ValueError, match="Invalid email format"):
            HealthcareValidators.validate_email("@domain.com")

    def test_validate_date_of_birth_valid(self):
        """Test valid date of birth."""
        result = HealthcareValidators.validate_date_of_birth("1990-05-15")
        assert result == "1990-05-15"

    def test_validate_date_of_birth_invalid(self):
        """Test invalid date of birth."""
        # Future date
        future_date = (date.today().replace(year=date.today().year + 1)).strftime("%Y-%m-%d")
        with pytest.raises(ValueError, match="Date of birth cannot be in the future"):
            HealthcareValidators.validate_date_of_birth(future_date)
        
        # Invalid format
        with pytest.raises(ValueError, match="Date of birth must be in YYYY-MM-DD format"):
            HealthcareValidators.validate_date_of_birth("05/15/1990")
        
        # Too old
        with pytest.raises(ValueError, match="Invalid date of birth - age too high"):
            HealthcareValidators.validate_date_of_birth("1800-01-01")

    def test_validate_gender_valid(self):
        """Test valid gender values."""
        assert HealthcareValidators.validate_gender("M") == "M"
        assert HealthcareValidators.validate_gender("f") == "F"
        assert HealthcareValidators.validate_gender("other") == "O"
        assert HealthcareValidators.validate_gender("unknown") == "U"

    def test_validate_gender_invalid(self):
        """Test invalid gender values."""
        with pytest.raises(ValueError, match="Gender must be one of"):
            HealthcareValidators.validate_gender("invalid")

    def test_validate_price_valid(self):
        """Test valid price values."""
        assert HealthcareValidators.validate_price(100.50) == 100.50
        assert HealthcareValidators.validate_price(0.01) == 0.01
        assert HealthcareValidators.validate_price(999999.99) == 999999.99
        
        # Test rounding
        assert HealthcareValidators.validate_price(100.555) == 100.56

    def test_validate_price_invalid(self):
        """Test invalid price values."""
        with pytest.raises(ValueError, match="Price cannot be negative"):
            HealthcareValidators.validate_price(-10.00)
        
        with pytest.raises(ValueError, match="Price too high"):
            HealthcareValidators.validate_price(9999999.99)

    def test_validate_clinical_notes_valid(self):
        """Test valid clinical notes."""
        result = HealthcareValidators.validate_clinical_notes("Patient reports fatigue")
        assert result == "Patient reports fatigue"
        
        # Empty notes should return None
        result = HealthcareValidators.validate_clinical_notes("")
        assert result is None
        
        result = HealthcareValidators.validate_clinical_notes(None)
        assert result is None

    def test_validate_clinical_notes_invalid(self):
        """Test invalid clinical notes."""
        long_notes = "A" * 5001  # Too long
        with pytest.raises(ValueError, match="Clinical notes too long"):
            HealthcareValidators.validate_clinical_notes(long_notes)

    def test_validate_test_name_valid(self):
        """Test valid test names."""
        result = HealthcareValidators.validate_test_name("Complete Blood Count")
        assert result == "Complete Blood Count"
        
        # Test trimming
        result = HealthcareValidators.validate_test_name("  Glucose Test  ")
        assert result == "Glucose Test"

    def test_validate_test_name_invalid(self):
        """Test invalid test names."""
        with pytest.raises(ValueError, match="Test name cannot be empty"):
            HealthcareValidators.validate_test_name("")
        
        long_name = "A" * 201
        with pytest.raises(ValueError, match="Test name too long"):
            HealthcareValidators.validate_test_name(long_name)

    def test_validate_reference_range_valid(self):
        """Test valid reference ranges."""
        valid_ranges = [
            "10-20",
            "10.5-20.5",
            "<10",
            ">20",
            "≤10",
            "≥20",
            "Negative",
            "Positive",
            "Normal",
            "15 mg/dL",
            "10.5 g/dL"
        ]
        
        for range_str in valid_ranges:
            result = HealthcareValidators.validate_reference_range(range_str)
            assert result == range_str

    def test_validate_reference_range_invalid(self):
        """Test invalid reference ranges."""
        with pytest.raises(ValueError, match="Reference range cannot be empty"):
            HealthcareValidators.validate_reference_range("")
        
        with pytest.raises(ValueError, match="Invalid reference range format"):
            HealthcareValidators.validate_reference_range("invalid-range")

    def test_validate_appointment_datetime_valid(self):
        """Test valid appointment datetime."""
        future_time = (datetime.utcnow().replace(microsecond=0) + timedelta(hours=1)).isoformat()
        result = HealthcareValidators.validate_appointment_time(future_time)
        assert result == future_time

    def test_validate_appointment_datetime_invalid(self):
        """Test invalid appointment datetime."""
        # Past time
        past_time = (datetime.utcnow() - timedelta(hours=1)).isoformat()
        with pytest.raises(ValueError, match="Appointment must be scheduled for future time"):
            HealthcareValidators.validate_appointment_time(past_time)
        
        # Too far in future
        far_future = (datetime.utcnow().replace(year=datetime.utcnow().year + 2)).isoformat()
        with pytest.raises(ValueError, match="Appointment cannot be scheduled more than 1 year"):
            HealthcareValidators.validate_appointment_time(far_future)
        
        # Invalid format
        with pytest.raises(ValueError, match="Invalid datetime format"):
            HealthcareValidators.validate_appointment_time("invalid-datetime")

    def test_validate_lab_service_name_valid(self):
        """Test valid lab service names."""
        result = HealthcareValidators.validate_lab_service_name("Complete Blood Count")
        assert result == "Complete Blood Count"

    def test_validate_lab_service_name_invalid(self):
        """Test invalid lab service names."""
        with pytest.raises(ValueError, match="Lab service name cannot be empty"):
            HealthcareValidators.validate_lab_service_name("")
        
        with pytest.raises(ValueError, match="Lab service name too short"):
            HealthcareValidators.validate_lab_service_name("AB")
        
        long_name = "A" * 201
        with pytest.raises(ValueError, match="Lab service name too long"):
            HealthcareValidators.validate_lab_service_name(long_name)