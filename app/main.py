from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .schemas import TaskCreate, TaskRead, TaskUpdate
from .store import TaskStore, _UNSET, task_to_dict


app = FastAPI(
    title="API de Gerenciamento de Tarefas",
    description="API básica de gerenciamento de tarefas para criar, editar, listar e concluir tarefas.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = TaskStore()


def _fields_set(payload: TaskUpdate) -> set[str]:
    fields_set = getattr(payload, "model_fields_set", None)
    if fields_set is not None:
        return set(fields_set)

    legacy_fields_set = getattr(payload, "__fields_set__", None)
    return set(legacy_fields_set or set())


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/tasks", response_model=list[TaskRead])
def list_tasks() -> list[dict]:
    return [task_to_dict(task) for task in store.list()]


@app.post("/tasks", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(payload: TaskCreate) -> dict:
    task = store.create(payload.title, payload.description, payload.due_date, payload.priority)
    return task_to_dict(task)


@app.get("/tasks/{task_id}", response_model=TaskRead)
def get_task(task_id: str) -> dict:
    task = store.get(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task_to_dict(task)


@app.put("/tasks/{task_id}", response_model=TaskRead)
def edit_task(task_id: str, payload: TaskUpdate) -> dict:
    fields_set = _fields_set(payload)
    task = store.update(
        task_id,
        title=payload.title,
        description=payload.description,
        due_date=payload.due_date if "due_date" in fields_set else _UNSET,
        priority=payload.priority if "priority" in fields_set else _UNSET,
        completed=payload.completed,
    )
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task_to_dict(task)


@app.patch("/tasks/{task_id}/complete", response_model=TaskRead)
def complete_task(task_id: str) -> dict:
    task = store.complete(task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task_to_dict(task)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str) -> None:
    deleted = store.delete(task_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
