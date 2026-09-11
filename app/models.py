"""
Modelo de datos para las tareas, usando SQLAlchemy (ORM).

En la Fase 1, Task era una clase simple que solo vivía en memoria (una
lista de Python). Ahora Task hereda de `Base`: eso le dice a SQLAlchemy
"esta clase representa una tabla real en la base de datos". Cada
instancia de Task = una fila en la tabla `tasks`.
"""

from sqlalchemy import Boolean, Column, Integer, String

from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    done = Column(Boolean, default=False, nullable=False)

    def to_dict(self) -> dict:
        """Convierte la tarea a un diccionario, útil para responder en JSON."""
        return {"id": self.id, "title": self.title, "done": self.done}