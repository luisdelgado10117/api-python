"""
Pruebas básicas para la To-Do API.

Corre estas pruebas con:
    pytest

Aprovecha para practicar: leer, entender y (más adelante) escribir
tus propias pruebas cuando agregues nuevos endpoints.
"""

import pytest

from app.main import app, tasks


@pytest.fixture
def client():
    """Crea un cliente de pruebas de Flask y limpia la lista de tareas."""
    tasks.clear()
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


def test_update_task(client):
    create_response = client.post("/tasks", json={"title": "Tarea original"})
    task_id = create_response.get_json()["id"]

    update_response = client.put(f"/tasks/{task_id}", json={"done": True})
    assert update_response.status_code == 200
    assert update_response.get_json()["done"] is True


def test_delete_task(client):
    create_response = client.post("/tasks", json={"title": "Tarea a borrar"})
    task_id = create_response.get_json()["id"]

    delete_response = client.delete(f"/tasks/{task_id}")
    assert delete_response.status_code == 200

    get_response = client.get(f"/tasks/{task_id}")
    assert get_response.status_code == 404
