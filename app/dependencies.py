import uuid
from uuid import UUID
from typing import Sequence, Union
from builtins import Exception, dict, str
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import Database
from app.utils.template_manager import TemplateManager
from app.services.email_service import EmailService
from app.services.jwt_service import decode_token
from settings.config import Settings
from fastapi import Depends
from app.models.user_model import User, UserRole

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login/")

def get_settings() -> Settings:
    """Return application settings."""
    return Settings()

def get_email_service() -> EmailService:
    template_manager = TemplateManager()
    return EmailService(template_manager=template_manager)

async def get_db() -> AsyncSession:
    """Dependency that provides a database session for each request."""
    async_session_factory = Database.get_session_factory()
    async with async_session_factory() as session:
        try:
            yield session
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
        



async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    credentials_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if not payload or "sub" not in payload:
        raise credentials_exc

    try:
        user_uuid = UUID(payload["sub"])   # ← now this will succeed
    except ValueError:
        raise credentials_exc

    user = await db.get(User, user_uuid)
    if not user:
        # Token was valid, but the user record no longer exists
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user

def require_role(allowed: Sequence[Union[UserRole,str]]):
    """
    Dependency that ensures current_user.role is one of the allowed roles.
    allowed can be enum members or their .name strings.
    """
    allowed_names = {
        r.name if isinstance(r, UserRole) else str(r)
        for r in allowed
    }

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        # current_user.role is a UserRole enum
        role_name = (
            current_user.role.name
            if isinstance(current_user.role, UserRole)
            else str(current_user.role)
        )
        if role_name not in allowed_names:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted"
            )
        return current_user

    return role_checker