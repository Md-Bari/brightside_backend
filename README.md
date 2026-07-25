# Brightside AI Chatbot Backend

Production-ready AI chatbot backend for **Brightside Car Wash**, built with
Django REST Framework, PostgreSQL + pgvector, JSONB conversation storage,
and Groq as the LLM. Fully dockerized with Nginx, Gunicorn and pgAdmin.

## Architecture

```
User → Nginx → Gunicorn → Django REST Framework
                              ├─ Question Classifier (DOMAIN / GENERAL)
                              ├─ Session Manager (JSONB conversation memory)
                              └─ Knowledge Base (pgvector RAG)
                                       ↓
                                  Prompt Builder → Groq API → Response
```

Layering: **APIView → Serializer → Service → Repository → Database**.
Views contain no business logic; repositories are the only layer that
touches the ORM.

### Project structure

```
brightside_backend/
├── config/                # settings, urls, wsgi/asgi
├── apps/
│   ├── common/             # standard response envelope, exceptions, pagination, logging middleware
│   ├── users/               # email-based customer identification
│   ├── sessions/            # chat session lifecycle + JSONB conversation storage
│   ├── chatbot/              # classifier, chat orchestration service, public chat endpoint
│   ├── knowledgebase/        # KB upload pipeline + pgvector RAG search (admin)
│   └── adminpanel/           # JWT login for admin APIs
├── utils/
│   ├── llm/groq_client.py               # Groq wrapper
│   ├── embeddings/                      # OpenAI / Gemini embedding abstraction
│   └── text_processing/                 # extraction, cleaning, chunking
├── prompts/builder.py       # prompt assembly (system + history + KB context + question)
├── docker/                  # entrypoint.sh, postgres init SQL, pgadmin server config
├── nginx/nginx.conf
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env.example
```

## Tech stack

Django 5, DRF, PostgreSQL 16 + pgvector, JSONB, Groq, OpenAI/Gemini
embeddings (configurable), SimpleJWT (admin only), drf-spectacular
(Swagger/Redoc), Docker Compose, Gunicorn, Nginx, pgAdmin.

## Getting started (Docker)

1. Copy environment variables and fill in your API keys:

   ```bash
   cp .env.example .env
   # edit .env: GROQ_API_KEY, OPENAI_API_KEY (or GEMINI_API_KEY + EMBEDDING_PROVIDER=gemini)
   ```

2. Build and start every service:

   ```bash
   docker compose up --build
   ```

   This starts: `postgres` (with pgvector extension auto-created),
   `backend` (Django via Gunicorn, runs migrations automatically),
   `nginx` (reverse proxy on port 80), `pgadmin` (on port 5050).

3. Create an admin (staff) user for the JWT-protected admin APIs:

   ```bash
   docker compose exec backend python manage.py createsuperuser
   ```

4. Open:

   - Swagger UI: http://localhost/api/docs/  (or http://localhost:8000/api/docs/)
   - Redoc: http://localhost/api/redoc/
   - OpenAPI schema: http://localhost/api/schema/
   - Django admin: http://localhost/admin/
   - pgAdmin: http://localhost:5050  (login with `PGADMIN_DEFAULT_EMAIL` /
     `PGADMIN_DEFAULT_PASSWORD` from `.env`; the Brightside PostgreSQL
     server is pre-registered — enter `POSTGRES_PASSWORD` on first connect)

## Common Docker commands

```bash
docker compose up --build          # build & start all services
docker compose down                # stop everything
docker compose logs -f backend     # tail backend logs
docker compose exec backend bash   # shell into the backend container
docker compose exec backend python manage.py migrate
docker compose exec backend python manage.py createsuperuser
docker compose exec backend python manage.py test
```

## API overview

All responses follow a standard envelope:

```json
{ "success": true, "message": "...", "data": {} }
{ "success": false, "message": "...", "errors": {} }
```

### Public (no auth — UUID session validation)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/sessions/` | Create a session (`{"email": "..."}`) → returns `session_id` and the customer's `user_id` |
| POST | `/api/v1/chat/message/` | Send a chat message (`{"session_id": "...", "message": "..."}`) |
| POST | `/api/v1/sessions/end/` | End a session (`{"session_id": "..."}`) |

### Data model

Two tables, two identifiers, both UUIDs:

