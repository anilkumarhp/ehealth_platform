from pydantic import BaseModel, ConfigDict
import uuid
from typing import List

class PermissionRead(BaseModel):
    id: uuid.UUID
    name: str
    description: str | None = None
    model_config = ConfigDict(from_attributes=True)

class RoleBase(BaseModel):
    name: str
    description: str | None = None

class RoleCreate(RoleBase):
    permission_ids: List[uuid.UUID] = []

class RoleUpdate(RoleBase):
    permission_ids: List[uuid.UUID] = []

class RoleRead(RoleBase):
    id: uuid.UUID
    permissions: List[PermissionRead] = []
    model_config = ConfigDict(from_attributes=True)