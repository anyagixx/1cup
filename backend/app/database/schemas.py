# FILE: backend/app/database/schemas.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Pydantic schemas for request/response validation
#   SCOPE: User schemas, auth schemas, pagination schemas
#   DEPENDS: None
#   LINKS: M-BE-DB
# END_MODULE_CONTRACT

import uuid
from datetime import datetime
from typing import Optional, Generic, TypeVar
from pydantic import BaseModel, EmailStr, Field

T = TypeVar("T")


class BaseResponse(BaseModel):
    class Config:
        from_attributes = True


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    full_name: Optional[str] = Field(None, max_length=100)
    role: str = Field(default="viewer", pattern="^(admin|operator|viewer)$")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=100)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, max_length=100)
    role: Optional[str] = Field(None, pattern="^(admin|operator|viewer)$")
    is_active: Optional[bool] = None


class UserResponse(UserBase, BaseResponse):
    id: uuid.UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime]


class UserListResponse(BaseModel):
    items: list[UserResponse]
    total: int


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class RefreshRequest(BaseModel):
    refresh_token: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=100)


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
    pages: int


class AuditLogResponse(BaseModel, BaseResponse):
    id: uuid.UUID
    user_id: Optional[uuid.UUID]
    action: str
    resource_type: str
    resource_id: Optional[str]
    details: Optional[str]
    ip_address: Optional[str]
    created_at: datetime


class ErrorResponse(BaseModel):
    error: dict
