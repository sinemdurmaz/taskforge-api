from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from core.database import get_session
from models.user import UserCreate, UserRead, User
from services.auth_service import AuthService
from api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Kimlik Doğrulama"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, session: Annotated[Session, Depends(get_session)]):
    """Yeni kullanıcı kaydı oluşturur."""
    auth_service = AuthService(session)
    try:
        return auth_service.register_user(user_in)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Annotated[Session, Depends(get_session)]
):
    """Kullanıcı girişi yapar ve JWT erişim token'ı üretir."""
    auth_service = AuthService(session)
    user = auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Hatalı e-posta veya parola.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = auth_service.create_access_token(user.id, user.role.value)
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserRead)
def get_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Oturum açmış kullanıcının kendi profil bilgilerini getirir."""
    return current_user
