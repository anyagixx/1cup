# FILE: backend/app/auth/router.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: Authentication REST API endpoints
#   SCOPE: Login, logout, token refresh, password change, user management
#   DEPENDS: M-BE-CORE, M-BE-DB, M-BE-AUTH (service, dependencies)
#   LINKS: M-BE-AUTH
# END_MODULE_CONTRACT

from datetime import datetime
from typing import Annotated
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.database.models import User, AuditLog
from app.database.schemas import (
    LoginRequest,
    TokenResponse,
    RefreshRequest,
    UserCreate,
    UserResponse,
    UserUpdate,
    UserListResponse,
    PasswordChange,
)
from app.auth.service import (
    authenticate_user,
    create_tokens_for_user,
    hash_password,
    change_user_password,
    get_user_by_id,
)
from app.auth.dependencies import get_current_user, require_admin
from app.auth.jwt_handler import verify_token
from app.exceptions import AuthenticationException, ValidationException

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    user = await authenticate_user(db, request.username, request.password)
    if not user:
        raise AuthenticationException(message="Invalid username or password")
    
    audit = AuditLog(
        user_id=user.id,
        action="login",
        resource_type="user",
        resource_id=str(user.id),
    )
    db.add(audit)
    await db.commit()
    
    return await create_tokens_for_user(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    payload = verify_token(request.refresh_token, token_type="refresh")
    if not payload:
        raise AuthenticationException(message="Invalid refresh token")
    
    user_id = payload.get("sub")
    user = await get_user_by_id(db, user_id)
    
    if not user or not user.is_active:
        raise AuthenticationException(message="User not found or inactive")
    
    return await create_tokens_for_user(user)


@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    audit = AuditLog(
        user_id=current_user.id,
        action="logout",
        resource_type="user",
        resource_id=str(current_user.id),
    )
    db.add(audit)
    await db.commit()
    
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user


@router.post("/change-password")
async def change_password(
    request: PasswordChange,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    success = await change_user_password(
        db, current_user, request.current_password, request.new_password
    )
    if not success:
        raise ValidationException(message="Current password is incorrect")
    
    return {"message": "Password changed successfully"}


@router.get("/users", response_model=UserListResponse)
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
    skip: int = 0,
    limit: int = 50,
):
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    
    count_result = await db.execute(select(User))
    total = len(count_result.scalars().all())
    
    return UserListResponse(items=[UserResponse.model_validate(u) for u in users], total=total)


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    request: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    existing = await db.execute(
        select(User).where(
            (User.username == request.username) | (User.email == request.email)
        )
    )
    if existing.scalar_one_or_none():
        raise ValidationException(message="Username or email already exists")
    
    user = User(
        username=request.username,
        email=request.email,
        hashed_password=hash_password(request.password),
        full_name=request.full_name,
        role=request.role,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: str,
    request: UserUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValidationException(message="User not found")
    
    update_data = request.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    
    return user


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_admin)],
):
    user = await get_user_by_id(db, user_id)
    if not user:
        raise ValidationException(message="User not found")
    
    user.is_active = False
    await db.commit()
    
    return {"message": "User deactivated"}
