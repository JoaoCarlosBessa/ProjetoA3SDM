# ProjetoA3SDM

API básica de gerenciamento de tarefas construída com FastAPI.

## Funcionalidades

- Criar tarefas
- Listar tarefas
- Visualizar uma tarefa
- Editar tarefas
- Marcar tarefas como concluídas

## Requisitos

- Python 3.10+

## Instalação

```bash
python -m pip install -r requirements.txt
```

## Execução

```bash
python -m uvicorn app.main:app --reload
```

Se o comando `uvicorn` não estiver disponível no seu terminal, use a forma acima com `python -m`, que executa o servidor pelo mesmo interpretador usado na instalação.

A API persiste as tarefas em um arquivo SQLite local chamado `SDM_A3.db` na raiz do projeto.

Abra o frontend carregando `frontend/index.html` em um navegador ou servindo a pasta `frontend/` com qualquer servidor de arquivos estáticos.

O frontend espera a API em `http://127.0.0.1:8000` por padrão.

## Endpoints

- `GET /health`
- `GET /tasks`
- `POST /tasks`
- `GET /tasks/{task_id}`
- `PUT /tasks/{task_id}`
- `PATCH /tasks/{task_id}/complete`

## Frontend

A pasta `frontend/` contém um cliente simples em HTML e JavaScript que se comunica com a API usando `fetch`.

## Exemplos de payload

Criar tarefa:

```json
{
	"title": "Finalizar relatório",
	"description": "Preparar o relatório final do projeto"
}
```

Editar tarefa:

```json
{
	"title": "Finalizar relatório v2",
	"completed": false
}
```