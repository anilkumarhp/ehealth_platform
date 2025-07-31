"""
Compliance service for audit and regulatory requirements
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from typing import List
from uuid import UUID
import logging
from datetime import datetime, date

from app.models.compliance import AuditLog, ControlledSubstanceLog
from app.repositories.base_repository import BaseRepository
from app.schemas.compliance import AuditLogFilter, AuditLogResponse, ComplianceReport

logger = logging.getLogger(__name__)


class ComplianceService:
    """Service for compliance and audit operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_repo = BaseRepository(db, AuditLog)
        self.controlled_substance_repo = BaseRepository(db, ControlledSubstanceLog)
    
    async def get_audit_logs(self, filter_params: AuditLogFilter) -> List[AuditLogResponse]:
        """Get audit logs with filtering."""
        try:
            # Build filters
            filters = {}
            if filter_params.pharmacy_id:
                filters["pharmacy_id"] = filter_params.pharmacy_id
            if filter_params.user_id:
                filters["user_id"] = filter_params.user_id
            if filter_params.action:
                filters["action"] = filter_params.action
            if filter_params.resource_type:
                filters["resource_type"] = filter_params.resource_type
            if filter_params.severity:
                filters["severity"] = filter_params.severity
            
            # Get audit logs
            audit_logs = await self.audit_repo.get_multi(
                skip=filter_params.skip,
                limit=filter_params.limit,
                filters=filters,
                order_by="created_at"
            )
            
            # Filter by date range if provided
            if filter_params.start_date or filter_params.end_date:
                filtered_logs = []
                for log in audit_logs:
                    log_date = log.created_at.date()
                    if filter_params.start_date and log_date < filter_params.start_date:
                        continue
                    if filter_params.end_date and log_date > filter_params.end_date:
                        continue
                    filtered_logs.append(log)
                audit_logs = filtered_logs
            
            logger.info(f"Retrieved {len(audit_logs)} audit logs")
            return [AuditLogResponse.from_orm(log) for log in audit_logs]
        except Exception as e:
            logger.error(f"Error getting audit logs: {e}")
            raise
    
    async def generate_compliance_report(
        self, 
        pharmacy_id: UUID, 
        start_date: date, 
        end_date: date
    ) -> ComplianceReport:
        """Generate compliance report for a pharmacy."""
        try:
            # Get audit statistics
            audit_count_result = await self.db.execute(
                select(func.count(AuditLog.id)).where(
                    and_(
                        AuditLog.pharmacy_id == pharmacy_id,
                        AuditLog.created_at >= start_date,
                        AuditLog.created_at <= end_date
                    )
                )
            )
            total_transactions = audit_count_result.scalar() or 0
            
            # Get controlled substance transactions
            cs_count_result = await self.db.execute(
                select(func.count(ControlledSubstanceLog.id)).where(
                    and_(
                        ControlledSubstanceLog.pharmacy_id == pharmacy_id,
                        ControlledSubstanceLog.created_at >= start_date,
                        ControlledSubstanceLog.created_at <= end_date
                    )
                )
            )
            controlled_substance_transactions = cs_count_result.scalar() or 0
            
            # Get prescription validations
            validation_count_result = await self.db.execute(
                select(func.count(AuditLog.id)).where(
                    and_(
                        AuditLog.pharmacy_id == pharmacy_id,
                        AuditLog.action.like('%prescription%'),
                        AuditLog.created_at >= start_date,
                        AuditLog.created_at <= end_date
                    )
                )
            )
            prescription_validations = validation_count_result.scalar() or 0
            
            # Calculate compliance score (simplified)
            compliance_score = min(100.0, (prescription_validations / max(1, total_transactions)) * 100)
            
            # Generate recommendations
            recommendations = []
            if compliance_score < 80:
                recommendations.append("Increase prescription validation frequency")
            if controlled_substance_transactions > 0:
                recommendations.append("Ensure all controlled substances are properly logged")
            
            report = ComplianceReport(
                pharmacy_id=pharmacy_id,
                report_period=f"{start_date} to {end_date}",
                total_transactions=total_transactions,
                controlled_substance_transactions=controlled_substance_transactions,
                prescription_validations=prescription_validations,
                audit_events=total_transactions,
                compliance_score=compliance_score,
                issues_found=len(recommendations),
                recommendations=recommendations
            )
            
            logger.info(f"Generated compliance report for pharmacy {pharmacy_id}")
            return report
        except Exception as e:
            logger.error(f"Error generating compliance report: {e}")
            raise
    
    async def log_controlled_substance_transaction(
        self,
        pharmacy_id: UUID,
        medicine_id: UUID,
        transaction_data: dict
    ) -> bool:
        """Log controlled substance transaction."""
        try:
            cs_log_data = {
                "pharmacy_id": pharmacy_id,
                "medicine_id": medicine_id,
                **transaction_data
            }
            
            cs_log = await self.controlled_substance_repo.create(cs_log_data)
            
            logger.info(f"Logged controlled substance transaction {cs_log.id}")
            return True
        except Exception as e:
            logger.error(f"Error logging controlled substance transaction: {e}")
            raise
    
    async def get_compliance_alerts(self, pharmacy_id: UUID) -> List[dict]:
        """Get compliance alerts for a pharmacy."""
        try:
            alerts = []
            
            # Check for missing controlled substance logs
            # This would involve complex queries to identify gaps
            
            # Check for expired licenses
            # This would check staff license expiry dates
            
            # Check for audit log gaps
            # This would identify periods without proper logging
            
            # For now, return empty list
            logger.info(f"Retrieved {len(alerts)} compliance alerts for pharmacy {pharmacy_id}")
            return alerts
        except Exception as e:
            logger.error(f"Error getting compliance alerts: {e}")
            raise
    
    async def get_controlled_substances_report(self, pharmacy_id=None, start_date=None, end_date=None):
        """Get controlled substances report for DEA compliance."""
        try:
            # Set default dates if not provided
            if not start_date:
                start_date = date.today().replace(day=1)  # First day of current month
            if not end_date:
                end_date = date.today()
            
            # Get controlled substance logs
            query = select(ControlledSubstanceLog)
            
            if pharmacy_id:
                query = query.where(ControlledSubstanceLog.pharmacy_id == pharmacy_id)
            
            query = query.where(
                and_(
                    ControlledSubstanceLog.created_at >= start_date,
                    ControlledSubstanceLog.created_at <= end_date
                )
            )
            
            result = await self.db.execute(query)
            logs = result.scalars().all()
            
            # Group by DEA schedule
            report_data = {}
            for log in logs:
                schedule = log.dea_schedule
                if schedule not in report_data:
                    report_data[schedule] = {
                        "total_transactions": 0,
                        "dispensed": 0,
                        "received": 0,
                        "returned": 0,
                        "destroyed": 0
                    }
                
                report_data[schedule]["total_transactions"] += 1
                report_data[schedule][log.transaction_type] = report_data[schedule].get(log.transaction_type, 0) + 1
            
            # Format report
            report = {
                "report_period": f"{start_date} to {end_date}",
                "report_date": datetime.now().date().isoformat(),  # Add report_date
                "pharmacy_id": str(pharmacy_id) if pharmacy_id else "All Pharmacies",
                "generated_at": datetime.now().isoformat(),
                "total_transactions": len(logs),
                "schedule_summary": report_data,
                "substances": [],  # Add empty substances list
                "compliance_status": "Compliant",  # Would be calculated based on rules
                "recommendations": []
            }
            
            logger.info(f"Generated controlled substances report with {len(logs)} transactions")
            return report
        except Exception as e:
            logger.error(f"Error generating controlled substances report: {e}")
            raise