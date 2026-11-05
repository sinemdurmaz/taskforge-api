from typing import Generator
from sqlmodel import Session, SQLModel, create_engine
from core.config import settings

# SQLite için multi-thread FastAPI uyumluluğu
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

# Veritabanı motoru (Engine)
engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args
)


def init_db() -> None:
    """
    Veritabanı tablolarını metadata üzerinden oluşturur.
    Tüm modeller import edildikten sonra çağrılır.
    """
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    FastAPI Depends ile kullanılacak veritabanı oturum sağlayıcısı.
    
    Tasarım Deseni:
        - Dependency Injection (Bağımlılık Enjeksiyonu): Endpoint'lere oturum enjekte eder.
        - Unit of Work: Session nesnesi, tüm veritabanı işlemlerini tek bir iş birimi olarak izler.
        
    ACID Prensipleri:
        - Atomicity (Bölünemezlik): Başarılı yield sonrası işlem tamamlanır.
          Beklenmeyen bir hata fırlatılırsa otomatik session.rollback() çalışır ("ya hep ya hiç").
        - Durability (Kalıcılık): Commit edilen işlemler diske güvenli şekilde yazılır.
    """
    with Session(engine) as session:
        try:
            yield session
        except Exception:
            session.rollback()
            raise
