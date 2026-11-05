from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session
from core.database import get_session
from models.project import Project, ProjectCreate, ProjectRead
from models.user import User
from models.enums import UserRole
from repositories.project_repository import ProjectRepository
from api.deps import get_current_user, require_role

router = APIRouter(prefix="/projects", tags=["Projeler"])


@router.post(
    "/",
    response_model=ProjectRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))]
)
def create_project(
    project_in: ProjectCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Yeni proje oluşturur (Yalnızca Admin ve Manager)."""
    project_repo = ProjectRepository(session)
    existing = project_repo.get_by_key(project_in.key)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"'{project_in.key}' anahtarı ile başka bir proje zaten mevcut."
        )
    project = Project(**project_in.model_dump(), owner_id=current_user.id)
    return project_repo.create(project)


@router.get("/", response_model=Sequence[ProjectRead])
def list_projects(
    session: Annotated[Session, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Mevcut projeleri listeler."""
    project_repo = ProjectRepository(session)
    return project_repo.get_all()
