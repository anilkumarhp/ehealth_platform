from pydantic import BaseModel
from enum import Enum

class FileType(str, Enum):
    PROFILE_PHOTO = "profile_photo"
    INSURANCE_DOCUMENT = "insurance_document"
    MEDICAL_RECORD = "medical_record"
    OTHER = "other"

class FileUploadResponse(BaseModel):
    file_id: str
    file_url: str
    file_type: FileType
    content_type: str
    size: int