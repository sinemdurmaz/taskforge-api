from datetime import datetime, timezone, timedelta
import pytest
from sqlmodel import Session
from models import (
    User, UserCreate, UserRole, Project, TaskCreate, TaskPriority, TaskStatus
)
from repositories import ProjectRepository, UserRepository
from services import AuthService, TaskService


def test_auth_service_register_and_verify(session: Session):
    """AuthService kullanıcı kaydı, Argon2 parola doğrulaması ve JWT üretimini test eder."""
    auth_service = AuthService(session)
    user_in = UserCreate(
        email="developer@taskforge.dev",
        full_name="Junior Dev",
        role=UserRole.DEVELOPER,
        password="SecurePassword456!",
        is_active=True
    )
    user = auth_service.register_user(user_in)
    assert user.id is not None
    assert user.email == "developer@taskforge.dev"
    assert auth_service.verify_password("SecurePassword456!", user.hashed_password)
    assert not auth_service.verify_password("WrongPassword", user.hashed_password)

    # Aynı e-posta ile ikinci kayıt hata vermeli
    with pytest.raises(ValueError, match="Bu e-posta adresi zaten kullanımda"):
        auth_service.register_user(user_in)


def test_task_service_state_machine(session: Session, admin_user: User):
    """TaskService durum makinesi: TODO -> IN_PROGRESS geçerli, TODO -> DONE geçersiz."""
    project_repo = ProjectRepository(session)
    project = project_repo.create(Project(name="Sprint 1", key="S1", owner_id=admin_user.id))

    task_service = TaskService(session)
    task = task_service.create_task(TaskCreate(
        title="Durum Test Görevi",
        priority=TaskPriority.HIGH,
        project_id=project.id
    ), creator_id=admin_user.id)
    assert task.status == TaskStatus.TODO

    # Geçersiz geçiş: TODO -> DONE
    with pytest.raises(ValueError, match="Geçersiz durum geçişi"):
        task_service.change_status(task.id, TaskStatus.DONE)

    # Geçerli geçiş: TODO -> IN_PROGRESS
    updated = task_service.change_status(task.id, TaskStatus.IN_PROGRESS)
    assert updated.status == TaskStatus.IN_PROGRESS


def test_task_service_min_heap_priority_queue(session: Session, admin_user: User):
    """Min-Heap (heapq) veri yapısının en acil görevi en tepeye yerleştirdiğini test eder."""
    project_repo = ProjectRepository(session)
    project = project_repo.create(Project(name="Heap Projesi", key="HP", owner_id=admin_user.id))

    task_service = TaskService(session)

    # Düşük öncelikli görev
    t_low = task_service.create_task(TaskCreate(
        title="Düşük Öncelik",
        priority=TaskPriority.LOW,
        project_id=project.id
    ), creator_id=admin_user.id)

    # Kritik öncelikli görev
    t_critical = task_service.create_task(TaskCreate(
        title="Kritik Yangın",
        priority=TaskPriority.CRITICAL,
        project_id=project.id,
        deadline=datetime.now(timezone.utc) + timedelta(hours=1)
    ), creator_id=admin_user.id)

    # Yüksek öncelikli görev
    t_high = task_service.create_task(TaskCreate(
        title="Yüksek Öncelik",
        priority=TaskPriority.HIGH,
        project_id=project.id,
        deadline=datetime.now(timezone.utc) + timedelta(days=1)
    ), creator_id=admin_user.id)

    urgent_tasks = task_service.get_most_urgent_tasks(project.id, top_n=3)
    assert len(urgent_tasks) == 3
    # Min-Heap sırası: CRITICAL (1) -> HIGH (2) -> LOW (4)
    assert urgent_tasks[0].id == t_critical.id
    assert urgent_tasks[1].id == t_high.id
    assert urgent_tasks[2].id == t_low.id


def test_task_service_hash_set_filtering(session: Session, admin_user: User):
    """Hash Set veri yapısı ile O(1) alt küme etiket aramasını test eder."""
    project_repo = ProjectRepository(session)
    project = project_repo.create(Project(name="Set Projesi", key="SP", owner_id=admin_user.id))

    task_service = TaskService(session)
    t1 = task_service.create_task(TaskCreate(
        title="Backend API",
        tags="backend, fastapi, python",
        project_id=project.id
    ), creator_id=admin_user.id)

    t2 = task_service.create_task(TaskCreate(
        title="Frontend UI",
        tags="frontend, react",
        project_id=project.id
    ), creator_id=admin_user.id)

    matched = task_service.filter_by_tags(project.id, {"backend", "python"})
    assert len(matched) == 1
    assert matched[0].id == t1.id
