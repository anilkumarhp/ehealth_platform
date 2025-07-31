import uuid
from sqlalchemy.orm import Session
from datetime import date

from app.db import models

def create_document_record(
    db: Session, 
    *, 
    doc_id: uuid.UUID,
    patient_id: uuid.UUID, 
    uploader_id: uuid.UUID,
    file_name: str,
    content_type: str,
    s3_key: str
) -> models.MedicalDocument:
    """
    Create a record for a medical document in the database before upload.
    """
    db_document = models.MedicalDocument(
        id=doc_id,
        patient_id=patient_id,
        uploader_id=uploader_id,
        file_name=file_name,
        content_type=content_type,
        s3_key=s3_key,
        status=models.DocumentStatus.PENDING_UPLOAD
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

def get_document_by_id(db: Session, doc_id: uuid.UUID) -> models.MedicalDocument | None:
    """Get a document by its ID."""
    return db.query(models.MedicalDocument).filter(models.MedicalDocument.id == doc_id).first()

def update_document_status(db: Session, *, doc: models.MedicalDocument, status: models.DocumentStatus) -> models.MedicalDocument:
    """Update the status of a document (e.g., after successful upload)."""
    doc.status = status
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc

def get_documents_for_patient(db: Session, *, patient_id: uuid.UUID) -> list[models.MedicalDocument]:
    """Get a list of all documents for a specific patient."""
    return db.query(models.MedicalDocument).filter(models.MedicalDocument.patient_id == patient_id).all()

def get_documents_for_patient(
    db: Session, 
    *, 
    patient_id: uuid.UUID,
    search: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    # You can also add the hierarchical filters here
    source_org_id: uuid.UUID | None = None,
    source_practitioner_id: uuid.UUID | None = None,
    category: models.DocumentCategory | None = None
) -> list[models.MedicalDocument]:
    """
    Get a list of all documents for a specific patient, with optional filters.
    """
    query = db.query(models.MedicalDocument).filter(models.MedicalDocument.patient_id == patient_id)

    if search:
        query = query.filter(models.MedicalDocument.file_name.ilike(f"%{search}%"))
    
    if start_date:
        query = query.filter(models.MedicalDocument.created_at >= start_date)
        
    if end_date:
        query = query.filter(models.MedicalDocument.created_at <= end_date)

    if source_org_id:
        query = query.filter(models.MedicalDocument.source_organization_id == source_org_id)
        
    if source_practitioner_id:
        query = query.filter(models.MedicalDocument.source_practitioner_id == source_practitioner_id)

    if category:
        query = query.filter(models.MedicalDocument.document_category == category)

    return query.order_by(models.MedicalDocument.created_at.desc()).all()

def get_unique_document_sources(db: Session, *, patient_id: uuid.UUID) -> list:
    """Gets a unique list of source organizations and practitioners for a patient's documents."""
    query = db.query(
        models.MedicalDocument.source_organization_id,
        models.Organization.name.label("organization_name"),
        models.MedicalDocument.source_practitioner_id,
        models.User.personal_info['first_name'].astext().label("practitioner_first_name")
    ).join(
        models.Organization, models.MedicalDocument.source_organization_id == models.Organization.id
    ).join(
        models.User, models.MedicalDocument.source_practitioner_id == models.User.id
    ).filter(
        models.MedicalDocument.patient_id == patient_id
    ).distinct()
    
    return query.all()