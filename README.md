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
uvicorn app.main:app --reload
```

A API agora persiste as tarefas em um arquivo SQLite local chamado `SDM_A3.db` na raiz do projeto.

Se você já tiver um arquivo de banco SQLite, coloque-o na raiz do projeto com esse nome exato para que a API o utilize.

Se você quiser recriar o banco no sqliteonline.com, abra `sqliteonline-schema.sql` e execute a instrução `CREATE TABLE` lá.

Abra o frontend carregando `frontend/index.html` em um navegador ou servindo a pasta `frontend/` com qualquer servidor de arquivos estáticos.

O frontend espera a API em `http://127.0.0.1:8000` por padrão. Você pode alterar a URL na página se a API estiver rodando em outro endereço.

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