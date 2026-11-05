import heapq
from datetime import datetime, timezone
from typing import Sequence
from sqlmodel import Session
from models.task import Task, TaskCreate, TaskUpdate
from models.enums import TaskPriority, TaskStatus
from repositories.task_repository import TaskRepository
from repositories.project_repository import ProjectRepository
from repositories.user_repository import UserRepository


class TaskService:
    """
    İş mantığı (Business Logic), Veri Yapıları (Heap, Set) ve ACID yönetimi.
    
    SOLID - Single Responsibility (S):
        Yalnızca görevlerle ilgili iş kurallarını işletir; ham SQL veya HTTP detayları içermez.
    """
    PRIORITY_WEIGHTS = {
        TaskPriority.CRITICAL: 1,
        TaskPriority.HIGH: 2,
        TaskPriority.MEDIUM: 3,
        TaskPriority.LOW: 4,
    }

    # State Pattern: Geçerli durum geçiş haritası
    ALLOWED_TRANSITIONS = {
        TaskStatus.TODO: {TaskStatus.IN_PROGRESS},
        TaskStatus.IN_PROGRESS: {TaskStatus.IN_REVIEW, TaskStatus.TODO},
        TaskStatus.IN_REVIEW: {TaskStatus.DONE, TaskStatus.IN_PROGRESS},
        TaskStatus.DONE: {TaskStatus.TODO},  # Yeniden açma
    }

    def __init__(self, session: Session):
        self.session = session
        self.task_repo = TaskRepository(session)
        self.project_repo = ProjectRepository(session)
        self.user_repo = UserRepository(session)

    def create_task(self, task_in: TaskCreate, creator_id: int) -> Task:
        """Yeni bir görev oluşturur. Proje ve atanan kullanıcı geçerliliğini denetler."""
        project = self.project_repo.get(task_in.project_id)
        if not project:
            raise ValueError(f"Proje bulunamadı: ID {task_in.project_id}")

        if task_in.assignee_id:
            assignee = self.user_repo.get(task_in.assignee_id)
            if not assignee or not assignee.is_active:
                raise ValueError("Atanan kullanıcı bulunamadı veya pasif durumda.")

        task_data = task_in.model_dump()
        task = Task(**task_data, creator_id=creator_id)
        return self.task_repo.create(task)

    def change_status(self, task_id: int, new_status: TaskStatus) -> Task:
        """
        State Machine: Geçerli durum geçişlerini denetler.
        ACID Atomicity: Kural dışı geçişlerde hata fırlatır ve değişiklik yapılmaz.
        """
        task = self.task_repo.get(task_id)
        if not task:
            raise ValueError(f"Görev bulunamadı: ID {task_id}")

        allowed = self.ALLOWED_TRANSITIONS.get(task.status, set())
        if new_status not in allowed:
            raise ValueError(f"Geçersiz durum geçişi: '{task.status.value}' durumundan '{new_status.value}' durumuna geçilemez.")

        task.status = new_status
        task.updated_at = datetime.now(timezone.utc)
        return self.task_repo.update(task, {"status": new_status, "updated_at": task.updated_at})

    def get_most_urgent_tasks(self, project_id: int, top_n: int = 5) -> list[Task]:
        """
        Veri Yapısı: Priority Queue / Min-Heap (heapq)
        Görevleri öncelik puanı ve deadline'a göre sıralayıp en acil olanları O(1) hızla döndürür.
        """
        tasks = self.task_repo.get_project_tasks(project_id)
        if not tasks:
            return []

        # Heap elemanları: (oncelik_puani, deadline_timestamp, task_id, task)
        heap = []
        for task in tasks:
            if task.status == TaskStatus.DONE:
                continue  # Tamamlananlar acil kuyruğuna girmez
            weight = self.PRIORITY_WEIGHTS.get(task.priority, 5)
            deadline_ts = task.deadline.timestamp() if task.deadline else float("inf")
            heapq.heappush(heap, (weight, deadline_ts, task.id, task))

        # En acil N görevi heap'ten çıkar
        urgent_tasks = []
        for _ in range(min(top_n, len(heap))):
            urgent_tasks.append(heapq.heappop(heap)[3])
        return urgent_tasks

    def filter_by_tags(self, project_id: int, required_tags: set[str]) -> list[Task]:
        """
        Veri Yapısı: Hash Set (set)
        İstenen etiket kümesine sahip olan görevleri O(1) küme kesişimi ile süzer.
        """
        tasks = self.task_repo.get_project_tasks(project_id)
        matching = []
        for task in tasks:
            task_tags = task.get_tags_set()
            if required_tags.issubset(task_tags):
                matching.append(task)
        return matching
