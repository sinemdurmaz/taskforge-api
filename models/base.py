from datetime import datetime, timezone
from sqlmodel import Field, SQLModel


class TimeStampedModel(SQLModel):
    """
    OOP Inheritance (Kalıtım):
    Tüm varlıkların ortak zamansal ve birincil anahtar (PK) alanlarını kapsüller.
    """
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
