# pc-api

## Descrição

Este projeto é a API do Pioneiros da Colina, desenvolvida para fornecer funcionalidades essenciais para o gerenciamento de desbravadores. Ela foi construída com foco em performance, segurança e manutenibilidade.

## Dependências

| Dependência | Finalidade |
|---|---|
| **FastAPI** | Framework web de alta performance com documentação automática (Swagger UI / ReDoc) |
| **Granian** | Servidor ASGI/RSGI de alta performance com suporte a uvloop |
| **SQLAlchemy** | ORM assíncrono para acesso ao banco de dados PostgreSQL |
| **Alembic** | Gerenciamento de migrações do banco de dados |
| **Pydantic / pydantic-settings** | Validação de dados e leitura de variáveis de ambiente |
| **pydantic-br** | Validadores para documentos brasileiros (CPF, CNPJ, etc.) |
| **PyJWT** | Geração e validação de tokens JWT |
| **pwdlib** | Hashing seguro de senhas |
| **secure** | Middleware que injeta cabeçalhos de segurança HTTP nas respostas |
| **ORJSON** | Serialização JSON de alta performance |
| **python-decouple** | Separação de configurações sensíveis do código |

## Pré-requisitos

*   **Python 3.13** ou superior
*   **UV** — gerenciador de pacotes moderno e rápido
*   **PostgreSQL** — banco de dados relacional

## Instalação

```bash
# 1. Clone o repositório
git clone <repository-url>
cd pc-api

# 2. Instale as dependências (cria o virtualenv automaticamente)
uv sync
```

## Configuração

Copie o arquivo de exemplo e preencha os valores:

```bash
cp .env.example .env
```

### Variáveis de ambiente

#### Servidor

| Variável | Padrão | Descrição |
|---|---|---|
| `ENVIRONMENT` | `development` | Ambiente de execução: `development` \| `production` \| `staging` \| `test`. Em `production` a documentação interativa é desativada. |
| `LOG_LEVEL` | `info` | Nível mínimo de log: `debug` \| `info` \| `warning` \| `error` \| `critical` |
| `SERVER_HOST` | `0.0.0.0` | Interface de rede para o servidor (`0.0.0.0` = todas) |
| `SERVER_PORT` | `8000` | Porta do servidor |
| `WORKERS` | `cpu * 2 + 1` | Número de processos workers |
| `SENTRY_DSN` | _(vazio)_ | DSN do Sentry para rastreamento de erros (deixe vazio para desativar) |

#### Banco de dados

| Variável | Padrão | Descrição |
|---|---|---|
| `DATABASE_HOST` | `localhost` | Host do PostgreSQL |
| `DATABASE_PORT` | `5432` | Porta do PostgreSQL |
| `DATABASE_USER` | `postgres` | Usuário do banco |
| `DATABASE_PASSWORD` | `postgres` | Senha do banco |
| `DATABASE_NAME` | `postgres` | Nome do banco |
| `DATABASE_ECHO` | `False` | Loga todas as queries SQL (útil para debug) |
| `DATABASE_POOL_SIZE` | `10` | Conexões persistentes no pool |
| `DATABASE_POOL_MAX_OVERFLOW` | `5` | Conexões extras além do pool |
| `DATABASE_POOL_RECYCLE` | `1800` | Segundos até reciclar uma conexão (30 min) |
| `DATABASE_POOL_PRE_PING` | `True` | Testa conexões antes de usar para detectar conexões obsoletas |
| `DATABASE_POOL_TIMEOUT` | `30` | Segundos de espera por uma conexão do pool |
| `DATABASE_POOL_RESET_ON_RETURN` | `commit` | Ação ao devolver conexão ao pool: `commit` \| `rollback` \| `none` |

#### Autenticação

| Variável | Padrão | Descrição |
|---|---|---|
| `AUTH_SECRET_KEY` | `secret` | Chave secreta para assinar tokens JWT (use uma string longa e aleatória em produção) |
| `AUTH_ALGORITHM` | `HS256` | Algoritmo de assinatura JWT |
| `AUTH_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Tempo de expiração do token em minutos |

## Banco de Dados

### Migrações

```bash
# Aplicar todas as migrações pendentes
uv run alembic upgrade head

