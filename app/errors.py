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
