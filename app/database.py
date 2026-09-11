"""
Configuración de la base de datos.

Usamos SQLite (una base de datos que vive en un solo archivo, no necesita
instalar ningún servidor) junto con SQLAlchemy, que es un ORM: nos deja
trabajar con la base de datos usando clases y objetos de Python, en vez
de escribir SQL a mano.

La variable de entorno DATABASE_URL permite cambiar de base de datos sin
tocar el código (por ejemplo, en los tests usamos una base en memoria).
"""

import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///tasks.db")

connect_args = {"check_same_thread": False}
engine_kwargs = {"connect_args": connect_args}

# Una base de datos ":memory:" se borra al cerrar la conexión, así que en
# ese caso forzamos a SQLAlchemy a reutilizar SIEMPRE la misma conexión
# (StaticPool), para que todas las sesiones "vean" los mismos datos.
if DATABASE_URL == "sqlite:///:memory:":
    engine_kwargs["poolclass"] = StaticPool

engine = create_engine(DATABASE_URL, **engine_kwargs)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()


def init_db() -> None:
    """Crea las tablas en la base de datos si todavía no existen."""
    Base.metadata.create_all(bind=engine)
