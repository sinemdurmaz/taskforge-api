from sqlmodel import Session, select
from models.user import User
from repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Kullanıcıya özel veritabanı sorguları.
    """
    def __init__(self, session: Session):
        super().__init__(User, session)

    def get_by_email(self, email: str) -> User | None:
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()
