from typing import Sequence
from sqlmodel import Session, select
from models.project import Project, Sprint
from repositories.base import BaseRepository


class ProjectRepository(BaseRepository[Project]):
    """
    Proje varlığına özel veritabanı sorguları.
    """
    def __init__(self, session: Session):
        super().__init__(Project, session)

    def get_by_key(self, key: str) -> Project | None:
        statement = select(Project).where(Project.key == key.upper())
        return self.session.exec(statement).first()

    def get_by_owner(self, owner_id: int) -> Sequence[Project]:
        statement = select(Project).where(Project.owner_id == owner_id)
        return self.session.exec(statement).all()


class SprintRepository(BaseRepository[Sprint]):
    """
    Sprint varlığına özel veritabanı sorguları.
    """
    def __init__(self, session: Session):
        super().__init__(Sprint, session)

    def get_active_sprints(self, project_id: int) -> Sequence[Sprint]:
        statement = select(Sprint).where(
            Sprint.project_id == project_id,
            Sprint.is_active == True
        )
        return self.session.exec(statement).all()
