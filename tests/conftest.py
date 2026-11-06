import pytest
from typing import Generator
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool
import models  # Modellerin metadata'ya kaydolması için
from core.database import get_session
from main import app
from models.user import User
from models.enums import UserRole
from services.auth_service import AuthService


@pytest.fixture(name="session")
def session_fixture() -> Generator[Session, None, None]:
    """
    Her test için RAM'de çalışan (in-memory) tertemiz bir SQLite veritabanı sağlar.
    Test bittiğinde otomatik olarak bellekten silinir.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="client")
def client_fixture(session: Session) -> Generator[TestClient, None, None]:
    """
    FastAPI get_session bağımlılığını geçici test oturumuyla ezen TestClient üretir.
    """
    def get_session_override():
        return session

    app.dependency_overrides[get_session] = get_session_override
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def admin_user(session: Session) -> User:
    """Testler için hazır Admin kullanıcısı oluşturur."""
    auth_service = AuthService(session)
    user = User(
        email="test_admin@taskforge.dev",
        full_name="Test Admin",
        role=UserRole.ADMIN,
        hashed_password=auth_service.hash_password("AdminPass123!"),
        is_active=True
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


@pytest.fixture
def admin_headers(admin_user: User) -> dict[str, str]:
    """Admin kullanıcısı için Bearer Token authorization başlığı üretir."""
    token = AuthService.create_access_token(admin_user.id, admin_user.role.value)
    return {"Authorization": f"Bearer {token}"}
