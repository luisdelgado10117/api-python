"""
Pruebas para la To-Do API (Fase 3: con autenticación).

Corre estas pruebas con:
    python -m pytest
"""

import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest

from app.database import SessionLocal, init_db
from app.main import app
from app.models import Task, User


@pytest.fixture
def client():
    """Prepara una base de datos limpia y un cliente de pruebas para cada test."""
    init_db()

    db = SessionLocal()
    db.query(Task).delete()
    db.query(User).delete()
    db.commit()
    db.close()

    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client):
    """Registra un usuario, hace login, y devuelve los headers listos para usar."""
    client.post("/register", json={"username": "ana", "password": "1234"})
    response = client.post("/login", json={"username": "ana", "password": "1234"})
    token = response.get_json()["token"]
    return {"Authorization": f"Bearer {token}"}


# --- Registro y login ---


def test_register(client):
    response = client.post("/register", json={"username": "carlos", "password": "abcd"})
    assert response.status_code == 201
    assert response.get_json()["username"] == "carlos"


def test_register_username_duplicado(client):
    client.post("/register", json={"username": "carlos", "password": "abcd"})
    response = client.post("/register", json={"username": "carlos", "password": "otra"})
    assert response.status_code == 409


def test_register_password_muy_corta(client):
    response = client.post("/register", json={"username": "carlos", "password": "12"})
    assert response.status_code == 400


def test_login_correcto(client):
    client.post("/register", json={"username": "ana", "password": "1234"})
    response = client.post("/login", json={"username": "ana", "password": "1234"})
    assert response.status_code == 200
    assert "token" in response.get_json()


def test_login_password_incorrecta(client):
    client.post("/register", json={"username": "ana", "password": "1234"})
    response = client.post("/login", json={"username": "ana", "password": "mala"})
    assert response.status_code == 401


def test_login_usuario_no_existe(client):
    response = client.post("/login", json={"username": "fantasma", "password": "1234"})
    assert response.status_code == 401


# --- Protección de rutas de tareas ---


def test_tasks_sin_token(client):
    """Sin header Authorization, debe rechazar la petición."""
    response = client.get("/tasks")
    assert response.status_code == 401


def test_tasks_con_token_invalido(client):
    response = client.get("/tasks", headers={"Authorization": "Bearer token-falso"})
    assert response.status_code == 401


# --- CRUD de tareas (ya autenticado) ---


def test_get_tasks_empty(client, auth_headers):
    response = client.get("/tasks", headers=auth_headers)
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_task(client, auth_headers):
    response = client.post(
        "/tasks", json={"title": "Aprender JWT"}, headers=auth_headers
    )
    assert response.status_code == 201
    assert response.get_json()["title"] == "Aprender JWT"


def test_create_task_sin_titulo(client, auth_headers):
    response = client.post("/tasks", json={}, headers=auth_headers)
    assert response.status_code == 400


def test_update_task(client, auth_headers):
    create_response = client.post(
        "/tasks", json={"title": "Tarea original"}, headers=auth_headers
    )
    task_id = create_response.get_json()["id"]

    update_response = client.put(
        f"/tasks/{task_id}", json={"done": True}, headers=auth_headers
    )
    assert update_response.status_code == 200
    assert update_response.get_json()["done"] is True


def test_delete_task(client, auth_headers):
    create_response = client.post(
        "/tasks", json={"title": "Tarea a borrar"}, headers=auth_headers
    )
    task_id = create_response.get_json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert delete_response.status_code == 200


# --- Aislamiento entre usuarios (lo más importante de esta fase) ---


def test_usuarios_no_ven_tareas_de_otros(client):
    # Usuario A crea una tarea
    client.post("/register", json={"username": "usuarioA", "password": "1234"})
    login_a = client.post("/login", json={"username": "usuarioA", "password": "1234"})
    headers_a = {"Authorization": f"Bearer {login_a.get_json()['token']}"}
    client.post("/tasks", json={"title": "Tarea de A"}, headers=headers_a)

    # Usuario B se registra y consulta sus propias tareas
    client.post("/register", json={"username": "usuarioB", "password": "1234"})
    login_b = client.post("/login", json={"username": "usuarioB", "password": "1234"})
    headers_b = {"Authorization": f"Bearer {login_b.get_json()['token']}"}
    response_b = client.get("/tasks", headers=headers_b)

    # B no debe ver la tarea de A
    assert response_b.get_json() == []


def test_usuario_no_puede_editar_tarea_de_otro(client):
    client.post("/register", json={"username": "usuarioA", "password": "1234"})
    login_a = client.post("/login", json={"username": "usuarioA", "password": "1234"})
    headers_a = {"Authorization": f"Bearer {login_a.get_json()['token']}"}
    create_response = client.post(
        "/tasks", json={"title": "Tarea de A"}, headers=headers_a
    )
    task_id = create_response.get_json()["id"]

    client.post("/register", json={"username": "usuarioB", "password": "1234"})
    login_b = client.post("/login", json={"username": "usuarioB", "password": "1234"})
    headers_b = {"Authorization": f"Bearer {login_b.get_json()['token']}"}

    response = client.put(f"/tasks/{task_id}", json={"done": True}, headers=headers_b)
    assert response.status_code == 404  # para B, esa tarea "no existe"
