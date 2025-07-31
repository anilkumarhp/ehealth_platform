"""
Custom exceptions for Pharma Management Service
"""

from fastapi import HTTPException
from typing import Optional


class PharmaException(HTTPException):
    """Base exception for pharma service."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        error_code: Optional[str] = None,
        headers: Optional[dict] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


# Prescription-related exceptions
class PrescriptionNotFoundException(PharmaException):
    def __init__(self, prescription_id: str):
        super().__init__(
            status_code=404,
            detail=f"Prescription {prescription_id} not found",
            error_code="PRESCRIPTION_NOT_FOUND"
        )


class InvalidPrescriptionException(PharmaException):
    def __init__(self, reason: str):
        super().__init__(
            status_code=400,
            detail=f"Invalid prescription: {reason}",
            error_code="INVALID_PRESCRIPTION"
        )


class PrescriptionExpiredException(PharmaException):
    def __init__(self, prescription_id: str):
        super().__init__(
            status_code=400,
            detail=f"Prescription {prescription_id} has expired",
            error_code="PRESCRIPTION_EXPIRED"
        )


# Inventory-related exceptions
class InsufficientStockException(PharmaException):
    def __init__(self, medicine_name: str, available: int, requested: int):
        super().__init__(
            status_code=409,
            detail=f"Insufficient stock for {medicine_name}. Available: {available}, Requested: {requested}",
            error_code="INSUFFICIENT_STOCK"
        )


class MedicineNotFoundException(PharmaException):
    def __init__(self, medicine_id: str):
        super().__init__(
            status_code=404,
            detail=f"Medicine {medicine_id} not found",
            error_code="MEDICINE_NOT_FOUND"
        )


class ExpiredMedicineException(PharmaException):
    def __init__(self, medicine_name: str, batch_number: str):
        super().__init__(
            status_code=400,
            detail=f"Medicine {medicine_name} (Batch: {batch_number}) has expired",
            error_code="EXPIRED_MEDICINE"
        )


# Order-related exceptions
class OrderNotFoundException(PharmaException):
    def __init__(self, order_id: str):
        super().__init__(
            status_code=404,
            detail=f"Order {order_id} not found",
            error_code="ORDER_NOT_FOUND"
        )


class OrderAlreadyFulfilledException(PharmaException):
    def __init__(self, order_id: str):
        super().__init__(
            status_code=409,
            detail=f"Order {order_id} has already been fulfilled",
            error_code="ORDER_ALREADY_FULFILLED"
        )


# Compliance-related exceptions
class ControlledSubstanceViolationException(PharmaException):
    def __init__(self, reason: str):
        super().__init__(
            status_code=403,
            detail=f"Controlled substance violation: {reason}",
            error_code="CONTROLLED_SUBSTANCE_VIOLATION"
        )


class DrugInteractionException(PharmaException):
    def __init__(self, interaction_details: str):
        super().__init__(
            status_code=400,
            detail=f"Drug interaction detected: {interaction_details}",
            error_code="DRUG_INTERACTION"
        )


class InsuranceVerificationException(PharmaException):
    def __init__(self, reason: str):
        super().__init__(
            status_code=402,
            detail=f"Insurance verification failed: {reason}",
            error_code="INSURANCE_VERIFICATION_FAILED"
        )


# OCR-related exceptions
class OCRProcessingException(PharmaException):
    def __init__(self, reason: str):
        super().__init__(
            status_code=422,
            detail=f"OCR processing failed: {reason}",
            error_code="OCR_PROCESSING_FAILED"
        )


class InvalidPrescriptionImageException(PharmaException):
    def __init__(self, reason: str):
        super().__init__(
            status_code=400,
            detail=f"Invalid prescription image: {reason}",
            error_code="INVALID_PRESCRIPTION_IMAGE"
        )


# Pharmacy-related exceptions
class PharmacyNotFoundException(PharmaException):
    def __init__(self, pharmacy_id: str):
        super().__init__(
            status_code=404,
            detail=f"Pharmacy {pharmacy_id} not found",
            error_code="PHARMACY_NOT_FOUND"
        )


class PharmacyNotActiveException(PharmaException):
    def __init__(self, pharmacy_id: str):
        super().__init__(
            status_code=403,
            detail=f"Pharmacy {pharmacy_id} is not active",
            error_code="PHARMACY_NOT_ACTIVE"
        )


# External service exceptions
class ExternalServiceException(PharmaException):
    def __init__(self, service_name: str, reason: str):
        super().__init__(
            status_code=503,
            detail=f"External service {service_name} error: {reason}",
            error_code="EXTERNAL_SERVICE_ERROR"
        )