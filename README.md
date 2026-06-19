# Startup Success Prediction Platform

A full-stack, AI-powered solution that equips investors, founders, and incubators with data-driven forecasts, risk assessments, and beautiful investment reports.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12+, FastAPI (ASGI) |
| **Frontend** | React 18 + TypeScript + Tailwind CSS |
| **Database** | PostgreSQL 15 + SQLAlchemy 2.x + Alembic |
| **ML** | Scikit-Learn, XGBoost, LightGBM, Optuna |
| **PDF** | ReportLab |
| **Container** | Docker + Docker Compose |
| **CI/CD** | GitHub Actions |

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── core/          # Config, DB, Security, Dependencies
│   │   ├── models/        # SQLAlchemy ORM models (9 tables)
│   │   ├── schemas/       # Pydantic request/response models
│   │   ├── routers/       # API endpoints (auth, startup, predict, report, dashboard)
│   │   ├── services/      # Business logic layer
│   │   ├── ml/            # Feature engineering, model training, data ingestion
│   │   └── main.py        # FastAPI app entry point
│   ├── tests/             # 63 tests — 100% coverage
│   └── Dockerfile
├── frontend/
│   ├── src/               # React components, pages, services, types
│   └── Dockerfile
├── docker-compose.yml     # API, Frontend, PostgreSQL, Redis
└── .github/workflows/     # CI/CD pipeline
```

## Quick Start

### Prerequisites

- Python 3.12+
- Node.js 20+
- Docker (optional)

### Backend

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v    # 63 tests — all pass
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Docker

```bash
docker compose up --build
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Create account |
| POST | `/auth/login` | Login (JWT) |
| POST | `/startup` | Create startup profile |
| GET | `/startup/{id}` | Get startup details |
| PUT | `/startup/{id}` | Update startup (admin) |
| DELETE | `/startup/{id}` | Soft-delete startup (admin) |
| POST | `/predict/success` | Success probability (0–100%) |
| POST | `/predict/growth` | Revenue growth forecast (1y/3y/5y) |
| POST | `/predict/risk` | Risk scores (financial, operational, market, team) |
| POST | `/report/generate` | Generate AI investment PDF report |
| GET | `/dashboard` | Aggregated dashboard data |
| GET | `/similar?startup_id=X&n=5` | Top-N similar startups |
| GET | `/health` | Liveness probe |

## Test Coverage

**100%** — 63 tests covering all 808 statements across 45 source files:

```
Name                                 Stmts   Miss  Cover
app/core/config.py                      23      0   100%
app/core/database.py                    31      0   100%
app/core/dependencies.py                22      0   100%
app/core/security.py                    26      0   100%
app/main.py                             16      0   100%
app/middleware.py                       20      0   100%
app/ml/data_ingestion.py                18      0   100%
app/ml/feature_engineering.py           35      0   100%
app/ml/model_loader.py                  20      0   100%
app/ml/model_training.py                46      0   100%
app/routers/*.py                       114      0   100%
app/services/*.py                      274      0   100%
... and 12 more files ...
TOTAL                                  808      0   100%
```

## License

MIT
