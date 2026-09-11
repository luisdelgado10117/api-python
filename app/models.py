"""
Modelos de datos (tablas de la base de datos), usando SQLAlchemy (ORM).

Fase 3: agregamos User. Cada Task ahora pertenece a un User (relación
"uno a muchos": un usuario puede tener muchas tareas).
"""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)

    # Da acceso a user.tasks -> lista de tareas de ese usuario
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    done = Column(Boolean, default=False, nullable=False)

    # Clave foránea: guarda a QUIÉN pertenece esta tarea
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="tasks")

    def to_dict(self) -> dict:
        """Convierte la tarea a un diccionario. No incluimos user_id a propósito:
        el dueño de la tarea ya se sabe por quién hizo la petición (su token)."""
        return {"id": self.id, "title": self.title, "done": self.done}