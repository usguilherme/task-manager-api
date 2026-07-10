# Gerenciador de Tarefas

API REST, frontend web e CLI para gerenciamento de tarefas, construído em
Python com **FastAPI**, **SQLite** e arquitetura em camadas (models →
repository → service → API/CLI).

![CI](https://github.com/usguilherme/gerenciador-de-tarefas/actions/workflows/ci.yml/badge.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Por que este projeto

Comecei como um To-Do List de terminal simples para praticar POO e SQLite.
Na v2, refatorei a base inteira para separar responsabilidades em camadas
independentes e testáveis, adicionei uma API REST completa por cima da
mesma lógica de negócio, e um frontend web que consome essa API — sem
duplicar código de negócio entre CLI, API e frontend.

## Demo

O frontend é servido pela própria API em `http://localhost:8000/`. O
visual remete de propósito a um terminal, já que o projeto nasceu como
uma aplicação de linha de comando.

```bash
make run
# abra http://localhost:8000
```

## Arquitetura

```
┌─────────────┐  ┌─────────────┐  ┌──────────────┐
│     CLI     │  │  Frontend   │  │   API REST   │   ← interfaces
│  (cli.py)   │  │ (static/)   │─▶│ (app/api.py) │      (sem regra de negócio)
└──────┬──────┘  └─────────────┘  └──────┬───────┘
       │                                 │
       └────────────────┬────────────────┘
                         ▼
              ┌──────────────────────┐
              │  GerenciadorTarefas   │   ← regras de negócio (app/service.py)
              └──────────┬────────────┘
                         ▼
              ┌──────────────────────┐
              │   TarefaRepository    │   ← única camada que fala SQL (app/repository.py)
              └──────────┬────────────┘
                         ▼
              ┌──────────────────────┐
              │  Database (SQLite)    │   ← conexão via context manager (app/database.py)
              └──────────────────────┘
```

Cada camada só conhece a camada logo abaixo dela. `GerenciadorTarefas` não
sabe se está sendo chamado por HTTP, terminal ou um form no navegador, e
`TarefaRepository` é o único lugar do sistema que escreve SQL — trocar
SQLite por PostgreSQL no futuro seria uma mudança isolada em um arquivo.

## Funcionalidades

- CRUD completo de tarefas (título, descrição, prioridade, data de vencimento)
- Frontend web funcional (busca, filtros, paginação, criação, conclusão)
- Busca por título/descrição e paginação na listagem (API e frontend)
- Filtros por status: todas / pendentes / concluídas
- Conclusão e reabertura de tarefas
- Limpeza em lote de tarefas concluídas
- Ordenação por data de vencimento
- Estatísticas (total, concluídas, pendentes, taxa de conclusão)
- Validação de dados no nível do modelo (título vazio, data mal formatada,
  prioridade inválida nunca chegam a existir como objeto)
- Erros de negócio como exceções tipadas (`TarefaNotFoundError`), não `print()`
- Configuração via variáveis de ambiente (`GERENCIADOR_DATABASE_PATH`,
  `GERENCIADOR_LOG_LEVEL`)
- Logging estruturado em vez de `print()`

## Stack

| Camada | Tecnologia |
|---|---|
| API | FastAPI + Pydantic |
| Frontend | HTML/CSS/JS puro, sem build step |
| Persistência | SQLite (via `sqlite3` da biblioteca padrão) |
| Configuração | pydantic-settings |
| Testes | pytest + `TestClient` do FastAPI |
| Lint | ruff (+ pre-commit) |
| CI | GitHub Actions |
| Deploy | Docker / Docker Compose |

## Rodando localmente

```bash
git clone https://github.com/usguilherme/gerenciador-de-tarefas.git
cd gerenciador-de-tarefas
make install
```

### API + frontend

```bash
make run
# API:       http://localhost:8000
# Frontend:  http://localhost:8000/
# Swagger:   http://localhost:8000/docs
```

### CLI

```bash
make cli
```

### Com Docker Compose

```bash
make docker-up
```

### Configuração (opcional)

```bash
export GERENCIADOR_DATABASE_PATH=/caminho/customizado/tarefas.db
export GERENCIADOR_LOG_LEVEL=DEBUG
```

## Endpoints da API

| Método | Rota | Descrição |
|---|---|---|
| GET | `/tarefas` | Lista tarefas (`?filtro=&busca=&pagina=&tamanho_pagina=`) |
| POST | `/tarefas` | Cria uma tarefa |
| GET | `/tarefas/{id}` | Busca uma tarefa por ID |
| PATCH | `/tarefas/{id}` | Edita campos de uma tarefa |
| POST | `/tarefas/{id}/concluir` | Marca como concluída |
| POST | `/tarefas/{id}/reabrir` | Reabre uma tarefa concluída |
| DELETE | `/tarefas/{id}` | Remove uma tarefa |
| DELETE | `/tarefas/concluidas/limpar` | Remove todas as concluídas |
| GET | `/tarefas/resumo/estatisticas` | Estatísticas gerais |
| GET | `/api` | Metadados da API |

Exemplo:

```bash
curl -X POST http://localhost:8000/tarefas \
  -H "Content-Type: application/json" \
  -d '{"titulo": "Estudar FastAPI", "prioridade": "Alta", "data_vencimento": "2026-07-20"}'

curl "http://localhost:8000/tarefas?busca=fastapi&pagina=1&tamanho_pagina=10"
```

## Testes

35 testes cobrindo modelo, repositório, serviço e API (unitários + integração):

```bash
make test
```

## Qualidade de código

```bash
make lint     # ruff check
make format   # ruff check --fix
```

O CI roda lint + testes em Python 3.11 e 3.12 a cada push/PR.

## Estrutura do projeto

```
├── app/
│   ├── models.py           # Entidade Tarefa (validação de domínio)
│   ├── database.py         # Conexão SQLite via context manager
│   ├── repository.py       # Acesso a dados (única camada com SQL)
│   ├── service.py          # Regras de negócio
│   ├── api.py               # Rotas FastAPI + montagem do frontend
│   ├── config.py            # Configuração via variáveis de ambiente
│   ├── logging_config.py   # Logging estruturado
│   └── exceptions.py       # Exceções de domínio
├── static/
│   └── index.html          # Frontend web (consome a API)
├── cli.py                   # Interface de terminal
├── tests/
├── .github/workflows/ci.yml
├── .pre-commit-config.yaml
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── requirements.txt
```

## Possíveis próximos passos

- Autenticação (JWT) para múltiplos usuários
- Migração para PostgreSQL em produção
- Notificações de tarefas próximas ao vencimento

## Licença

MIT — veja [LICENSE](LICENSE).
