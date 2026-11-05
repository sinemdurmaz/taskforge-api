from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlmodel import Session
from core.config import settings
from core.database import get_session
from models.user import User
from models.enums import UserRole
from repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")


def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: Annotated[Session, Depends(get_session)]
) -> User:
    """
    Dependency Injection (Bağımlılık Enjeksiyonu):
    Gelen istekteki Bearer Token'ı çözer, veritabanından kullanıcıyı çeker ve doğrular.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Geçersiz kimlik doğrulama anahtarı.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    user_repo = UserRepository(session)
    user = user_repo.get(int(user_id))
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Kullanıcı bulunamadı veya hesabı pasif durumda."
        )
    return user


def require_role(allowed_roles: list[UserRole]):
    """
    Rol Tabanlı Erişim Kontrolü (RBAC):
    Yalnızca belirtilen rollere sahip kullanıcıların endpoint'e erişmesine izin verir.
    """
    def role_checker(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Bu işlem için yetkiniz yetersiz. İzin verilen roller: {[r.value for r in allowed_roles]}"
            )
        return current_user
    return role_checker
