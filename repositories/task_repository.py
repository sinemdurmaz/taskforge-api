from typing import Sequence
from sqlmodel import Session, select
from models.task import Task
from models.enums import TaskPriority, TaskStatus
from repositories.base import BaseRepository


class TaskRepository(BaseRepository[Task]):
    """
    Görev varlığına özel veritabanı sorguları ve filtreleme metotları.
    """
    def __init__(self, session: Session):
        super().__init__(Task, session)

    def get_project_tasks(
        self,
        project_id: int,
        status: TaskStatus | None = None,
        priority: TaskPriority | None = None,
        skip: int = 0,
        limit: int = 100
    ) -> Sequence[Task]:
        """Proje altındaki görevleri isteğe bağlı durum ve öncelik filtresiyle getirir."""
        statement = select(Task).where(Task.project_id == project_id)
        if status:
            statement = statement.where(Task.status == status)
        if priority:
            statement = statement.where(Task.priority == priority)
        statement = statement.offset(skip).limit(limit)
        return self.session.exec(statement).all()

    def get_user_assigned_tasks(self, user_id: int) -> Sequence[Task]:
        """Belirli bir kullanıcıya atanan görevleri getirir."""
        statement = select(Task).where(Task.assignee_id == user_id)
        return self.session.exec(statement).all()

    def get_sprint_tasks(self, sprint_id: int) -> Sequence[Task]:
        """Belirli bir sprint altındaki görevleri getirir."""
        statement = select(Task).where(Task.sprint_id == sprint_id)
        return self.session.exec(statement).all()
