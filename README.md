# To-Do API (Python + Flask)

API REST sencilla para gestionar una lista de tareas. Proyecto creado para
practicar y consolidar las bases de Python, aplicando lo aprendido en un
caso real, con la intención de ir creciendo por fases.

## 🚧 Estado del proyecto

**Fase 1 - Completada:** CRUD básico con almacenamiento en memoria.

Próximas fases planeadas:

- [ ] Persistencia con base de datos (SQLite + SQLAlchemy)
- [ ] Validaciones y manejo de errores más robusto
- [ ] Autenticación de usuarios
- [ ] Documentación automática (Swagger / FastAPI)
- [ ] Tests con mayor cobertura
- [ ] Deploy en la nube

## 📦 Instalación

```bash
git clone <url-de-tu-repo>
cd todo-api-python
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## ▶️ Cómo correr el proyecto

```bash
python -m app.main
```

La API quedará disponible en `http://127.0.0.1:5000`.

## 🔌 Endpoints

| Método | Ruta        | Descripción                   |
| ------ | ----------- | ----------------------------- |
| GET    | /tasks      | Lista todas las tareas        |
| GET    | /tasks/{id} | Obtiene una tarea por id      |
| POST   | /tasks      | Crea una tarea nueva          |
| PUT    | /tasks/{id} | Actualiza una tarea existente |
| DELETE | /tasks/{id} | Elimina una tarea             |

### Ejemplo: crear una tarea

```bash
curl -X POST http://127.0.0.1:5000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Aprender Python"}'
```

## 🧪 Cómo correr las pruebas

```bash
pytest
```

## 🧠 Qué aprendí en esta fase

- Estructurar un proyecto de Python en módulos y paquetes.
- Crear una API REST con Flask (rutas, métodos HTTP, respuestas JSON).
- Programación orientada a objetos básica (clase `Task`).
- Escribir pruebas automatizadas con `pytest`.
