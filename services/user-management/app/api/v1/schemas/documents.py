from pydantic import BaseModel, ConfigDict
import uuid
from datetime import datetime

# --- Schemas ---
class GenerateUploadURLRequest(BaseModel):
    file_name: str
    content_type: str

class GenerateUploadURLResponse(BaseModel):
    upload_url: str
    document_id: uuid.UUID

class DocumentRead(BaseModel):
    id: uuid.UUID
    file_name: str
    content_type: str
    s3_key: str
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class MessageResponse(BaseModel):
    message: str
