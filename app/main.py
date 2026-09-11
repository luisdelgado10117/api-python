"""
API de gestión de tareas (To-Do API) - Fase 3.

Cambios respecto a la Fase 2:
    - Sistema de usuarios: /register y /login
    - Las tareas ahora pertenecen a un usuario (cada quien ve solo las suyas)
    - Un decorador (@require_auth) protege las rutas de tareas

Endpoints disponibles:
    POST   /register             -> crea una cuenta nueva
    POST   /login                -> devuelve un token de acceso

    GET    /tasks                -> lista MIS tareas (requiere token)
    GET    /tasks/<id>            -> obtiene una de MIS tareas (requiere token)
    POST   /tasks                -> crea una tarea para MÍ (requiere token)
    PUT    /tasks/<id>            -> actualiza una de MIS tareas (requiere token)
    DELETE /tasks/<id>            -> elimina una de MIS tareas (requiere token)
"""

from functools import wraps

import jwt
from flask import Flask, g, jsonify, request

from app.auth import decode_token
from app.database import SessionLocal, init_db
from app.errors import (
    InvalidCredentialsError,
    InvalidTaskDataError,
    InvalidUserDataError,
    TaskNotFoundError,
    UserAlreadyExistsError,
)
from app.task_manager import TaskManager
from app.user_manager import UserManager

app = Flask(__name__)

init_db()


def get_task_manager() -> TaskManager:
    return TaskManager(SessionLocal())


def get_user_manager() -> UserManager:
    return UserManager(SessionLocal())


def require_auth(view_function):
    """Decorador: exige un token válido antes de ejecutar la ruta.

    Un decorador es una función que "envuelve" a otra función para
    agregarle comportamiento extra sin modificar su código. Aquí,
    antes de correr la ruta real (get_tasks, create_task, etc.),
    revisamos que venga un token válido en el header Authorization.
    Si es válido, guardamos el user_id en `g` (un espacio de Flask
    para datos de la petición actual) para que la ruta lo use después.
    """

    @wraps(view_function)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")

        if not auth_header.startswith("Bearer "):
            return jsonify(
                {"error": "Falta el token (header Authorization: Bearer <token>)"}
            ), 401

        token = auth_header.removeprefix("Bearer ").strip()

        try:
            g.user_id = decode_token(token)
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "El token expiró, inicia sesión de nuevo"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Token inválido"}), 401

        return view_function(*args, **kwargs)

    return wrapper


# --- Autenticación ---


@app.post("/register")
def register():
    manager = get_user_manager()
    data = request.get_json(silent=True) or {}

    try:
        user = manager.register(username=data.get("username"), password=data.get("password"))
        return jsonify({"id": user.id, "username": user.username}), 201
    except InvalidUserDataError as e:
        return jsonify({"error": str(e)}), 400
    except UserAlreadyExistsError as e:
        return jsonify({"error": str(e)}), 409


@app.post("/login")
def login():
    manager = get_user_manager()
    data = request.get_json(silent=True) or {}

    try:
        token = manager.login(username=data.get("username"), password=data.get("password"))
        return jsonify({"token": token})
    except InvalidUserDataError as e:
        return jsonify({"error": str(e)}), 400
    except InvalidCredentialsError as e:
        return jsonify({"error": str(e)}), 401


# --- Tareas (todas requieren estar autenticado) ---


@app.get("/tasks")
@require_auth
def get_tasks():
    manager = get_task_manager()
    tasks = manager.get_all(g.user_id)
    return jsonify([t.to_dict() for t in tasks])


@app.get("/tasks/<int:task_id>")
@require_auth
def get_task(task_id: int):
    manager = get_task_manager()
    try:
        task = manager.get_by_id(task_id, g.user_id)
        return jsonify(task.to_dict())
    except TaskNotFoundError as e:
        return jsonify({"error": str(e)}), 404


@app.post("/tasks")
@require_auth
def create_task():
    manager = get_task_manager()
    data = request.get_json(silent=True) or {}

    try:
        task = manager.create(title=data.get("title"), user_id=g.user_id)
        return jsonify(task.to_dict()), 201
    except InvalidTaskDataError as e:
        return jsonify({"error": str(e)}), 400


@app.put("/tasks/<int:task_id>")
@require_auth
def update_task(task_id: int):
    manager = get_task_manager()
    data = request.get_json(silent=True) or {}

    try:
        task = manager.update(
            task_id, g.user_id, title=data.get("title"), done=data.get("done")
        )
        return jsonify(task.to_dict())
    except TaskNotFoundError as e:
        return jsonify({"error": str(e)}), 404
    except InvalidTaskDataError as e:
        return jsonify({"error": str(e)}), 400


@app.delete("/tasks/<int:task_id>")
@require_auth
def delete_task(task_id: int):
    manager = get_task_manager()
    try:
        manager.delete(task_id, g.user_id)
        return jsonify({"message": "Tarea eliminada"}), 200
    except TaskNotFoundError as e:
        return jsonify({"error": str(e)}), 404


if __name__ == "__main__":
    app.run(debug=True)