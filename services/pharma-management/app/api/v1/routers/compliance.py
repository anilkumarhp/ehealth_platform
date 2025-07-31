"""
Compliance and audit endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from uuid import UUID
from datetime import date
import logging

from app.db.session import get_async_session
from app.schemas.compliance import AuditLogResponse, AuditLogFilter
from app.services.compliance_service import ComplianceService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/reports/controlled-substances")
async def get_controlled_substances_report(
    pharmacy_id: Optional[UUID] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_async_session)
):
    """Get controlled substances report for DEA compliance."""
    try:
        compliance_service = ComplianceService(db)
        report = await compliance_service.get_controlled_substances_report(
            pharmacy_id, start_date, end_date
        )
        return report
    except ValueError as e:
        logger.error(f"Validation error in controlled substances report: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting controlled substances report: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/audit-logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    pharmacy_id: Optional[UUID] = Query(None),
    user_id: Optional[UUID] = Query(None),
    action: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    severity: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_async_session)
):
    """Get audit logs for compliance reporting."""
    try:
        compliance_service = ComplianceService(db)
        
        filter_params = AuditLogFilter(
            pharmacy_id=pharmacy_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            start_date=start_date,
            end_date=end_date,
            severity=severity,
            skip=skip,
            limit=limit
        )
        
        audit_logs = await compliance_service.get_audit_logs(filter_params)
        logger.info(f"Retrieved {len(audit_logs)} audit logs with filters")
        return audit_logs
    except ValueError as e:
        logger.error(f"Validation error in audit log request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error getting audit logs: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")