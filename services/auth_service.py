from datetime import datetime, timedelta, timezone
from pwdlib import PasswordHash
import jwt
from sqlmodel import Session
from core.config import settings
from models.user import User, UserCreate
from repositories.user_repository import UserRepository

password_hash = PasswordHash.recommended()


class AuthService:
    """
    Kullanıcı kimlik doğrulama, parola hashleme ve JWT üretimi sorumluluğu (SOLID SRP).
    """
    def __init__(self, session: Session):
        self.session = session
        self.user_repo = UserRepository(session)

    @staticmethod
    def hash_password(password: str) -> str:
        """Parolayı Argon2 algoritmasıyla güvenli şekilde hashler."""
        return password_hash.hash(password)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Düz metin parolayı Argon2 hash'i ile karşılaştırır."""
        return password_hash.verify(plain_password, hashed_password)

    def register_user(self, user_in: UserCreate) -> User:
        """Yeni bir kullanıcı kaydeder; email benzersizliğini denetler."""
        existing = self.user_repo.get_by_email(user_in.email)
        if existing:
            raise ValueError(f"Bu e-posta adresi zaten kullanımda: {user_in.email}")

        hashed = self.hash_password(user_in.password)
        user = User(
            email=user_in.email,
            full_name=user_in.full_name,
            role=user_in.role,
            is_active=user_in.is_active,
            hashed_password=hashed
        )
        return self.user_repo.create(user)

    def authenticate_user(self, email: str, password: str) -> User | None:
        """Kullanıcı e-posta ve parolasını doğrular."""
        user = self.user_repo.get_by_email(email)
        if not user or not self.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    def create_access_token(user_id: int, role: str) -> str:
        """Kullanıcı için süreli JWT erişim anahtarı oluşturur."""
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),
            "role": role,
            "exp": expire,
            "iat": datetime.now(timezone.utc),
        }
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
