from pydantic import BaseModel
from pydantic.types import PositiveInt, UUID, AwareDatetime
from typing import ClassVar


class SecretBase(BaseModel):
    secret: str | bytes


class SecretCreate(SecretBase):
    ttl_seconds: PositiveInt
    passphrase: str | None = None


class SecretRead(SecretCreate):
    passphrase: ClassVar[int]
    secret_key: UUID
    is_accessed: bool
    created_at: AwareDatetime


class SecretPassphrase(BaseModel):
    passphrase: str | None = None
