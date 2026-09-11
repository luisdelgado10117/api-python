"""
Excepciones propias del dominio de tareas.

Crear tus propias excepciones (en vez de usar solo genéricas como
`Exception` o `ValueError`) hace el código mucho más claro: cuando lees
`except TaskNotFoundError`, sabes exactamente qué pasó, sin adivinar.
"""


class TaskNotFoundError(Exception):
    """Se lanza cuando se busca una tarea que no existe."""


class InvalidTaskDataError(Exception):
    """Se lanza cuando los datos para crear/actualizar una tarea son inválidos."""


class UserAlreadyExistsError(Exception):
    """Se lanza al intentar registrar un username que ya está en uso."""


class InvalidUserDataError(Exception):
    """Se lanza cuando el username o password no cumplen las reglas mínimas."""


class InvalidCredentialsError(Exception):
    """Se lanza cuando el username o password no coinciden con ningún usuario."""