```
customer_users                     chat_sessions
──────────────                     ─────────────
user_id     UUID  [PK]  ◄─────────── user_id     UUID  (FK)
email                                session_id  UUID  [PK]
name                                 messages    JSONB — the chats
created_at / updated_at              created_at / updated_at / ended_at
```

- **`user_id`** — one per customer, stable across all of their sessions.
  It is the *primary key* of `customer_users`: there is no surrogate
  integer `id` column. The session foreign key stores this same UUID, so
  `user_id` denotes exactly one thing in every table and everywhere in the
  code.
- **`session_id`** — one per chat session, and the *primary key* of
  `chat_sessions`. Again no surrogate `id`: one table, one identifier.
- The conversation lives entirely in `chat_sessions.messages` (JSONB).

Sessions do not store the email — it is read through the user relation, so
a customer's email exists in exactly one place.

### Admin (JWT — obtain via `/api/v1/auth/login/`)

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/login/` | Obtain JWT access/refresh tokens (staff/superuser only) |
| POST | `/api/v1/auth/refresh/` | Refresh an access token |
| GET | `/api/v1/admin/users/` | List all chatbot customers (each with its `user_id`) |
| GET | `/api/v1/admin/users/{user_id}/sessions/` | List every `session_id` belonging to one customer |
| GET | `/api/v1/admin/sessions/{session_id}/` | The chats (full JSONB conversation) of one session |
| POST | `/api/v1/admin/kb/upload/` | Upload a knowledge base file (PDF/DOCX/TXT) |
| GET | `/api/v1/admin/kb/` | List knowledge base files |
| GET/DELETE | `/api/v1/admin/kb/{id}/` | Retrieve (with chunks) / delete a knowledge base file |

Use `Authorization: Bearer <access_token>` for all `/api/v1/admin/*` calls.

### Admin dashboard pipeline

The three admin endpoints are designed to be drilled through in order:

```
1. GET /api/v1/admin/users/
      → every user_id
              │ click a user_id
              ▼
2. GET /api/v1/admin/users/{user_id}/sessions/
      → every session_id for that user (+ status, message_count)
              │ click a session_id
              ▼
3. GET /api/v1/admin/sessions/{session_id}/
      → the chats (messages JSONB)
```

### Knowledge base timestamps

Every knowledge base operation is timestamped in the database and returned
in the response:

| Field | Set when |
|---|---|
| `uploaded_at` | the file row is first created |
| `updated_at` | any change to the file row (edit, re-processing) |
| `processed_at` | extraction + chunking + embedding finishes (success or failure) |
| `deleted_at` | returned in the `DELETE` response body |

Chunks carry their own `created_at` / `updated_at`, exposed on the file
detail endpoint.

## How a chat message is processed

1. Load the session's JSONB conversation history.
2. Append the new user message.
3. Classify the question as `DOMAIN` or `GENERAL` (Groq-based classifier).
4. If `DOMAIN`: embed the question, run a pgvector cosine-similarity
   search over `knowledge_chunks`, retrieve the top-K chunks.
5. Build the final prompt: system prompt + full conversation history +
   retrieved KB context (if any) + current question.
6. Call Groq for the answer.
7. Append the assistant message and persist the full JSONB array.
8. Return the standard response envelope with the answer.

No summarization is performed in V1 — the full JSONB history is always
sent to the LLM.

## Switching embedding providers

Set in `.env`:

```
EMBEDDING_PROVIDER=openai   # or "gemini"
EMBEDDING_DIMENSION=1536    # must match the chosen model's output dimension
```

Changing the provider after knowledge base data already exists requires
re-uploading documents (embeddings from different models are not
interchangeable).

## Running tests

```bash
docker compose exec backend python manage.py test
```

or locally (with a Postgres+pgvector instance available):

```bash
python manage.py test
```

## Local (non-Docker) development

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # point POSTGRES_HOST to localhost and start Postgres+pgvector yourself
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

> `runserver` is for local development only — Docker always runs Gunicorn
> behind Nginx.

## Notes

- No Redis, Celery, RabbitMQ, or external vector databases are used —
  vector search runs entirely inside PostgreSQL via `pgvector`.
- API keys are never logged; the logging middleware only records method,
  path, status code and latency.
- Public chatbot endpoints are authorized via UUID session validation;
  only `/api/v1/admin/*` endpoints require JWT.
