# saarTURNier – Gymnastics Competition Scoring System

A modern web-based scoring system for gymnastics competitions, enabling judges to score routines in real-time, organizers to manage competitions, and audiences to view live results.

**Status**: In Development (Sprint 1)  
**Target Launch**: 22 August 2026  
**Tech Stack**: Python FastAPI + React 18 + Next.js 14 + MariaDB

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+ LTS**
- **Docker & Docker Compose** (for local development)
- **Git**

### Local Development Setup (One Command)

```bash
# Clone and set up everything
bash scripts/dev-setup.sh

# Then start the development environment
docker-compose up

# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Manual Setup

**Backend**:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
export DATABASE_URL=mysql+pymysql://root:root@localhost:3306/saarturnier
alembic upgrade head
pytest tests/
```

**Frontend**:
```bash
cd frontend
npm install
npm run dev
```

**Database**:
```bash
docker run -d \
  -e MARIADB_ROOT_PASSWORD=root \
  -e MARIADB_DATABASE=saarturnier \
  -p 3306:3306 \
  mariadb:10.6
```

---

## Project Structure

```
saarTURNier/
├── backend/              # Python FastAPI backend
│   ├── app/             # Application code
│   ├── alembic/         # Database migrations
│   ├── tests/           # Unit & integration tests
│   └── requirements.txt # Python dependencies
├── frontend/            # React + Next.js frontend
│   ├── src/
│   │   ├── app/         # Next.js pages
│   │   ├── components/  # React components
│   │   ├── stores/      # Zustand state stores
│   │   └── hooks/       # React Query hooks
│   └── package.json     # Node.js dependencies
├── scripts/             # Deployment & setup scripts
├── docs/                # Documentation
├── docker-compose.yml   # Local dev environment
└── .github/workflows/   # CI/CD pipelines
```

---

## Key Features

### For Judges
- Real-time score entry (Difficulty, Execution, Neutral deductions)
- Live calculation of total scores
- Edit/delete routines before submission
- Apparatus completion tracking
- Connection status indicator + auto-retry on network loss

### For Organizers
- Create and manage competitions
- Assign teams to rotation groups (1–4 per competition)
- Manage judges panel credentials
- Control rotation state (PENDING → ACTIVE → COMPLETED)
- Edit any score anytime with audit trail
- View apparatus completion status
- Export results (CSV, print-friendly)

### For Public / Spectators
- View published scores (read-only)
- Real-time leaderboard updates
- Results by apparatus pair
- Responsive design (mobile, tablet, desktop)
- No login required

---

## Architecture

### Backend (Python FastAPI)
- **Async-first** with SQLAlchemy 2.0 ORM
- **JWT authentication** (judges & organizers)
- **RESTful API** with Pydantic schemas
- **State machine** for rotation lifecycle
- **Alembic migrations** for database versioning

### Frontend (React + Next.js)
- **Server-side rendering** with Next.js 14
- **Type-safe** with TypeScript
- **State management**: Zustand (UI) + React Query (server state)
- **HTTP Polling** for real-time updates (v1)
- **Tailwind CSS** + Shadcn/ui component library

### Database (MariaDB)
- **Window functions** for efficient score aggregation
- **JSON data type** for flexible apparatus data
- **Unique constraints** for fairness invariant (each apparatus scored by exactly one panel)

### Deployment
- **Git-based** deployment (no Docker on production)
- **Nginx** reverse proxy
- **Systemd** service management
- **GitHub Actions** CI/CD (tests on every push)

---

## Development Workflow

### 1. Create a Feature Branch
```bash
git checkout mvp
git pull origin mvp
git checkout -b feature/your-feature-name
```

### 2. Make Changes & Test Locally
```bash
# Backend tests
cd backend && pytest tests/ -v

# Frontend tests
cd frontend && npm run test

# Run locally
docker-compose up
```

### 3. Commit & Push
```bash
git add .
git commit -m "feat: description of changes"
git push origin feature/your-feature-name
```

### 4. Create Pull Request
- Push your branch to GitHub
- Create PR against `mvp` branch
- Wait for CI/CD checks to pass
- Request review from team members
- Merge when approved

---

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
# Coverage report: htmlcov/index.html
```

### Frontend Tests
```bash
cd frontend
npm run test:coverage
# Coverage report: coverage/index.html
```

### Run All Tests Locally
```bash
# Both backend and frontend tests
docker-compose exec backend pytest tests/ -v
docker-compose exec frontend npm run test
```

---

## Documentation

- **[Implementation Plan](docs/saarTURNier_Implementation_Plan_v1.0.md)** — 8-sprint roadmap, success criteria
- **[Planning Document](docs/saarTURNier_Planning_v1.5.md)** — Domain model, requirements, rules
- **[Architecture](docs/ARCHITECTURE.md)** — Design decisions, patterns, workflows
- **[API Reference](docs/API_ENDPOINTS.md)** — REST endpoints (auto-generated from Swagger)
- **[Database Schema](docs/DATABASE_SCHEMA.md)** — Table structure, migrations
- **[Deployment Guide](docs/DEPLOYMENT.md)** — Hosting setup, production checklist

---

## Git Branches

- **`mvp`** — Active development (default branch for PRs)
- **`main`** — Production-ready (merges only from mvp after testing)

**CI/CD runs on**:
- All commits to `mvp` and `main`
- All PRs to `main`

---

## Contributing

1. Work on `mvp` branch or feature branches
2. Write tests for new features
3. Ensure all tests pass locally (`pytest`, `npm run test`)
4. Create PR against `mvp`
5. Get team review before merging
6. CI/CD checks must pass

---

## Timeline

| Sprint | Duration | Focus |
|--------|----------|-------|
| 1 | May 12–26 | Infrastructure, database schema |
| 2 | May 27–Jun 9 | Backend auth, score CRUD |
| 3 | Jun 10–23 | Rotation state machine |
| 4 | Jun 24–Jul 7 | Team/rotation group management |
| 5 | Jul 8–21 | Organizer APIs, frontend setup |
| 6 | Jul 22–Aug 4 | Judges panel UI, polling |
| 7 | Aug 5–18 | Organizer UI, public results |
| 8 | Aug 19–22 | Testing, deployment, buffer |

**Target Launch**: 22 August 2026

---

## Team Contacts

- **Backend Lead**: [TBD]
- **Frontend Lead**: [TBD]
- **Project Owner**: [TBD]

---

## License

[See LICENSE file](LICENSE)

---

## Support

For questions or issues:
1. Check [documentation](docs/) first
2. Create a GitHub Issue
3. Reach out to team lead

---

**Last Updated**: 13 May 2026  
**Status**: Sprint 1 In Progress