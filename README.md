# PlatformHub

[![CI](https://github.com/y0s3ph/platformhub/actions/workflows/ci.yml/badge.svg)](https://github.com/y0s3ph/platformhub/actions/workflows/ci.yml)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-jph91-0A66C2?logo=linkedin)](https://linkedin.com/in/jph91)

**Developer self-service portal for infrastructure provisioning.**

PlatformHub lets developers request infrastructure resources (Kubernetes namespaces, S3 buckets, RDS databases) through a web UI or REST API. Requests go through an approval workflow, and production-ready manifests (Kubernetes YAML / Terraform HCL) are generated automatically upon approval.

## Features

- **Self-service catalog** — Browse available infrastructure resources with pre-configured parameters
- **Approval workflow** — Requests require approver/admin review before provisioning
- **Manifest generation** — Kubernetes YAML and Terraform HCL generated via Jinja2 templates with security best practices baked in
- **Role-based access** — Developers, approvers, and admins with JWT authentication
- **Audit trail** — Every action is logged: who requested what, who approved it, when
- **API-first** — Full REST API with auto-generated Swagger/OpenAPI docs at `/docs`
- **Modern UI** — HTMX + TailwindCSS for a responsive, lightweight frontend
- **Zero infrastructure** — SQLite by default, swap to PostgreSQL with one env var

## Resource Catalog

| Resource | Output Format | What's Included |
|---|---|---|
| **Kubernetes Namespace** | YAML | Namespace, ResourceQuota, NetworkPolicy, RBAC RoleBinding |
| **S3 Bucket** | Terraform HCL | Bucket, versioning, KMS encryption, public access block |
| **RDS Database** | Terraform HCL | Instance, encryption, backups, multi-AZ, security variables |

## Quick Start

```bash
git clone https://github.com/y0s3ph/platformhub.git
cd platformhub
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn platformhub.main:app --reload
```

Open [http://localhost:8000](http://localhost:8000) for the UI or [http://localhost:8000/docs](http://localhost:8000/docs) for the API docs.

## Usage

### 1. Register and login

```bash
# Register a new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "dev1", "email": "dev1@example.com", "password": "securepass123"}'

# Login and get token
curl -X POST http://localhost:8000/api/auth/login \
  -d "username=dev1&password=securepass123"
```

### 2. Browse the catalog

```bash
curl http://localhost:8000/api/catalog/
```

### 3. Submit a resource request

```bash
curl -X POST http://localhost:8000/api/requests/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "resource_type": "k8s_namespace",
    "name": "my-service",
    "environment": "staging",
    "parameters": {"cpu_limit": "2", "memory_limit": "2Gi", "team": "backend"}
  }'
```

### 4. Approve (as approver)

```bash
curl -X POST http://localhost:8000/api/admin/<request_id>/review \
  -H "Authorization: Bearer <approver_token>" \
  -H "Content-Type: application/json" \
  -d '{"action": "approved", "comment": "LGTM"}'
```

The response includes the generated manifest ready to apply with `kubectl apply` or `terraform apply`.

## Configuration

All settings are configurable via environment variables with the `PLATFORMHUB_` prefix:

| Variable | Default | Description |
|---|---|---|
| `PLATFORMHUB_DATABASE_URL` | `sqlite+aiosqlite:///./platformhub.db` | Database connection string |
| `PLATFORMHUB_SECRET_KEY` | `change-me-in-production` | JWT signing key |
| `PLATFORMHUB_ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | Token expiry |
| `PLATFORMHUB_DEBUG` | `false` | Enable debug mode |

To use PostgreSQL instead of SQLite:

```bash
export PLATFORMHUB_DATABASE_URL="postgresql+asyncpg://user:pass@localhost/platformhub"
pip install asyncpg
```

## Architecture

```
platformhub/
├── main.py              # FastAPI app, lifespan, page routes
├── config.py            # Pydantic settings from env vars
├── database.py          # Async SQLAlchemy engine + session
├── models.py            # ORM: User, ResourceRequest, AuditLog
├── schemas.py           # Pydantic request/response schemas
├── auth.py              # JWT + bcrypt + RBAC dependencies
├── routers/
│   ├── auth.py          # Register, login
│   ├── catalog.py       # Resource catalog (K8s, S3, RDS)
│   ├── requests.py      # Request CRUD + audit trail
│   └── admin.py         # Approval workflow (approver/admin)
├── services/
│   ├── approval.py      # Review logic + state transitions
│   └── generator.py     # Jinja2 manifest rendering
└── templates/
    ├── manifests/       # Jinja2 templates for K8s YAML & Terraform HCL
    └── pages/           # HTML templates (HTMX + TailwindCSS)
```

## Development

```bash
# Run tests
pytest

# Run tests with coverage
pytest --cov=platformhub --cov-report=term-missing

# Lint
ruff check .

# Format
ruff format .

# Run dev server
uvicorn platformhub.main:app --reload
```

## License

Apache License 2.0 — see [LICENSE](LICENSE) for details.
