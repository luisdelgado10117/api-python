"""
API de gestión de tareas (To-Do API) - Fase 2.

Cambios respecto a la Fase 1:
    - Persistencia real con SQLite (antes las tareas se perdían al reiniciar)
    - Validaciones y manejo de errores más completo
    - Lógica de negocio separada en TaskManager (antes todo vivía en las rutas)

Endpoints disponibles:
    GET    /tasks        -> lista todas las tareas
    GET    /tasks/<id>   -> obtiene una tarea por su id
    POST   /tasks        -> crea una tarea nueva
    PUT    /tasks/<id>   -> actualiza una tarea existente
    DELETE /tasks/<id>   -> elimina una tarea
"""

from flask import Flask, jsonify, request

from app.database import SessionLocal, init_db
from app.errors import InvalidTaskDataError, TaskNotFoundError
from app.task_manager import TaskManager

app = Flask(__name__)

init_db()  # Crea la base de datos y sus tablas si todavía no existen


def get_task_manager() -> TaskManager:
    """Abre una sesión de base de datos nueva y crea el TaskManager asociado."""
    db = SessionLocal()
    return TaskManager(db)


@app.get("/tasks")
def get_tasks():
    manager = get_task_manager()
    tasks = manager.get_all()
    return jsonify([t.to_dict() for t in tasks])


@app.get("/tasks/<int:task_id>")
def get_task(task_id: int):
    manager = get_task_manager()
    try:
        task = manager.get_by_id(task_id)
        return jsonify(task.to_dict())
    except TaskNotFoundError as e:
        return jsonify({"error": str(e)}), 404


@app.post("/tasks")
def create_task():
    manager = get_task_manager()
    data = request.get_json(silent=True) or {}

    try:
        task = manager.create(title=data.get("title"))
        return jsonify(task.to_dict()), 201
    except InvalidTaskDataError as e:
        return jsonify({"error": str(e)}), 400


@app.put("/tasks/<int:task_id>")
def update_task(task_id: int):
    manager = get_task_manager()
    data = request.get_json(silent=True) or {}

    try:
        task = manager.update(task_id, title=data.get("title"), done=data.get("done"))
        return jsonify(task.to_dict())
    except TaskNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except InvalidTaskDataError as e:
        return jsonify({"error": str(e)}), 400


@app.delete("/tasks/<int:task_id>")
def delete_task(task_id: int):
    manager = get_task_manager()
    try:
        manager.delete(task_id)
        return jsonify({"message": "Tarea eliminada"}), 200
    except TaskNotFoundError as e:
        return jsonify({"error": str(e)}), 404


if __name__ == "__main__":
    app.run(debug=True)