from fastapi.testclient import TestClient
from models.user import User
from models.enums import UserRole
from services.auth_service import AuthService


def test_api_auth_register_and_login(client: TestClient):
    """Kullanıcı kaydı ve ardından giriş yaparak JWT token almayı test eder."""
    # 1. Register
    reg_res = client.post("/api/v1/auth/register", json={
        "email": "api_user@taskforge.dev",
        "full_name": "API User",
        "role": "developer",
        "password": "Password123!",
        "is_active": True
    })
    assert reg_res.status_code == 201
    assert reg_res.json()["email"] == "api_user@taskforge.dev"

    # 2. Login
    login_res = client.post("/api/v1/auth/login", data={
        "username": "api_user@taskforge.dev",
        "password": "Password123!"
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert token is not None

    # 3. /me
    me_res = client.get("/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "api_user@taskforge.dev"


def test_api_projects_and_rbac(client: TestClient, admin_headers: dict[str, str]):
    """Rol Tabanlı Erişim Kontrolü (RBAC): Admin proje oluşturabilir."""
    # Admin proje oluşturur -> 201
    create_res = client.post("/api/v1/projects/", json={
        "name": "E2E Proje",
        "key": "E2E",
        "description": "Entegrasyon testi projesi"
    }, headers=admin_headers)
    assert create_res.status_code == 201
    project_id = create_res.json()["id"]

    # Projeleri listele -> 200
    list_res = client.get("/api/v1/projects/", headers=admin_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1


def test_api_tasks_and_urgent_heap(client: TestClient, admin_headers: dict[str, str]):
    """Görev oluşturma ve Min-Heap endpoint'ini test eder."""
    # Proje aç
    proj_res = client.post("/api/v1/projects/", json={
        "name": "Görev Test Projesi",
        "key": "GT",
        "description": "Görevler için"
    }, headers=admin_headers)
    proj_id = proj_res.json()["id"]

    # Görev ekle
    task_res = client.post("/api/v1/tasks/", json={
        "title": "API Üzerinden Görev",
        "priority": "critical",
        "status": "todo",
        "tags": "api,e2e",
        "project_id": proj_id
    }, headers=admin_headers)
    assert task_res.status_code == 201
    task_id = task_res.json()["id"]

    # Acil görevleri Min-Heap endpoint'inden çek
    urgent_res = client.get(f"/api/v1/tasks/project/{proj_id}/urgent", headers=admin_headers)
    assert urgent_res.status_code == 200
    assert len(urgent_res.json()) >= 1
    assert urgent_res.json()[0]["id"] == task_id

    # Durum güncelle (TODO -> IN_PROGRESS)
    patch_res = client.patch(
        f"/api/v1/tasks/{task_id}/status?new_status=in_progress",
        headers=admin_headers
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "in_progress"
