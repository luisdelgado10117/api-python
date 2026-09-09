"""
Modelo de datos para las tareas.

Aquí usamos una clase para representar cada tarea. Es una forma sencilla
de empezar a practicar Programación Orientada a Objetos (POO), aunque
el proyecto todavía sea "principiante".
"""


class Task:
    """Representa una tarea individual."""

    def __init__(self, task_id: int, title: str, done: bool = False):
        self.id = task_id
        self.title = title
        self.done = done

    def to_dict(self) -> dict:
        """Convierte la tarea a un diccionario, útil para responder en JSON."""
        return {
            "id": self.id,
            "title": self.title,
            "done": self.done,
        }