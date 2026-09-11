"""
Capa de lógica de negocio: TaskManager.

Esta clase es responsable de TODAS las reglas relacionadas con tareas:
crearlas, buscarlas, actualizarlas, eliminarlas y validar sus datos.

¿Por qué separar esto de las rutas de Flask (en main.py)? Porque así las
rutas solo se encargan de "traducir" HTTP <-> Python (leer el request,
devolver JSON), y TaskManager se encarga de la lógica real. Esto es más
fácil de leer, de probar, y el día de mañana de reutilizar (por ejemplo,
si agregas un comando de consola además de la API web).
"""

from sqlalchemy.orm import Session

from app.errors import InvalidTaskDataError, TaskNotFoundError
from app.models import Task


class TaskManager:
    """Encapsula las operaciones CRUD sobre tareas, usando una sesión de BD."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Task]:
        return self.db.query(Task).all()

    def get_by_id(self, task_id: int) -> Task:
        task = self.db.query(Task).filter(Task.id == task_id).first()
        if task is None:
            raise TaskNotFoundError(f"No existe una tarea con id {task_id}")
        return task

    def create(self, title) -> Task:
        self._validate_title(title)

        task = Task(title=title.strip(), done=False)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)  # recarga el objeto para traer el id generado
        return task

    def update(self, task_id: int, title=None, done=None) -> Task:
        task = self.get_by_id(task_id)  # lanza TaskNotFoundError si no existe

        if title is not None:
            self._validate_title(title)
            task.title = title.strip()

        if done is not None:
            if not isinstance(done, bool):
                raise InvalidTaskDataError(
                    "El campo 'done' debe ser verdadero o falso (true/false)"
                )
            task.done = done

        self.db.commit()
        self.db.refresh(task)
        return task

    def delete(self, task_id: int) -> None:
        task = self.get_by_id(task_id)  # lanza TaskNotFoundError si no existe
        self.db.delete(task)
        self.db.commit()

    @staticmethod
    def _validate_title(title) -> None:
        """Reglas para que un título sea válido: debe ser texto y no estar vacío."""
        if not isinstance(title, str) or not title.strip():
            raise InvalidTaskDataError(
                "El campo 'title' es obligatorio y debe ser texto no vacío"
            )
