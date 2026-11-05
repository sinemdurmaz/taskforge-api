from enum import Enum


class UserRole(str, Enum):
    """Kullanıcı yetki rolleri."""
    ADMIN = "admin"
    MANAGER = "manager"
    DEVELOPER = "developer"


class TaskPriority(str, Enum):
    """Görev öncelik dereceleri (Heap / Priority Queue ile sıralanacak)."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TaskStatus(str, Enum):
    """Görev yaşam döngüsü durumları."""
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    DONE = "done"
