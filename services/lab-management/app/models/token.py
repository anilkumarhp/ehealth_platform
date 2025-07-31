from pydantic import BaseModel, UUID4
from datetime import datetime
from typing import Optional, List


class TokenPayload(BaseModel):
    """
    Represents the data decoded from a JWT access token.
    """
    sub: UUID4  # The subject of the token (the user's ID)
    exp: datetime
    # These are optional fields that a real User Management service would provide.
    roles: List[str] = []
    org_id: Optional[UUID4] = None # The organization/lab the user belongs to
