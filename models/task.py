from datetime import datetime
from sqlmodel import Field, SQLModel
from models.base import TimeStampedModel
from models.enums import TaskPriority, TaskStatus


class TaskBase(SQLModel):
    title: str = Field(index=True)
    description: str | None = None
    priority: TaskPriority = Field(default=TaskPriority.MEDIUM, index=True)
    status: TaskStatus = Field(default=TaskStatus.TODO, index=True)
    tags: str = Field(default="")
    deadline: datetime | None = None


class TaskCreate(TaskBase):
    project_id: int
    sprint_id: int | None = None
    assignee_id: int | None = None


class TaskRead(TaskBase):
    id: int
    project_id: int
    sprint_id: int | None
    creator_id: int
    assignee_id: int | None


class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    priority: TaskPriority | None = None
    status: TaskStatus | None = None
    tags: str | None = None
    deadline: datetime | None = None
    sprint_id: int | None = None
    assignee_id: int | None = None


class Task(TimeStampedModel, TaskBase, table=True):
    project_id: int = Field(foreign_key="project.id", index=True)
    sprint_id: int | None = Field(default=None, foreign_key="sprint.id", index=True)
    creator_id: int = Field(foreign_key="user.id", index=True)
    assignee_id: int | None = Field(default=None, foreign_key="user.id", index=True)

    def get_tags_set(self) -> set[str]:
        """
        Veri Yapısı: Hash Set (set)
        Virgülle ayrılmış etiketleri O(1) sürede kontrol edilebilen bir Python kümesine çevirir.
        """
        if not self.tags:
            return set()
        return {tag.strip().lower() for tag in self.tags.split(",") if tag.strip()}
