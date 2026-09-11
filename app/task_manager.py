"""
Capa de lógica de negocio: TaskManager.

Fase 3: cada método ahora recibe user_id, y SOLO opera sobre las tareas
de ese usuario. Esto es lo que hace que cada quien vea únicamente sus
propias tareas.
"""

from sqlalchemy.orm import Session

from app.errors import InvalidTaskDataError, TaskNotFoundError
from app.models import Task


class TaskManager:
    """Encapsula las operaciones CRUD sobre tareas, siempre acotadas a un usuario."""

    def __init__(self, db: Session):
        self.db = db

    def get_all(self, user_id: int) -> list[Task]:
        return self.db.query(Task).filter(Task.user_id == user_id).all()

    def get_by_id(self, task_id: int, user_id: int) -> Task:
        task = (
            self.db.query(Task)
            .filter(Task.id == task_id, Task.user_id == user_id)
            .first()
        )
        if task is None:
            # A propósito no distinguimos "no existe" de "es de otro usuario":
            # en ambos casos, para este usuario, esa tarea "no existe".
            raise TaskNotFoundError(f"No existe una tarea con id {task_id}")
        return task

    def create(self, title, user_id: int) -> Task:
        self._validate_title(title)

        task = Task(title=title.strip(), done=False, user_id=user_id)
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task

    def update(self, task_id: int, user_id: int, title=None, done=None) -> Task:
        task = self.get_by_id(task_id, user_id)

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

    def delete(self, task_id: int, user_id: int) -> None:
        task = self.get_by_id(task_id, user_id)
        self.db.delete(task)
        self.db.commit()

    @staticmethod
    def _validate_title(title) -> None:
        if not isinstance(title, str) or not title.strip():
            raise InvalidTaskDataError(
                "El campo 'title' es obligatorio y debe ser texto no vacío"
            )