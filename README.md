# 🌿 ECO COMPANY Backend

FastAPI backend for ECO COMPANY website — clean water products & services.

## Tech Stack
- **FastAPI** 0.110 + **Uvicorn**
- **PostgreSQL** + **SQLAlchemy** 2.0 + **Alembic**
- **JWT** auth (python-jose + bcrypt)
- **Cloudinary** — file uploads
- **Anthropic Claude** — AI chatbot
- **Telegram Bot** — admin notifications
- **cPanel** deployment (Passenger WSGI)

## Quick Start (Local)

```bash
# 1. Virtual environment
python3.12 -m venv .venv
source .venv/bin/activate

# 2. Dependencies
pip install -r requirements.txt

# 3. Environment
cp .env.example .env
# Edit .env with real values

# 4. Database
alembic upgrade head
python scripts/seed.py

# 5. Run
uvicorn app.main:app --reload
```

Open [http://localhost:8000/docs](http://localhost:8000/docs) for Swagger UI.

## cPanel Deploy

```bash
# 1. cPanel → Setup Python App → Create
#    Python: 3.11/3.12, App root: ecocompany-backend

# 2. Terminal
cd ~/ecocompany-backend
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env && nano .env
alembic upgrade head
python scripts/seed.py

# 3. cPanel → Python App → Restart

# 4. Cron Job (Instagram token refresh, every 25 days)
#    0 0 */25 * * cd ~/ecocompany-backend && .venv/bin/python cron/instagram_refresh.py
```

## API Overview

| Group | Prefix | Endpoints |
|-------|--------|-----------|
| Auth | `/api/v1/auth` | login, me, logout, change-password |
| Products | `/api/v1/products` | list (paginated), featured, single |
| Categories | `/api/v1/categories` | list |
| Certificates | `/api/v1/certificates` | list |
| Gallery | `/api/v1/gallery` | albums, album detail |
| Contacts | `/api/v1/contacts` | submit (rate limited) |
| Settings | `/api/v1/settings` | public key-value |
| Instagram | `/api/v1/instagram` | cached posts |
| Chat | `/api/v1/chat` | AI chatbot |
| Admin | `/api/v1/admin/*` | Full CRUD for all entities |

## Default Admin

```
Email: admin@ecocompany.uz
Password: Admin123!
```

## Project Structure

```
app/
├── config.py          # Pydantic Settings
├── database.py        # SQLAlchemy engine
├── main.py            # FastAPI app
├── models/            # 11 SQLAlchemy models
├── schemas/           # 9 Pydantic schema modules
├── routers/           # Public API routers
│   └── admin/         # Admin CRUD routers
├── services/          # Business logic (7 services)
├── middleware/        # Error handler, logging, security
├── dependencies/      # Auth dependencies
└── utils/             # Hashing, pagination, sanitize
```
