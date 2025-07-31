from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime
from typing import List

class ConsentGrant(BaseModel):
    # Who are you giving consent to?
    data_fiduciary_id: uuid.UUID
    # Why are you giving consent?
    purpose: str
    # What data can they access?
    data_categories: List[str]
    # How long can they access it for?
    expires_at: datetime

class ConsentRead(BaseModel):
    id: uuid.UUID
    patient_id: uuid.UUID
    data_fiduciary_id: uuid.UUID
    status: str
    purpose: str
    data_categories: List[str]
    granted_at: datetime
    expires_at: datetime
    withdrawn_at: datetime | None = None
    
    model_config = ConfigDict(from_attributes=True)