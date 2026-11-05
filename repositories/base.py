from typing import Generic, TypeVar, Type, Sequence
from sqlmodel import Session, select, SQLModel

ModelType = TypeVar("ModelType", bound=SQLModel)


class BaseRepository(Generic[ModelType]):
    """
    OOP Generic Abstraction & SOLID (DIP, SRP):
    Tüm veritabanı varlıkları için ortak CRUD operasyonlarını sağlayan temel depo sınıfı.
    """
    def __init__(self, model: Type[ModelType], session: Session):
        self.model = model
        self.session = session

    def get(self, id: int) -> ModelType | None:
        """Birincil anahtara göre tek bir kayıt getirir."""
        return self.session.get(self.model, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Sayfalanmış tüm kayıtları getirir."""
        statement = select(self.model).offset(skip).limit(limit)
        return self.session.exec(statement).all()

    def create(self, entity: ModelType) -> ModelType:
        """Yeni bir varlık ekler ve veritabanına kaydeder."""
        self.session.add(entity)
        self.session.commit()
        self.session.refresh(entity)
        return entity

    def update(self, db_obj: ModelType, obj_in: SQLModel | dict) -> ModelType:
        """Var olan bir varlığı günceller."""
        update_data = obj_in if isinstance(obj_in, dict) else obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        self.session.add(db_obj)
        self.session.commit()
        self.session.refresh(db_obj)
        return db_obj

    def delete(self, id: int) -> bool:
        """Kayıt varsa siler ve True döner, yoksa False döner."""
        obj = self.get(id)
        if obj:
            self.session.delete(obj)
            self.session.commit()
            return True
        return False