# Criar uma nova migração (após alterar entities)
uv run alembic revision --autogenerate -m "descrição da mudança"

# Reverter a última migração
uv run alembic downgrade -1
```

### Seed

Após aplicar as migrações, popule as tabelas de roles e screens com os dados iniciais:

```bash
psql -d <database_name> -f seed.sql
```

O `seed.sql` insere todos os **13 papéis**, **17 telas** e os respectivos mapeamentos de permissão. É idempotente — pode ser re-executado com segurança.

## Execução

```bash
python app/main.py
```

A API estará disponível em `http://0.0.0.0:8000`. Com `ENVIRONMENT=development`, acesse a documentação interativa em `/docs`.

## Endpoints da API

### Health

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| `GET` | `/health` | Verifica o status da aplicação | Não |

### Auth

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| `POST` | `/auth/register` | Cadastra um novo usuário (CPF + data de nascimento) | Não |
| `POST` | `/auth/login` | Autentica e retorna um token JWT | Não |
| `GET` | `/auth/me` | Retorna o usuário atual com seus papéis e telas acessíveis | Bearer |

### Roles

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| `GET` | `/roles` | Lista todos os papéis disponíveis | Bearer |
| `POST` | `/roles/assign` | Atribui um papel a um usuário | Bearer + Admin |
| `DELETE` | `/roles/revoke` | Remove um papel de um usuário | Bearer + Admin |
| `GET` | `/roles/users` | Lista usuários com busca e paginação | Bearer + Admin |

> **Admin** = roles `diretor`, `secretaria` ou `tesouraria`.

### Reuniões

| Método | Rota | Descrição | Auth |
|---|---|---|---|
| `POST` | `/meetings` | Cria uma nova reunião | Bearer |

## Autenticação e Autorização

A API usa **JWT Bearer Token**. Após o login, inclua o token no header:

```
Authorization: Bearer <token>
```

### Papéis disponíveis

| ID | Label |
|---|---|
| `diretor` | Diretor |
| `secretaria` | Secretaria |
| `tesouraria` | Tesouraria |
| `equipe_pontuacao` | Equipe de Pontuação |
| `conselheiro_unidade` | Conselheiro da Unidade |
| `associado_unidade` | Associado da Unidade |
| `pai` | Pai |
| `membro` | Membro |
| `regional` | Regional |
| `distrital` | Distrital |
| `executiva` | Executiva |
| `chefe_apoio` | Chefe de Apoio |
| `apoio` | Apoio |

### Telas e permissões

| Tela (screen ID) | Papéis com acesso |
|---|---|
| `reunioes.nova_reuniao` | diretor, secretaria, tesouraria |
| `reunioes.editar` | diretor, secretaria, tesouraria |
| `reunioes.chamada` | diretor, secretaria, tesouraria, equipe_pontuacao |
| `secretaria` | diretor, secretaria, tesouraria |
| `unidade` | conselheiro_unidade, associado_unidade, diretor |
| `unidade.dashboard` | pai, conselheiro_unidade, associado_unidade |
| `meu_painel` | Todos |
| `tesouraria` | diretor, secretaria, tesouraria |
| `apoio_regional.informacoes` | Diretoria¹ |
| `apoio_regional.gerenciar_posts` | Diretoria¹ |
| `apoio_regional.caixa_entrada` | regional, distrital |
| `avaliacao_regional` | regional, distrital |
| `pontuacao.ranking` | Diretoria¹ |
| `pontuacao.lancamento` | equipe_pontuacao |
| `patrimonio.gerenciar` | diretor, secretaria, executiva, chefe_apoio |
| `patrimonio.solicitar_materiais` | Diretoria¹ + associado_unidade |
| `patrimonio.solicitacoes` | apoio |

