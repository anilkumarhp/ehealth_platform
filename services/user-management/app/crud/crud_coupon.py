import uuid
from sqlalchemy.orm import Session
from datetime import datetime
from app.db import models

def get_valid_coupon_by_code(db: Session, *, code: str, plan_id: uuid.UUID) -> models.Coupon | None:
    """
    Finds a coupon and validates it:
    - Is it active?
    - Has it not expired?
    - Is it applicable to the given plan?
    """
    now = datetime.utcnow()
    coupon = db.query(models.Coupon).filter(
        models.Coupon.code == code,
        models.Coupon.is_active == True,
        models.Coupon.expires_at > now,
    ).first()

    if coupon:
        # Check if the coupon is applicable to the specific plan
        for plan in coupon.applicable_plans:
            if plan.id == plan_id:
                return coupon
    return None