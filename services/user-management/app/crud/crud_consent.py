import uuid
from sqlalchemy.orm import Session
from datetime import datetime

from app.db import models
from app.api.v1.schemas import consent as consent_schema

def create_consent(db: Session, *, patient_id: uuid.UUID, consent_in: consent_schema.ConsentGrant) -> models.ConsentRecord:
    db_consent = models.ConsentRecord(
        patient_id=patient_id,
        data_fiduciary_id=consent_in.data_fiduciary_id,
        purpose=consent_in.purpose,
        data_categories=consent_in.data_categories,
        expires_at=consent_in.expires_at,
        status=models.ConsentStatus.GRANTED
    )
    db.add(db_consent)
    db.commit()
    db.refresh(db_consent)
    return db_consent

def get_consents_given_by_patient(db: Session, *, patient_id: uuid.UUID) -> list[models.ConsentRecord]:
    return db.query(models.ConsentRecord).filter(models.ConsentRecord.patient_id == patient_id).all()

def get_consent_by_id(db: Session, consent_id: uuid.UUID) -> models.ConsentRecord | None:
    return db.query(models.ConsentRecord).filter(models.ConsentRecord.id == consent_id).first()

def revoke_consent(db: Session, consent: models.ConsentRecord) -> models.ConsentRecord:
    consent.status = models.ConsentStatus.REVOKED
    consent.withdrawn_at = datetime.utcnow()
    db.add(consent)
    db.commit()
    db.refresh(consent)
    return consent