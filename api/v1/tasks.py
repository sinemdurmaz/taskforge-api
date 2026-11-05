from typing import Annotated, Sequence
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session
from core.database import get_session
from models.task import Task, TaskCreate, TaskRead
from models.enums import TaskPriority, TaskStatus
from models.user import User
from services.task_service import TaskService
from api.deps import get_current_user

router = APIRouter(prefix="/tasks", tags=["Görevler"])


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(
    task_in: TaskCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """Yeni bir görev oluşturur."""
    task_service = TaskService(session)
    try:
        return task_service.create_task(task_in, creator_id=current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.patch("/{task_id}/status", response_model=TaskRead)
def update_task_status(
    task_id: int,
    new_status: TaskStatus,
    current_user: Annotated[User, Depends(get_current_user)],
    session: Annotated[Session, Depends(get_session)]
):
    """State Machine: Görev durumunu geçerli kurallar dahilinde günceller."""
    task_service = TaskService(session)
    try:
        return task_service.change_status(task_id, new_status)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/project/{project_id}/urgent", response_model=Sequence[TaskRead])
def get_urgent_tasks(
    project_id: int,
    top_n: int = Query(default=5, ge=1, le=20),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    session: Annotated[Session, Depends(get_session)] = None
):
    """Veri Yapısı (Min-Heap): En acil görevleri O(1) hızla çeker."""
    task_service = TaskService(session)
    return task_service.get_most_urgent_tasks(project_id, top_n=top_n)


@router.get("/project/{project_id}/by-tags", response_model=Sequence[TaskRead])
def filter_tasks_by_tags(
    project_id: int,
    tags: str = Query(..., description="Virgülle ayrılmış aranan etiketler (örn: backend,bug)"),
    current_user: Annotated[User, Depends(get_current_user)] = None,
    session: Annotated[Session, Depends(get_session)] = None
):
    """Veri Yapısı (Hash Set): İstenen etiketlerin tamamını içeren görevleri süzer."""
    task_service = TaskService(session)
    required_tags = {t.strip().lower() for t in tags.split(",") if t.strip()}
    return task_service.filter_by_tags(project_id, required_tags)
