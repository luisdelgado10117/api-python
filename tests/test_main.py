"""
Pruebas para la To-Do API (Fase 2).

IMPORTANTE: configuramos DATABASE_URL como base en memoria ANTES de
importar cualquier cosa de app/, para que las pruebas nunca toquen tu
archivo real tasks.db.

Corre estas pruebas con:
    python -m pytest
"""

import os

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

import pytest

from app.database import SessionLocal, init_db
from app.main import app
from app.models import Task


@pytest.fixture
def client():
    """Prepara una base de datos limpia y un cliente de pruebas para cada test."""
    init_db()

    # Limpia cualquier dato que haya quedado de un test anterior.
    db = SessionLocal()
    db.query(Task).delete()
    db.commit()
    db.close()

    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_get_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.get_json() == []


def test_create_task(client):
    response = client.post("/tasks", json={"title": "Aprender Flask"})
    assert response.status_code == 201

    data = response.get_json()
    assert data["title"] == "Aprender Flask"
    assert data["done"] is False


def test_create_task_sin_titulo(client):
    response = client.post("/tasks", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()


def test_create_task_titulo_vacio(client):
    """El título no puede ser solo espacios en blanco."""
    response = client.post("/tasks", json={"title": "   "})
    assert response.status_code == 400


def test_get_task_no_encontrada(client):
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert "error" in response.get_json()


def test_update_task(client):
    create_response = client.post("/tasks", json={"title": "Tarea original"})
    task_id = create_response.get_json()["id"]

    update_response = client.put(f"/tasks/{task_id}", json={"done": True})
    assert update_response.status_code == 200
    assert update_response.get_json()["done"] is True


def test_update_task_done_invalido(client):
    """El campo 'done' debe ser booleano, no cualquier otro tipo."""
    create_response = client.post("/tasks", json={"title": "Tarea"})
    task_id = create_response.get_json()["id"]

    update_response = client.put(f"/tasks/{task_id}", json={"done": "si"})
    assert update_response.status_code == 400


def test_delete_task(client):
    create_response = client.post("/tasks", json={"title": "Tarea a borrar"})
    task_id = create_response.get_json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404


def test_delete_task_no_encontrada(client):
    response = client.delete("/tasks/999")
    assert response.status_code == 404


def test_persistencia_entre_requests(client):
    """Verifica que las tareas creadas realmente persisten (a diferencia de la Fase 1)."""
    client.post("/tasks", json={"title": "Tarea 1"})
    client.post("/tasks", json={"title": "Tarea 2"})

    response = client.get("/tasks")
    data = response.get_json()
    assert len(data) == 2