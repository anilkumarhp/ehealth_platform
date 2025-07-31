"""
Clinical support service
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID
import logging
from datetime import datetime
import uuid

from app.models.clinical import DrugInteraction, InteractionCheck, AdverseDrugReaction
from app.repositories.base_repository import BaseRepository
from app.schemas.clinical import (
    InteractionCheckRequest, InteractionCheckResponse, 
    ADRReportCreate, ADRReportResponse, DrugInteractionDetail
)
from app.services.audit_service import AuditService

logger = logging.getLogger(__name__)


class ClinicalService:
    """Service for clinical support operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.interaction_repo = BaseRepository(db, DrugInteraction)
        self.interaction_check_repo = BaseRepository(db, InteractionCheck)
        self.adr_repo = BaseRepository(db, AdverseDrugReaction)
        self.audit_service = AuditService(db)
    
    async def check_drug_interactions(
        self, 
        request: InteractionCheckRequest
    ) -> InteractionCheckResponse:
        """Check for drug-drug interactions."""
        try:
            check_id = str(uuid.uuid4())[:8].upper()
            
            # Get medicine names (simplified - would query medicine table)
            medicine_names = [f"Medicine-{str(mid)[:8]}" for mid in request.medicine_ids]
            
            # Simulate interaction checking
            # In production, this would query the drug interaction database
            interactions = []
            interactions_found = 0
            highest_severity = "none"
            
            # Mock interaction for demonstration
            if len(request.medicine_ids) >= 2:
                interactions.append(DrugInteractionDetail(
                    drug1_name=medicine_names[0],
                    drug2_name=medicine_names[1],
                    interaction_type="pharmacokinetic",
                    severity="moderate",
                    mechanism="CYP450 enzyme inhibition",
                    clinical_effect="Increased plasma concentration",
                    management_strategy="Monitor patient closely",
                    monitoring_required=True,
                    alternative_drugs=["Alternative-A", "Alternative-B"]
                ))
                interactions_found = 1
                highest_severity = "moderate"
            
            # Create interaction check record
            check_data = {
                "check_id": check_id,
                "patient_id": request.patient_id,
                "medicines_checked": [str(mid) for mid in request.medicine_ids],
                "current_medications": request.current_medications,
                "interactions_found": interactions_found,
                "highest_severity": highest_severity,
                "interaction_details": [interaction.dict() for interaction in interactions],
                "check_type": "automated"
            }
            
            interaction_check = await self.interaction_check_repo.create(check_data)
            
            # Generate recommendations
            recommendations = []
            if interactions_found > 0:
                recommendations.append("Consult with pharmacist before dispensing")
                recommendations.append("Monitor patient for adverse effects")
                if highest_severity in ["major", "contraindicated"]:
                    recommendations.append("Consider alternative medications")
            
            # Log audit trail
            await self.audit_service.log_action(
                action="drug_interaction_check",
                resource_type="clinical",
                resource_id=interaction_check.id,
                description=f"Checked interactions for {len(request.medicine_ids)} medicines",
                metadata={
                    "patient_id": str(request.patient_id),
                    "medicines_count": len(request.medicine_ids),
                    "interactions_found": interactions_found,
                    "highest_severity": highest_severity
                }
            )
            
            response = InteractionCheckResponse(
                check_id=check_id,
                patient_id=request.patient_id,
                medicines_checked=medicine_names,
                interactions_found=interactions_found,
                highest_severity=highest_severity,
                interactions=interactions,
                recommendations=recommendations,
                requires_pharmacist_review=interactions_found > 0,
                check_timestamp=datetime.utcnow().isoformat()
            )
            
            logger.info(f"Completed drug interaction check {check_id}")
            return response
        except Exception as e:
            logger.error(f"Error checking drug interactions: {e}")
            raise
    
    async def submit_adr_report(self, adr_data: ADRReportCreate) -> ADRReportResponse:
        """Submit Adverse Drug Reaction report."""
        try:
            # Generate report ID
            report_id = f"ADR-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            # Create ADR report
            adr_dict = adr_data.dict()
            adr_dict["report_id"] = report_id
            adr_dict["report_date"] = datetime.now().date()
            adr_dict["status"] = "submitted"
            
            adr_report = await self.adr_repo.create(adr_dict)
            
            # Log audit trail
            await self.audit_service.log_action(
                action="adr_report_submitted",
                resource_type="clinical",
                resource_id=adr_report.id,
                description=f"Submitted ADR report {report_id}",
                metadata={
                    "reporter_type": adr_data.reporter_type,
                    "suspected_drug": adr_data.suspected_drug_name,
                    "severity": adr_data.severity,
                    "outcome": adr_data.outcome
                }
            )
            
            response = ADRReportResponse.from_orm(adr_report)
            
            logger.info(f"Submitted ADR report {report_id}")
            return response
        except Exception as e:
            logger.error(f"Error submitting ADR report: {e}")
            raise
    
    async def get_drug_interactions(
        self, 
        drug1_id: UUID, 
        drug2_id: UUID
    ) -> List[DrugInteractionDetail]:
        """Get specific drug interactions."""
        try:
            interactions = await self.interaction_repo.get_multi(
                filters={
                    "drug1_id": drug1_id,
                    "drug2_id": drug2_id,
                    "is_active": True
                }
            )
            
            interaction_details = []
            for interaction in interactions:
                detail = DrugInteractionDetail(
                    drug1_name="Drug 1",  # Would get from medicine table
                    drug2_name="Drug 2",  # Would get from medicine table
                    interaction_type=interaction.interaction_type,
                    severity=interaction.severity,
                    mechanism=interaction.mechanism,
                    clinical_effect=interaction.clinical_effect,
                    management_strategy=interaction.management_strategy,
                    monitoring_required=interaction.monitoring_required,
                    alternative_drugs=interaction.alternative_drugs
                )
                interaction_details.append(detail)
            
            return interaction_details
        except Exception as e:
            logger.error(f"Error getting drug interactions: {e}")
            raise