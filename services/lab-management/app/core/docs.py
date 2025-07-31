from typing import Dict, Any


# OpenAPI documentation configuration
OPENAPI_CONFIG = {
    "title": "Lab Management Service API",
    "description": """
## Lab Management Service

A comprehensive API for managing laboratory services, test orders, appointments, and reports in a healthcare environment.

### Key Features

- **Lab Services Management**: Create and manage laboratory test services
- **Test Order Workflow**: Handle test ordering with consent management
- **Appointment Scheduling**: Schedule and manage lab appointments
- **Report Management**: Upload and share test reports
- **Payment Processing**: Handle payments for lab services
- **Consent Management**: Manage patient consent for tests and data sharing

### Authentication

All endpoints require JWT authentication via the `Authorization` header:
```
Authorization: Bearer <your-jwt-token>
```

### User Roles

- **Patient**: Can view own orders, approve consent, schedule appointments
- **Doctor/Nurse**: Can order tests for patients, view reports with consent
- **Lab Admin**: Can manage lab services, upload reports, manage appointments
- **Lab Technician**: Can update test status, upload results

### Workflow Overview

1. **Test Ordering**: Doctor orders test for patient
2. **Consent**: Patient receives consent request and approves
3. **Appointment**: Patient schedules appointment at lab
4. **Test Execution**: Lab performs test and uploads results
5. **Payment**: Patient pays for completed tests
6. **Report Sharing**: Reports shared with authorized parties

### Error Handling

The API uses standard HTTP status codes and returns structured error responses:

```json
{
  "message": "Error description",
  "details": {
    "field": "specific_field",
    "code": "ERROR_CODE"
  },
  "error_code": "LAB_400"
}
```

### Rate Limiting

API requests are rate-limited to ensure fair usage and system stability.

### Compliance

This API is designed to comply with healthcare regulations including:
- HIPAA (Health Insurance Portability and Accountability Act)
- GDPR (General Data Protection Regulation)
- HITECH (Health Information Technology for Economic and Clinical Health Act)
    """,
    "version": "1.0.0",
    "contact": {
        "name": "Lab Management API Support",
        "email": "support@hospital.com",
        "url": "https://hospital.com/support"
    },
    "license_info": {
        "name": "Proprietary",
        "url": "https://hospital.com/license"
    },
    "servers": [
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api-staging.hospital.com",
            "description": "Staging server"
        },
        {
            "url": "https://api.hospital.com",
            "description": "Production server"
        }
    ]
}

# Tags for API organization
API_TAGS = [
    {
        "name": "Authentication",
        "description": "User authentication and authorization endpoints"
    },
    {
        "name": "Lab Services",
        "description": "Manage laboratory test services and test definitions"
    },
    {
        "name": "Test Orders",
        "description": "Create and manage test orders with consent workflow"
    },
    {
        "name": "Appointments",
        "description": "Schedule and manage lab appointments"
    },
    {
        "name": "Reports",
        "description": "Upload, manage, and share test reports"
    },
    {
        "name": "Payments",
        "description": "Handle payment processing for lab services"
    },
    {
        "name": "Consent Management",
        "description": "Manage patient consent for tests and data sharing"
    },
    {
        "name": "Workflow Management",
        "description": "Advanced workflow operations and utilities"
    },
    {
        "name": "Health Checks",
        "description": "System health and monitoring endpoints"
    }
]

# Example responses for documentation
EXAMPLE_RESPONSES = {
    "lab_service": {
        "id": "123e4567-e89b-12d3-a456-426614174000",
        "name": "Complete Blood Count (CBC)",
        "description": "Comprehensive blood analysis including red blood cells, white blood cells, and platelets",
        "price": 85.50,
        "is_active": True,
        "lab_id": "987fcdeb-51a2-43d1-9c4f-123456789abc",
        "test_definitions": [
            {
                "id": "456e7890-e89b-12d3-a456-426614174001",
                "name": "Hemoglobin",
                "unit": "g/dL",
                "reference_range": "13.5-17.5"
            },
            {
                "id": "789e0123-e89b-12d3-a456-426614174002",
                "name": "White Blood Cell Count",
                "unit": "cells/mcL",
                "reference_range": "4500-11000"
            }
        ]
    },
    "test_order": {
        "id": "234e5678-e89b-12d3-a456-426614174003",
        "patient_user_id": "345e6789-e89b-12d3-a456-426614174004",
        "requesting_entity_id": "456e7890-e89b-12d3-a456-426614174005",
        "organization_id": "567e8901-e89b-12d3-a456-426614174006",
        "lab_service_id": "123e4567-e89b-12d3-a456-426614174000",
        "status": "PENDING_CONSENT",
        "clinical_notes": "Patient reports fatigue and dizziness",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    },
    "appointment": {
        "id": "678e9012-e89b-12d3-a456-426614174007",
        "test_order_id": "234e5678-e89b-12d3-a456-426614174003",
        "patient_user_id": "345e6789-e89b-12d3-a456-426614174004",
        "lab_service_id": "123e4567-e89b-12d3-a456-426614174000",
        "lab_id": "987fcdeb-51a2-43d1-9c4f-123456789abc",
        "appointment_time": "2024-01-20T09:00:00Z",
        "status": "SCHEDULED",
        "created_at": "2024-01-15T14:30:00Z"
    },
    "error_response": {
        "message": "Validation error",
        "details": {
            "field": "price",
            "constraint": "must be positive"
        },
        "error_code": "LAB_422"
    }
}

# Security schemes for OpenAPI
SECURITY_SCHEMES = {
    "BearerAuth": {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "JWT token obtained from authentication endpoint"
    }
}