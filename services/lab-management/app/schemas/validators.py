from pydantic import validator, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
import re


class HealthcareValidators:
    """Common validators for healthcare data."""
    
    @staticmethod
    def validate_phone_number(phone: str) -> str:
        """Validate phone number format."""
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        # Check if it's a valid length (10-15 digits)
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise ValueError("Phone number must be 10-15 digits")
        
        # Format as international number
        if len(digits_only) == 10:
            return f"+1{digits_only}"  # Assume US number
        elif digits_only.startswith('1') and len(digits_only) == 11:
            return f"+{digits_only}"
        else:
            return f"+{digits_only}"
    
    @staticmethod
    def validate_email(email: str) -> str:
        """Validate email format."""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        return email.lower()
    
    @staticmethod
    def validate_date_of_birth(dob: str) -> str:
        """Validate date of birth."""
        try:
            birth_date = datetime.strptime(dob, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("Date of birth must be in YYYY-MM-DD format")
        
        # Check if date is not in the future
        if birth_date > date.today():
            raise ValueError("Date of birth cannot be in the future")
        
        # Check if person is not too old (reasonable limit)
        age = (date.today() - birth_date).days // 365
        if age > 150:
            raise ValueError("Invalid date of birth - age too high")
        
        return dob
    
    @staticmethod
    def validate_gender(gender: str) -> str:
        """Validate gender value."""
        gender_map = {
            'M': 'M', 'MALE': 'M',
            'F': 'F', 'FEMALE': 'F', 
            'O': 'O', 'OTHER': 'O',
            'U': 'U', 'UNKNOWN': 'U'
        }
        
        gender_upper = gender.upper()
        if gender_upper not in gender_map:
            raise ValueError(f"Gender must be one of: M, F, O, U, male, female, other, unknown")
        return gender_map[gender_upper]
    
    @staticmethod
    def validate_price(price: float) -> float:
        """Validate price value."""
        if price < 0:
            raise ValueError("Price cannot be negative")
        if price > 999999.99:
            raise ValueError("Price too high")
        # Round to 2 decimal places
        return round(price, 2)
    
    @staticmethod
    def validate_clinical_notes(notes: Optional[str]) -> Optional[str]:
        """Validate clinical notes."""
        if notes is None:
            return None
        
        # Remove excessive whitespace
        notes = notes.strip()
        
        # Check length
        if len(notes) > 5000:
            raise ValueError("Clinical notes too long (max 5000 characters)")
        
        return notes if notes else None
    
    @staticmethod
    def validate_test_name(name: str) -> str:
        """Validate test name."""
        name = name.strip()
        if not name:
            raise ValueError("Test name cannot be empty")
        if len(name) > 200:
            raise ValueError("Test name too long (max 200 characters)")
        return name
    
    @staticmethod
    def validate_reference_range(range_str: str) -> str:
        """Validate reference range format."""
        range_str = range_str.strip()
        if not range_str:
            raise ValueError("Reference range cannot be empty")
        
        # Common patterns: "10-20", "<10", ">20", "≤10", "≥20", "Negative", "Positive"
        valid_patterns = [
            r'^\d+(\.\d+)?-\d+(\.\d+)?$',  # 10-20, 10.5-20.5
            r'^[<≤]\s*\d+(\.\d+)?$',       # <10, ≤10
            r'^[>≥]\s*\d+(\.\d+)?$',       # >20, ≥20
            r'^(Negative|Positive|Normal|Abnormal)$',  # Qualitative results
            r'^\d+(\.\d+)?\s*(mg/dL|g/dL|mmol/L|IU/L|%)?$'  # Single value with unit
        ]
        
        if not any(re.match(pattern, range_str, re.IGNORECASE) for pattern in valid_patterns):
            raise ValueError("Invalid reference range format")
        
        return range_str
    
    @staticmethod
    def validate_appointment_time(dt_str: str) -> str:
        """Validate appointment datetime."""
        try:
            appointment_dt = datetime.fromisoformat(dt_str.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError("Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)")
        
        # Check if appointment is in the future
        if appointment_dt <= datetime.utcnow():
            raise ValueError("Appointment must be scheduled for future time")
        
        # Check if appointment is not too far in the future (1 year)
        max_future = datetime.utcnow().replace(year=datetime.utcnow().year + 1)
        if appointment_dt > max_future:
            raise ValueError("Appointment cannot be scheduled more than 1 year in advance")
        
        return dt_str
    
    @staticmethod
    def validate_lab_service_name(name: str) -> str:
        """Validate lab service name."""
        name = name.strip()
        if not name:
            raise ValueError("Lab service name cannot be empty")
        if len(name) < 3:
            raise ValueError("Lab service name too short (min 3 characters)")
        if len(name) > 200:
            raise ValueError("Lab service name too long (max 200 characters)")
        return name
    
    @staticmethod
    def validate_uuid_list(uuid_list: List[str]) -> List[UUID]:
        """Validate list of UUID strings."""
        validated_uuids = []
        for uuid_str in uuid_list:
            try:
                validated_uuids.append(UUID(uuid_str))
            except ValueError:
                raise ValueError(f"Invalid UUID format: {uuid_str}")
        return validated_uuids