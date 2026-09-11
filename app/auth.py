"""
Utilidades de autenticación: hash de contraseñas y tokens JWT.

DOS IDEAS CLAVE en este archivo:

1. NUNCA guardamos la contraseña real en la base de datos. Guardamos un
   "hash" (una huella digital de la contraseña, que no se puede revertir).
   Así, si alguien roba la base de datos, no obtiene las contraseñas reales.

2. Un JWT (JSON Web Token) es como un "gafete de acceso temporal": el
   usuario hace login UNA vez, le damos un token, y ese token demuestra
   quién es en cada petición futura (sin tener que mandar su contraseña
   de nuevo cada vez).
"""

import datetime
import os

import jwt
from werkzeug.security import (
    check_password_hash,
    generate_password_hash,
)  # En un proyecto real, esta clave NUNCA debe estar escrita en el código;

# se configura como variable de entorno en el servidor de producción.
SECRET_KEY = os.environ.get("SECRET_KEY", "clave-secreta-de-desarrollo-cambiame")
TOKEN_EXP_HOURS = 24


def hash_password(password: str) -> str:
    """Convierte una contraseña en texto plano a un hash seguro para guardar."""
    return generate_password_hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """Compara una contraseña en texto plano contra un hash guardado."""
    return check_password_hash(password_hash, password)


def generate_token(user_id: int) -> str:
    """Crea un token que identifica a este usuario, válido por TOKEN_EXP_HOURS."""
    payload = {
        "user_id": user_id,
        "exp": datetime.datetime.now(datetime.timezone.utc)
        + datetime.timedelta(hours=TOKEN_EXP_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token: str) -> int:
    """Verifica un token y devuelve el user_id que contiene.

    Lanza jwt.ExpiredSignatureError si ya venció, o jwt.InvalidTokenError
    si fue manipulado o es inválido.
    """
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    return payload["user_id"]
