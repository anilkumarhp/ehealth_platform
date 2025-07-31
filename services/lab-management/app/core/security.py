from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from functools import wraps
from fastapi import HTTPException, status


class TokenPayload(BaseModel):
    sub: UUID
    full_name: str
    date_of_birth: str
    gender: str
    primary_mobile_number: str
    email: str
    roles: List[str]
    org_id: Optional[UUID] = None
    national_health_id: Optional[str] = None
    address: Optional[str] = None


class RoleBasedAuth:
    """Role-based access control utilities."""
    
    @staticmethod
    def require_role(required_roles: List[str]):
        """Decorator to require specific roles for endpoint access."""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # Get current_user from kwargs
                current_user = kwargs.get('current_user')
                if not current_user:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Authentication required"
                    )
                
                # Check if user has required role
                user_roles = current_user.roles if hasattr(current_user, 'roles') else []
                if not any(role in user_roles for role in required_roles):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Required roles: {required_roles}"
                    )
                
                return await func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def check_patient_access(patient_id: UUID, current_user: TokenPayload) -> bool:
        """Check if user can access patient data."""
        # Patient can access their own data
        if current_user.sub == patient_id:
            return True
        
        # Medical staff can access patient data
        medical_roles = ["doctor", "nurse", "lab-admin", "lab-technician"]
        if any(role in current_user.roles for role in medical_roles):
            return True
        
        return False
    
    @staticmethod
    def check_lab_access(lab_id: UUID, current_user: TokenPayload) -> bool:
        """Check if user can access lab data."""
        # User must belong to the lab organization
        if current_user.org_id == lab_id:
            return True
        
        # Admin roles can access any lab
        admin_roles = ["system-admin", "hospital-admin"]
        if any(role in current_user.roles for role in admin_roles):
            return True
        
        return False
    
    @staticmethod
    def check_report_access(report_patient_id: UUID, current_user: TokenPayload) -> bool:
        """Check if user can access medical reports."""
        # Patient can access their own reports
        if current_user.sub == report_patient_id:
            return True
        
        # Medical professionals can access reports
        medical_roles = ["doctor", "nurse", "lab-admin"]
        if any(role in current_user.roles for role in medical_roles):
            return True
        
        return False


# Role definitions
class UserRoles:
    PATIENT = "patient"
    DOCTOR = "doctor"
    NURSE = "nurse"
    LAB_ADMIN = "lab-admin"
    LAB_TECHNICIAN = "lab-technician"
    HOSPITAL_ADMIN = "hospital-admin"
    SYSTEM_ADMIN = "system-admin"
    
    @classmethod
    def get_medical_roles(cls) -> List[str]:
        return [cls.DOCTOR, cls.NURSE, cls.LAB_ADMIN, cls.LAB_TECHNICIAN]
    
    @classmethod
    def get_admin_roles(cls) -> List[str]:
        return [cls.HOSPITAL_ADMIN, cls.SYSTEM_ADMIN, cls.LAB_ADMIN]