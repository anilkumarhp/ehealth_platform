"""
Clinical support and compliance endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import logging

from app.db.session import get_async_session
from app.schemas.clinical import (
    InteractionCheckRequest, InteractionCheckResponse,
    ADRReportCreate, ADRReportResponse
)
from app.services.clinical_service import ClinicalService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/interactions/check", response_model=InteractionCheckResponse)
async def check_drug_interactions(
    interaction_request: InteractionCheckRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """Check for drug-drug interactions."""
    try:
        clinical_service = ClinicalService(db)
        interaction_result = await clinical_service.check_drug_interactions(
            interaction_request
        )
        logger.info(f"Successfully checked drug interactions for patient {interaction_request.patient_id}")
        return interaction_result
    except ValueError as e:
        logger.error(f"Validation error in drug interaction check: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error checking drug interactions: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/pharmacovigilance/reports/adr", response_model=ADRReportResponse)
async def submit_adr_report(
    adr_report: ADRReportCreate,
    db: AsyncSession = Depends(get_async_session)
):
    """Submit Adverse Drug Reaction (ADR) report."""
    try:
        clinical_service = ClinicalService(db)
        adr_response = await clinical_service.submit_adr_report(adr_report)
        logger.info(f"Successfully submitted ADR report {adr_response.report_id}")
        return adr_response
    except ValueError as e:
        logger.error(f"Validation error in ADR report: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error submitting ADR report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")