from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, extract
from typing import Optional, Dict, Any
from datetime import datetime, date, timedelta
from uuid import UUID

from app.db.session import get_db_session
from app.api.deps import get_current_user
from app.core.security import TokenPayload
from app.models.appointment import Appointment, AppointmentStatusEnum
from app.models.test_order import TestOrder, TestOrderStatusEnum
from app.models.lab_service import LabService

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_metrics(
    *,
    db: AsyncSession = Depends(get_db_session),
    lab_id: Optional[UUID] = None,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: TokenPayload = Depends(get_current_user)
):
    """Get dashboard metrics for lab management."""
    
    # Default to last 30 days if no dates provided
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()
    
    # Use user's lab if not specified
    if not lab_id:
        lab_id = current_user.org_id
    
    # Total appointments
    appointments_query = select(func.count(Appointment.id)).where(
        and_(
            Appointment.lab_id == lab_id,
            func.date(Appointment.appointment_time) >= start_date,
            func.date(Appointment.appointment_time) <= end_date
        )
    )
    total_appointments = (await db.execute(appointments_query)).scalar()
    
    # Completed appointments
    completed_query = appointments_query.where(
        Appointment.status == AppointmentStatusEnum.COMPLETED
    )
    completed_appointments = (await db.execute(completed_query)).scalar()
    
    # Pending test orders
    pending_orders_query = select(func.count(TestOrder.id)).where(
        and_(
            TestOrder.organization_id == lab_id,
            TestOrder.status == TestOrderStatusEnum.PENDING_CONSENT
        )
    )
    pending_orders = (await db.execute(pending_orders_query)).scalar()
    
    # Revenue calculation (completed appointments)
    revenue_query = select(func.sum(LabService.price)).select_from(
        Appointment.__table__.join(LabService.__table__)
    ).where(
        and_(
            Appointment.lab_id == lab_id,
            Appointment.status == AppointmentStatusEnum.COMPLETED,
            func.date(Appointment.appointment_time) >= start_date,
            func.date(Appointment.appointment_time) <= end_date
        )
    )
    total_revenue = (await db.execute(revenue_query)).scalar() or 0
    
    return {
        "period": {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },
        "metrics": {
            "total_appointments": total_appointments,
            "completed_appointments": completed_appointments,
            "pending_orders": pending_orders,
            "total_revenue": float(total_revenue),
            "completion_rate": (completed_appointments / total_appointments * 100) if total_appointments > 0 else 0
        }
    }

@router.get("/appointments-by-day")
async def get_appointments_by_day(
    *,
    db: AsyncSession = Depends(get_db_session),
    lab_id: Optional[UUID] = None,
    days: int = Query(30, ge=1, le=365),
    current_user: TokenPayload = Depends(get_current_user)
):
    """Get appointment counts by day for the last N days."""
    
    if not lab_id:
        lab_id = current_user.org_id
    
    start_date = date.today() - timedelta(days=days)
    
    query = select(
        func.date(Appointment.appointment_time).label('appointment_date'),
        func.count(Appointment.id).label('count')
    ).where(
        and_(
            Appointment.lab_id == lab_id,
            func.date(Appointment.appointment_time) >= start_date
        )
    ).group_by(
        func.date(Appointment.appointment_time)
    ).order_by('appointment_date')
    
    result = await db.execute(query)
    data = result.all()
    
    return [
        {
            "date": row.appointment_date.isoformat(),
            "appointments": row.count
        }
        for row in data
    ]

@router.get("/popular-services")
async def get_popular_services(
    *,
    db: AsyncSession = Depends(get_db_session),
    lab_id: Optional[UUID] = None,
    limit: int = Query(10, ge=1, le=50),
    current_user: TokenPayload = Depends(get_current_user)
):
    """Get most popular lab services by appointment count."""
    
    if not lab_id:
        lab_id = current_user.org_id
    
    query = select(
        LabService.name,
        LabService.price,
        func.count(Appointment.id).label('appointment_count')
    ).select_from(
        LabService.__table__.join(Appointment.__table__)
    ).where(
        LabService.lab_id == lab_id
    ).group_by(
        LabService.id, LabService.name, LabService.price
    ).order_by(
        func.count(Appointment.id).desc()
    ).limit(limit)
    
    result = await db.execute(query)
    data = result.all()
    
    return [
        {
            "service_name": row.name,
            "price": float(row.price),
            "appointment_count": row.appointment_count
        }
        for row in data
    ]

@router.get("/monthly-revenue")
async def get_monthly_revenue(
    *,
    db: AsyncSession = Depends(get_db_session),
    lab_id: Optional[UUID] = None,
    months: int = Query(12, ge=1, le=24),
    current_user: TokenPayload = Depends(get_current_user)
):
    """Get monthly revenue for the last N months."""
    
    if not lab_id:
        lab_id = current_user.org_id
    
    query = select(
        extract('year', Appointment.appointment_time).label('year'),
        extract('month', Appointment.appointment_time).label('month'),
        func.sum(LabService.price).label('revenue')
    ).select_from(
        Appointment.__table__.join(LabService.__table__)
    ).where(
        and_(
            Appointment.lab_id == lab_id,
            Appointment.status == AppointmentStatusEnum.COMPLETED,
            Appointment.appointment_time >= datetime.now() - timedelta(days=months * 30)
        )
    ).group_by(
        extract('year', Appointment.appointment_time),
        extract('month', Appointment.appointment_time)
    ).order_by('year', 'month')
    
    result = await db.execute(query)
    data = result.all()
    
    return [
        {
            "year": int(row.year),
            "month": int(row.month),
            "revenue": float(row.revenue or 0)
        }
        for row in data
    ]