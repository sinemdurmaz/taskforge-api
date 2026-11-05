import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

# Proje ana dizinindeki .env dosyasını bul ve yükle
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings(BaseModel):
    """
    Uygulama genelinde kullanılan konfigürasyon parametreleri.
    
    OOP - Encapsulation (Kapsülleme):
        Konfigürasyon parametreleri dağınık değişkenler yerine tek bir tip-güvenli
        sınıf altında toplanır ve kapsüllenir.
        
    SOLID - Single Responsibility (Tek Sorumluluk - S):
        Yalnızca konfigürasyon verilerini okuma ve doğrulama sorumluluğuna sahiptir.
        Veritabanı veya API mantığı içermez.
    """
    PROJECT_NAME: str = "TaskForge API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Veritabanı
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///taskforge.db")
    
    # Güvenlik & JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "super-secret-taskforge-development-key-change-in-prod")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


# Singleton örneği: Uygulama genelinde tek bir konfigürasyon nesnesi kullanılır
settings = Settings()
