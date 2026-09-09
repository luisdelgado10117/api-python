"""
API de gestión de tareas (To-Do API) - Fase 1.

Esta es una API muy sencilla hecha con Flask. Las tareas se guardan
en memoria (una lista), así que al reiniciar el servidor se pierden.
Eso está bien para esta fase: el objetivo es practicar las bases.

Endpoints disponibles:
    GET    /tasks        -> lista todas las tareas
    GET    /tasks/<id>   -> obtiene una tarea por su id
    POST   /tasks        -> crea una tarea nueva
    PUT    /tasks/<id>   -> actualiza una tarea existente
    DELETE /tasks/<id>   -> elimina una tarea
"""

from flask import Flask, jsonify, request

from app.models import Task

app = Flask(__name__)

# "Base de datos" en memoria: una lista de objetos Task.
tasks: list[Task] = []
next_id = 1  # Contador simple para asignar ids únicos.


@app.get("/tasks")
def get_tasks():
    """Devuelve todas las tareas."""
    return jsonify([task.to_dict() for task in tasks])


@app.get("/tasks/<int:task_id>")
def get_task(task_id: int):
    """Devuelve una tarea específica por su id."""
    task = _find_task(task_id)
    if task is None:
        return jsonify({"error": "Tarea no encontrada"}), 404
    return jsonify(task.to_dict())


@app.post("/tasks")
def create_task():
    """Crea una nueva tarea a partir de un JSON: {"title": "..."}"""
    global next_id

    data = request.get_json(silent=True) or {}
    title = data.get("title")

    if not title:
        return jsonify({"error": "El campo 'title' es obligatorio"}), 400

    new_task = Task(task_id=next_id, title=title)
    tasks.append(new_task)
    next_id += 1

    return jsonify(new_task.to_dict()), 201


@app.put("/tasks/<int:task_id>")
def update_task(task_id: int):
    """Actualiza el título y/o el estado 'done' de una tarea."""
    task = _find_task(task_id)
    if task is None:
        return jsonify({"error": "Tarea no encontrada"}), 404

    data = request.get_json(silent=True) or {}

    if "title" in data:
        task.title = data["title"]
    if "done" in data:
        task.done = bool(data["done"])

    return jsonify(task.to_dict())


@app.delete("/tasks/<int:task_id>")
def delete_task(task_id: int):
    """Elimina una tarea por su id."""
    task = _find_task(task_id)
    if task is None:
        return jsonify({"error": "Tarea no encontrada"}), 404

    tasks.remove(task)
    return jsonify({"message": "Tarea eliminada"}), 200


def _find_task(task_id: int) -> Task | None:
    """Función auxiliar para buscar una tarea por id en la lista."""
    for task in tasks:
        if task.id == task_id:
            return task
    return None


if __name__ == "__main__":
    app.run(debug=True)
