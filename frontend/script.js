const defaultApiBaseUrl = "http://127.0.0.1:8000";

const apiBaseUrlInput = document.getElementById("apiBaseUrl");
const refreshTasksButton = document.getElementById("refreshTasks");
const createTaskForm = document.getElementById("createTaskForm");
const tasksList = document.getElementById("tasksList");
const taskTemplate = document.getElementById("taskTemplate");
const statusText = document.getElementById("statusText");

apiBaseUrlInput.value = localStorage.getItem("taskflowApiBaseUrl") || defaultApiBaseUrl;

function apiBaseUrl() {
  return apiBaseUrlInput.value.replace(/\/+$/, "");
}

function saveApiBaseUrl() {
  localStorage.setItem("taskflowApiBaseUrl", apiBaseUrl());
}

async function request(path, options = {}) {
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || `Request failed with status ${response.status}`);
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

function formatDate(value) {
  return new Date(value).toLocaleString();
}

function formatDueDate(value) {
  if (!value) {
    return "Sem data de entrega";
  }

  return new Date(`${value}T00:00:00`).toLocaleDateString();
}

function priorityLabel(priority) {
  if (priority === "high") {
    return "Alta prioridade";
  }

  if (priority === "low") {
    return "Baixa prioridade";
  }

  return "Prioridade média";
}

function isOverdue(task) {
  if (!task.due_date || task.completed) {
    return false;
  }

  const dueDate = new Date(`${task.due_date}T23:59:59`);
  return dueDate < new Date();
}

function priorityRank(priority) {
  if (priority === "high") {
    return 0;
  }

  if (priority === "medium") {
    return 1;
  }

  return 2;
}

function compareTasks(left, right) {
  const leftHasDueDate = Boolean(left.due_date);
  const rightHasDueDate = Boolean(right.due_date);

  if (leftHasDueDate !== rightHasDueDate) {
    return leftHasDueDate ? -1 : 1;
  }

  if (leftHasDueDate && rightHasDueDate) {
    const dueDateComparison = new Date(left.due_date) - new Date(right.due_date);
    if (dueDateComparison !== 0) {
      return dueDateComparison;
    }
  }

  const priorityComparison = priorityRank(left.priority) - priorityRank(right.priority);
  if (priorityComparison !== 0) {
    return priorityComparison;
  }

  return new Date(right.updated_at) - new Date(left.updated_at);
}

function taskSummary(task) {
  return task.completed ? "Concluída" : "Pendente";
}

function renderTask(task) {
  const fragment = taskTemplate.content.cloneNode(true);
  const taskCard = fragment.querySelector(".task-card");
  const title = fragment.querySelector(".task-title");
  const description = fragment.querySelector(".task-description");
  const status = fragment.querySelector(".task-status");
  const editForm = fragment.querySelector(".edit-form");
  const editTitle = fragment.querySelector(".edit-title");
  const editDescription = fragment.querySelector(".edit-description");
  const editDueDate = fragment.querySelector(".edit-due-date");
  const editPriority = fragment.querySelector(".edit-priority");
  const completeButton = fragment.querySelector(".complete-button");
  const deleteButton = fragment.querySelector(".delete-button");
  const taskMeta = fragment.querySelector(".task-meta");

  title.textContent = task.title;
  description.textContent = task.description || "Sem descrição informada.";
  taskMeta.textContent = `${formatDueDate(task.due_date)} · ${priorityLabel(task.priority)}`;
  status.textContent = `${taskSummary(task)}${isOverdue(task) ? " · Atrasada" : ""} · Atualizada em ${formatDate(task.updated_at)}`;
  editTitle.value = task.title;
  editDescription.value = task.description || "";
  editDueDate.value = task.due_date || "";
  editPriority.value = task.priority || "medium";
  completeButton.disabled = task.completed;
  completeButton.textContent = task.completed ? "Concluída" : "Concluir";

  if (isOverdue(task)) {
    taskCard.classList.add("task-overdue");
  }

  editForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    saveApiBaseUrl();

    await request(`/tasks/${task.id}`, {
      method: "PUT",
      body: JSON.stringify({
        title: editTitle.value.trim(),
        description: editDescription.value.trim(),
        due_date: editDueDate.value || null,
        priority: editPriority.value,
        completed: task.completed,
      }),
    });

    await loadTasks();
  });

  completeButton.addEventListener("click", async () => {
    saveApiBaseUrl();
    await request(`/tasks/${task.id}/complete`, { method: "PATCH" });
    await loadTasks();
  });

  deleteButton.addEventListener("click", async () => {
    saveApiBaseUrl();

    const shouldDelete = window.confirm(`Excluir a tarefa \"${task.title}\"?`);
    if (!shouldDelete) {
      return;
    }

    await request(`/tasks/${task.id}`, { method: "DELETE" });
    await loadTasks();
  });

  return taskCard;
}

async function loadTasks() {
  statusText.textContent = "Carregando...";
  tasksList.innerHTML = "";

  try {
    const tasks = await request("/tasks");

    if (tasks.length === 0) {
      statusText.textContent = "Nenhuma tarefa ainda.";
      tasksList.innerHTML = "<p class='task-description'>Crie sua primeira tarefa para começar.</p>";
      return;
    }

    statusText.textContent = `${tasks.length} tarefa${tasks.length === 1 ? "" : "s"}`;
    tasks
      .slice()
      .sort(compareTasks)
      .forEach((task) => tasksList.appendChild(renderTask(task)));
  } catch (error) {
    statusText.textContent = "Não foi possível carregar as tarefas.";
    tasksList.innerHTML = `<p class='task-description'>${error.message}</p>`;
  }
}

createTaskForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  saveApiBaseUrl();

  const formData = new FormData(createTaskForm);
  const payload = {
    title: String(formData.get("title") || "").trim(),
    description: String(formData.get("description") || "").trim() || null,
    due_date: String(formData.get("due_date") || "") || null,
    priority: String(formData.get("priority") || "medium"),
  };

  await request("/tasks", {
    method: "POST",
    body: JSON.stringify(payload),
  });

  createTaskForm.reset();
  await loadTasks();
});

refreshTasksButton.addEventListener("click", async () => {
  saveApiBaseUrl();
  await loadTasks();
});

apiBaseUrlInput.addEventListener("change", () => {
  saveApiBaseUrl();
});

loadTasks();