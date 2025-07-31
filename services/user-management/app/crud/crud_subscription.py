import uuid
from sqlalchemy.orm import Session
from app.db import models

def get_plan_by_id(db: Session, plan_id: uuid.UUID) -> models.SubscriptionPlan | None:
    return db.query(models.SubscriptionPlan).filter(models.SubscriptionPlan.id == plan_id, models.SubscriptionPlan.is_active == True).first()