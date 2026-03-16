# FILE: backend/app/auth/service.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: User authentication business logic
#   SCOPE: Password hashing, user verification, token creation
#   DEPENDS: M-BE-CORE, M-BE-DB, M-BE-AUTH (jwt_handler)
#   LINKS: M-BE-AUTH
# END_MODULE_CONTRACT

from datetime import datetime
from typing import Optional
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User
from app.database.schemas import TokenResponse
from app.auth.jwt_handler import create_access_token, create_refresh_token
from app.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


async def authenticate_user(
    db: AsyncSession,
    username: str,
    password: str,
) -> Optional[User]:
    result = await db.execute(
        select(User).where(
            (User.username == username) | (User.email == username)
        )
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    if not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    
    user.last_login = datetime.utcnow()
    await db.commit()
    
    return user


async def create_tokens_for_user(user: User) -> TokenResponse:
    access_token = create_access_token(
        subject=str(user.id),
        extra_data={
            "username": user.username,
            "role": user.role,
            "is_superuser": user.is_superuser,
        }
    )
    refresh_token = create_refresh_token(subject=str(user.id))
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


async def get_user_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def change_user_password(
    db: AsyncSession,
    user: User,
    current_password: str,
    new_password: str,
) -> bool:
    if not verify_password(current_password, user.hashed_password):
        return False
    
    user.hashed_password = hash_password(new_password)
    await db.commit()
    return True
