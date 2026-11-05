from sqlmodel import Field, SQLModel
from models.base import TimeStampedModel
from models.enums import UserRole


class UserBase(SQLModel):
    """
    OOP Base: Kullanıcı için ortak alanlar.
    """
    email: str = Field(unique=True, index=True)
    full_name: str
    role: UserRole = Field(default=UserRole.DEVELOPER)
    is_active: bool = Field(default=True)


class UserCreate(UserBase):
    """
    SOLID (SRP): İstemciden kullanıcı kaydı için gelen DTO.
    Düz metin parolayı içerir.
    """
    password: str


class UserRead(UserBase):
    """
    SOLID (SRP): API yanıtlarında döndürülen DTO.
    Hassas parola hash'ini ASLA içermez.
    """
    id: int


class UserUpdate(SQLModel):
    """
    Kullanıcı profili güncelleme DTO'su.
    """
    email: str | None = None
    full_name: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class User(TimeStampedModel, UserBase, table=True):
    """
    Veritabanı tablosu entity'si.
    """
    hashed_password: str
