# FILE: backend/app/auth/dependencies.py
# VERSION: 1.0.0
# START_MODULE_CONTRACT
#   PURPOSE: FastAPI dependencies for authentication and authorization
#   SCOPE: Current user extraction, role-based access control
#   DEPENDS: M-BE-CORE, M-BE-DB, M-BE-AUTH (service, jwt_handler)
#   LINKS: M-BE-AUTH
# END_MODULE_CONTRACT

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.database.models import User
from app.auth.service import get_user_by_id
from app.auth.jwt_handler import verify_token
from app.exceptions import AuthenticationException, AuthorizationException

security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not credentials:
        raise AuthenticationException(message="Not authenticated")
    
    token = credentials.credentials
    payload = verify_token(token, token_type="access")
    
    if not payload:
        raise AuthenticationException(message="Invalid or expired token")
    
    user_id = payload.get("sub")
    if not user_id:
        raise AuthenticationException(message="Invalid token payload")
    
    user = await get_user_by_id(db, user_id)
    if not user:
        raise AuthenticationException(message="User not found")
    
    if not user.is_active:
        raise AuthenticationException(message="User account is disabled")
    
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except AuthenticationException:
        return None


def require_role(*required_roles: str):
    async def role_checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if current_user.is_superuser:
            return current_user
        
        if current_user.role not in required_roles:
            raise AuthorizationException(
                message=f"Required role: {', '.join(required_roles)}"
            )
        return current_user
    
    return role_checker


require_admin = require_role("admin")
require_operator = require_role("admin", "operator")
require_user = require_role("admin", "operator", "viewer")
