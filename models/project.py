from datetime import datetime
from sqlmodel import Field, SQLModel
from models.base import TimeStampedModel


class ProjectBase(SQLModel):
    name: str = Field(index=True)
    key: str = Field(unique=True, index=True, min_length=2, max_length=10)
    description: str | None = None


class ProjectCreate(ProjectBase):
    pass


class ProjectRead(ProjectBase):
    id: int
    owner_id: int


class ProjectUpdate(SQLModel):
    name: str | None = None
    description: str | None = None


class Project(TimeStampedModel, ProjectBase, table=True):
    owner_id: int = Field(foreign_key="user.id", index=True)


class SprintBase(SQLModel):
    title: str
    project_id: int = Field(foreign_key="project.id", index=True)
    start_date: datetime
    end_date: datetime
    is_active: bool = Field(default=False)


class SprintCreate(SprintBase):
    pass


class SprintRead(SprintBase):
    id: int


class SprintUpdate(SQLModel):
    title: str | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    is_active: bool | None = None


class Sprint(TimeStampedModel, SprintBase, table=True):
    pass
