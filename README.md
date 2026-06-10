# ProjetoA3SDM

API de gerenciamento de tarefas construída com FastAPI e persistência local em SQLite.

## Visão Geral

O projeto está organizado em duas camadas principais:

- `app/` concentra o backend da API.
- `frontend/` contém uma interface estática em HTML, CSS e JavaScript que consome a API via `fetch`.

A aplicação permite criar, listar, visualizar, editar, concluir e excluir tarefas. Os dados ficam armazenados em um banco SQLite local chamado `SDM_A3.db`, criado automaticamente na raiz do projeto.

## Arquitetura

O backend segue uma estrutura simples em três partes:

- `app/main.py` define a aplicação FastAPI, os endpoints HTTP e a configuração de CORS.
- `app/schemas.py` define os modelos de entrada e saída usados na validação dos dados com Pydantic.
- `app/store.py` centraliza a persistência em SQLite e encapsula as operações de CRUD.

O frontend não tem lógica de negócio própria. Ele apenas envia requisições para a API, renderiza as tarefas retornadas e mantém o estado visual da tela.

## Tecnologias Utilizadas

- Python 3.10+
- FastAPI
- Pydantic
- SQLite
- Uvicorn
- HTML, CSS e JavaScript no frontend

## Funcionamento da API

Ao iniciar, a API cria a tabela `tasks` caso ela ainda não exista e garante a existência das colunas necessárias no banco local. Cada tarefa possui identificador único, título, descrição opcional, data de entrega opcional, prioridade, status de conclusão e datas de criação/atualização.

O fluxo básico é o seguinte:

1. O cliente envia uma requisição HTTP para um endpoint da API.
2. FastAPI valida o payload usando os schemas definidos em `app/schemas.py`.
3. A camada de persistência em `app/store.py` executa a operação no SQLite.
4. A API retorna a tarefa atualizada ou a lista de tarefas em formato JSON.

O frontend utiliza `http://127.0.0.1:8000` como URL padrão da API, mas esse endereço pode ser alterado na própria interface.

## Endpoints

### `GET /health`
Retorna um status simples para verificar se a API está ativa.

### `GET /tasks`
Lista todas as tarefas ordenadas pela data de atualização mais recente.

### `POST /tasks`
Cria uma nova tarefa.

Exemplo de payload:

```json
{
	"title": "Finalizar relatório",
	"description": "Preparar o relatório final do projeto",
	"due_date": "2026-06-20",
	"priority": "medium"
}
```

### `GET /tasks/{task_id}`
Retorna os dados de uma tarefa específica.

### `PUT /tasks/{task_id}`
Atualiza os dados da tarefa. Campos omitidos mantêm o valor atual.

Exemplo de payload:

```json
{
	"title": "Finalizar relatório v2",
	"completed": false
}
```

### `PATCH /tasks/{task_id}/complete`
Marca a tarefa como concluída.

### `DELETE /tasks/{task_id}`
Remove a tarefa do banco.

## Instalação

```bash
python -m pip install -r requirements.txt
```

## Execução

```bash
python -m uvicorn app.main:app --reload
```

Se o comando `uvicorn` não estiver disponível no terminal, use `python -m uvicorn`, que executa o servidor pelo mesmo interpretador usado na instalação.

## Frontend

Para usar a interface, abra `frontend/index.html` em um navegador ou sirva a pasta `frontend/` com qualquer servidor de arquivos estáticos.

O frontend já vem configurado para consumir a API em `http://127.0.0.1:8000`.