> ¹ **Diretoria** = diretor, secretaria, tesouraria, executiva, chefe_apoio

O endpoint `GET /auth/me` retorna a lista de `roles` e `screens` do usuário autenticado para que o frontend possa controlar a navegação.

## Tratamento de Erros

Todos os erros retornam JSON no seguinte formato:

```json
{
  "message": "Mensagem de erro resumida",
  "detail": "Detalhes adicionais sobre o erro",
  "fields": [
    { "name": "nome_do_campo", "detail": "Detalhe do erro no campo" }
  ],
  "status_code": 400
}
```

| Código | Significado |
|---|---|
| `400` | Requisição inválida — dados malformados ou parâmetros ausentes |
| `401` | Não autenticado — token ausente, inválido ou expirado |
| `403` | Sem permissão — autenticado mas sem o papel necessário |
| `404` | Recurso não encontrado |
| `409` | Conflito — recurso já existe |
| `422` | Erro de validação — dados não passaram nas regras do Pydantic |
| `500` | Erro interno — reporte à equipe de desenvolvimento |

## Segurança

O middleware `secure` adiciona automaticamente os seguintes cabeçalhos HTTP em todas as respostas:

*   `X-Content-Type-Options` — previne MIME-sniffing
*   `X-Frame-Options` — impede embedding em `<iframe>`
*   `Strict-Transport-Security` — força HTTPS em conexões futuras

## Estrutura do Projeto

```
pc-api/
├── app/
│   ├── main.py              # Ponto de entrada da aplicação
│   ├── settings.py          # Configurações via variáveis de ambiente
│   ├── api/
│   │   ├── routes.py        # Router principal (agrega todos os módulos)
│   │   ├── schemas.py       # BaseResponseSchema
│   │   ├── domain.py        # Classe base ApiDomain
│   │   ├── secure.py        # Middleware de cabeçalhos de segurança
│   │   └── exc/             # Exceções customizadas e handlers
│   ├── auth/
│   │   ├── entities.py      # UsersEntity (ORM)
│   │   ├── schemas.py       # Schemas de usuário e token
│   │   ├── repository.py    # UserRepository (busca, criação, paginação)
│   │   ├── domain.py        # Login e Register use cases
│   │   ├── handler.py       # JWT: sign, decode, HTTPBearer
│   │   ├── guards.py        # require_roles() — dependency de autorização
│   │   └── routes.py        # /auth/*
│   ├── roles/
│   │   ├── concepts.py      # Enums Role e Screen
│   │   ├── entities.py      # RoleEntity, ScreenEntity, RoleScreenEntity, UserRoleEntity
│   │   ├── schemas.py       # Schemas de roles e permissões
│   │   ├── repository.py    # Repositórios de roles e screens
│   │   ├── domain.py        # Use cases: assign, revoke, list users, permissions
│   │   └── routes.py        # /roles/*
│   ├── meetings/
│   │   ├── entities.py      # MeetingEntity (ORM)
│   │   ├── schemas.py       # Schemas de reunião
│   │   ├── repository.py    # MeetingRepository
│   │   ├── domain.py        # CreateMeeting use case
│   │   └── routes.py        # /meetings/*
│   └── infra/
│       └── database/
│           ├── adapter.py   # SessionAdapter, DatabaseAdapter, SessionContext
│           ├── config.py    # ConnectionConfig, PoolConfig
│           ├── entities.py  # Entity base, mixins (UUID, VarChar, Timestamp)
│           └── repository.py # Repository genérico com CRUD e paginação
├── migrations/
│   ├── env.py               # Configuração do Alembic
│   └── versions/            # Arquivos de migração
├── seed.sql                 # Dados iniciais: roles, screens e permissões
├── .env.example             # Exemplo de variáveis de ambiente
├── pyproject.toml           # Dependências e configurações do projeto
└── README.md                # Este arquivo
```

## Desenvolvimento

### Testes

```bash
uv run pytest
```

### Linting e Formatação

```bash
# Verificar problemas
uv run ruff check

# Formatar código
uv run ruff format
```
