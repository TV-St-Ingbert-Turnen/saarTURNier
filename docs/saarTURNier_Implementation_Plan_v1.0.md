# saarTURNier Implementation Plan v1.0

**Status**: Production-Ready Plan  
**Created**: 13 May 2026  
**Target Go-Live**: 22 August 2026 (102 days)  
**Team Size**: 1–2 developers  
**Concurrent Users**: 100–300 (20 judges, 10 organizers, 300 public viewers)

---

## Executive Summary

Build a complete gymnastics competition scoring system using **Python FastAPI** (backend) + **React 18 + Next.js** (frontend) + **MariaDB** (database), deployed via Git on la-webhosting.de shared hosting. Full v1.5 feature set production-ready by 22 August 2026.

---

## Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Backend Framework | Python FastAPI 0.104+ | Async-native, minimal boilerplate |
| Backend ORM | SQLAlchemy 2.0+ | Async support, MariaDB-compatible |
| Auth | Python-Jose + Passlib | JWT tokens, industry standard |
| Web Server | Gunicorn + Uvicorn | Production ASGI server |
| Frontend Framework | React 18 + TypeScript | Team expertise, excellent ecosystem |
| Meta-Framework | Next.js 14 (App Router) | Built-in optimizations, static export |
| State Management | Zustand + React Query | Simpler than Redux, great DevTools |
| Database | MariaDB 10.3+ (shared hosting) | JSON support, window functions, shared hosting compatible |
| Real-Time (v1) | HTTP Polling (2–5 sec) | Simple on shared hosting, sufficient for 100–300 users |
| Real-Time (v2) | WebSocket + Redis | Upgrade path (post-competition) |
| Deployment | Git + systemd | No Docker; simple on shared hosting |
| CI/CD | GitHub Actions | Tests on push, optional SSH deploy |
| UI Components | Shadcn/ui + Tailwind CSS | Unstyled + utility CSS |
| Testing (Backend) | Pytest + async fixtures | >80% coverage target |
| Testing (Frontend) | Vitest + React Testing Library | >70% coverage target |

---

## Core Features (v1 Production)

### Judges Panel UI
- Login with panel credentials (men/women assignment)
- Score entry: Athlete name, Difficulty (D), Execution (E), Neutral deductions
- **Live calculation**: Total = D + E − Neutral (immediate feedback)
- Edit/delete own routines
- Mark apparatus complete (transitions judges panel side from OPEN → COMPLETED)
- Connection status indicator (polling 3–5 sec intervals)
- Handles connection loss gracefully (show warning, auto-retry)

### Organizer/Admin UI
- **Competition Setup**:
  - Create competition (name, date, location)
  - Create/manage teams (assign to rotation groups)
  - Create rotation groups (1–4 per competition)
  - Assign judges panels to apparatus (fairness invariant enforcement)
- **Rotation Management**:
  - Start rotation (PENDING → ACTIVE)
  - End rotation (ACTIVE → COMPLETED, auto-publish results)
  - View rotation status + apparatus completion progress
- **Score Management**:
  - Edit any score anytime (organizer override)
  - View all scores (table: team, athlete, apparatus, D, E, neutral, total)
  - Reopen apparatus sides (COMPLETED → OPEN, only while rotation ACTIVE)
  - Audit log: view all organizer edits (before/after values, timestamp, user)
- **Judges Panel Credentials**:
  - Create judges panels (login, password, panel type)
  - Reset credentials (generate new password)
- **Results Export**:
  - CSV export (team, apparatus pair, score, rank)
  - Print-friendly HTML view

### Public Results Page
- View published scores (read-only, no login)
- Leaderboard by team total
- Results by apparatus pair
- Responsive design (mobile/tablet/desktop, touch-friendly)
- Polling updates (5–10 sec intervals)

### Score Aggregation Logic
**Best 2 of 3 per gender, per apparatus, per team**:
1. Collect all routines (0–3) for team × rotation × apparatus × gender
2. Sort by score descending
3. Select top 2 (or fewer if <2 exist)
4. Sum selected scores
5. **Apparatus pair result** = Men's subtotal + Women's subtotal
6. **Team total** = Sum of all apparatus pair results

**SQL (MariaDB window functions)**:
```sql
SELECT 
    team_id, 
    SUM(score) as gender_subtotal
FROM (
    SELECT 
        team_id, 
        routine_id, 
        total as score,
        ROW_NUMBER() OVER (PARTITION BY team_id ORDER BY total DESC) as rank
    FROM routines
    WHERE rotation_id = ? AND apparatus_pair_id = ? AND gender = ?
) ranked
WHERE rank <= 2
GROUP BY team_id;
```

### State Machine

**Rotation States** (immutable, irreversible):
```
PENDING → ACTIVE → COMPLETED
```
- **PENDING**: Rotation not started, judges panels INACTIVE
- **ACTIVE**: Judges panels can score (state = OPEN)
- **COMPLETED**: Rotation ended by organizer, all judges panels locked, results published

**Judges Panel Side States**:
```
INACTIVE → OPEN ↔ COMPLETED
```
- **INACTIVE**: Rotation not started yet
- **OPEN**: Rotation ACTIVE, judges can enter/edit scores
- **COMPLETED**: Judges marked complete; can reopen only while rotation ACTIVE
- **Re-open Rules**: Only by organizer, only if rotation ACTIVE, transitions COMPLETED → OPEN

**Apparatus Pair State** (derived):
- COMPLETED iff both men's and women's judges panel sides are COMPLETED

### Fairness Invariant (Critical)

**Rule**: Each apparatus (gender-specific) scored by exactly one judges panel throughout entire competition.

**Enforcement**:
- Database unique constraint: `apparatus_assignments(competition_id, apparatus_pair_id, gender)`
- Application validation: prevent reassignment after first assignment
- Checked at apparatus assignment time (during competition setup)

---

## 8-Sprint Implementation Schedule (102 Days)

### Sprint 1: Infrastructure & Database (Weeks 1–2, May 12–26)
**Deliverables**: Dev environment ready, database schema designed

- [ ] GitHub repo setup (`.gitignore`, branch protection, CI/CD templates)
- [ ] Docker Compose setup (FastAPI + MariaDB local dev)
- [ ] FastAPI project skeleton (async app, CORS, error handling)
- [ ] SQLAlchemy 2.0 async configuration
- [ ] Alembic migration system setup
- [ ] Database schema design + initial migration:
  - `competitions, teams, rotation_groups, apparatus_pairs, rotations`
  - `judges_panels, judges_panel_sides, routines, scores_audit`
- [ ] Connection testing + schema validation
- [ ] `.env.example` template (DB creds, JWT secret, CORS settings)

**Output**: `docker-compose up` → fully functional local dev environment

---

### Sprint 2: Backend Auth & Core Scoring (Weeks 3–4, May 27–Jun 9)
**Deliverables**: Auth layer, score CRUD, tests passing

- [ ] JWT authentication system:
  - Login endpoints: judges panels, organizers
  - Token validation middleware, role-based access control (RBAC)
- [ ] SQLAlchemy models (all core entities)
- [ ] Core API endpoints:
  - `POST /api/auth/judges-login` → JWT token
  - `POST /api/auth/organizer-login` → JWT token
  - `POST /api/routines` → create routine
  - `PUT /api/routines/{id}` → update routine
  - `GET /api/routines?rotation_id=...` → list routines
  - `DELETE /api/routines/{id}` → delete routine
- [ ] Pytest test suite: auth flow, CRUD operations, role validation

---

### Sprint 3: Rotation State Machine & Judges Panel Management (Weeks 5–6, Jun 10–23)
**Deliverables**: State machine logic, judges panel completion

- [ ] Rotation state transitions:
  - `POST /api/competitions/{id}/rotations` → create (PENDING)
  - `PUT /api/rotations/{id}/start` → PENDING → ACTIVE
  - `PUT /api/rotations/{id}/end` → ACTIVE → COMPLETED (validate all apparatus complete)
- [ ] Judges panel side management:
  - `PUT /api/judges-panel-sides/{id}/complete` → OPEN → COMPLETED
  - `PUT /api/judges-panel-sides/{id}/reopen` → COMPLETED → OPEN (organizer only, rotation ACTIVE)
  - `GET /api/judges-panel/active-rotation` → current rotation + assigned apparatus
- [ ] Score aggregation service (best 2 of 3 per gender)
- [ ] Pytest tests: state transitions, edge cases (0, 1, 2, 3 routines)

---

### Sprint 4: Team & Rotation Group Management (Weeks 7–8, Jun 24–Jul 7)
**Deliverables**: Full team setup API, fairness invariant enforcement

- [ ] Team management:
  - `POST /api/competitions/{id}/teams` → create team
  - `GET /api/competitions/{id}/teams` → list teams
  - `PUT /api/teams/{id}` → update team (change group)
  - `DELETE /api/teams/{id}` → delete team (validation: no scores)
- [ ] Rotation group management:
  - `POST /api/competitions/{id}/rotation-groups` → create group
  - `GET /api/competitions/{id}/rotation-groups` → list groups
  - `PUT /api/rotation-groups/{id}` → update group
  - `DELETE /api/rotation-groups/{id}` → delete group
- [ ] Apparatus assignment + fairness invariant:
  - `POST /api/competitions/{id}/apparatus-assignments` → assign judges panel to apparatus
  - Database constraint: unique (competition, apparatus_pair_id, gender)
  - `GET /api/competitions/{id}/apparatus-assignments` → verify assignments
- [ ] Pytest tests: team constraints, fairness invariant

---

### Sprint 5: Organizer Score Management & Frontend Setup (Weeks 9–10, Jul 8–21)
**Deliverables**: Score edits + audit trail, frontend infrastructure ready

- [ ] Backend:
  - `PUT /api/scores/{routine_id}` → organizer edit score
  - `scores_audit` table + logging
  - `GET /api/scores/audit?competition_id=...` → audit log
  - Publishing logic: end rotation → publish results
- [ ] Frontend scaffolding:
  - Next.js 14 + React 18 + TypeScript setup
  - Zustand stores (auth, UI state)
  - React Query + Axios setup (with JWT interceptor)
  - Tailwind CSS + Shadcn/ui
  - Folder structure: `/app`, `/components`, `/stores`, `/hooks`, `/api`

---

### Sprint 6: Judges Panel UI (Weeks 11–12, Jul 22–Aug 4)
**Deliverables**: Judges can score, polling works

- [ ] Frontend pages:
  - `/judges/login` (login form)
  - `/judges/dashboard` (rotation state + assigned apparatus + score list)
- [ ] Components:
  - `ScoreEntryForm`: D, E, neutral inputs + live total calculation
  - `RoutineList`: table with edit/delete buttons
  - `ApparatusStatus`: show side state (INACTIVE/OPEN/COMPLETED)
  - `ConnectionStatus`: polling indicator (green/red)
- [ ] Polling mechanism:
  - Judge polls `/api/judges-panel/scores-feed` every 3–5 sec
  - Response: updated routines, rotation status, apparatus completion flags
  - Connection loss: show warning if no poll for >10 sec
- [ ] Form validation (client + server)

---

### Sprint 7: Organizer UI (Weeks 13–14, Aug 5–18)
**Deliverables**: Organizer can manage full competition lifecycle

- [ ] Frontend pages:
  - `/admin/login` (login form)
  - `/admin/competitions` (list, create new)
  - `/admin/competitions/{id}` (detail with tabs)
- [ ] Tabs:
  - **Teams**: add/remove/edit teams, assign to groups
  - **Apparatus**: show assignments, manage judges panel assignments
  - **Rotations**: start/end rotations, view completion status
  - **Scores**: view/edit all scores, filter by rotation/apparatus
  - **Audit Log**: view all organizer edits
  - **Judges**: create/reset judges panel credentials
- [ ] Results export (CSV, print view)

---

### Sprint 8: Public Results UI & Launch (Aug 5–18)
**Deliverables**: Public results, integration tests, deployment

- [ ] Frontend pages:
  - `/` (public results homepage)
  - `/results/{competition_id}` (published results by competition)
- [ ] Components:
  - `ResultsLeaderboard`: team scores sorted by total
  - `ApparatusResultsTable`: show each team's score per apparatus pair
- [ ] Responsive design (mobile/tablet/desktop, touch-friendly)
- [ ] Polling: public results update every 5–10 sec
- [ ] Integration tests (end-to-end flow)
- [ ] Load testing: 20 judges + 10 organizers + 300 public viewers
- [ ] Deployment to la-webhosting.de:
  - Pre-deployment hosting setup (verify Python 3.11+, Node.js, MariaDB)
  - Git clone/pull, install dependencies, run migrations
  - Nginx reverse proxy config
  - Systemd service setup (Gunicorn auto-start)
  - Post-deployment verification (test all endpoints)
- [ ] Buffer for fixes (Aug 19–21), final sign-off (Aug 22)

---

## Deployment Architecture (Git-Based, No Docker)

### Development
- Local machine: Docker Compose (FastAPI + MariaDB + Node.js)
- Develop, test, commit, push to GitHub

### Production
- **Method**: Git clone/pull on hosting
- **Hosting**: la-webhosting.de shared hosting
- **Components**:
  - Backend: Gunicorn (ASGI server) on port 8000
  - Frontend: Next.js static export (`out/` directory)
  - Database: MariaDB (managed by hosting or self-managed)
  - Reverse Proxy: Nginx (routes `/api/*` → FastAPI, `/*` → static files)
  - Process Manager: systemd (auto-restart services)

### Deployment Flow
```
1. Local dev: docker-compose up
2. Commit changes: git commit + git push
3. On hosting: git pull origin main
4. Install deps: pip install -r requirements.txt, npm install
5. Build frontend: npm run build
6. Migrations: alembic upgrade head
7. Restart services: systemctl restart saarturnier-api
```

### One-Time Hosting Setup
1. SSH into hosting, verify Python 3.11+ and Node.js LTS available
2. Clone repo: `git clone https://github.com/yourorg/saarturnier.git ~/saarturnier`
3. Install dependencies + build
4. Create `.env` with secrets (DB creds, JWT key)
5. Configure Nginx reverse proxy
6. Set up systemd unit for Gunicorn
7. Set up health check cron job (every 5 min)

---

## Load Testing (Sprint 9)

**Realistic Concurrency**:
- 20 judges (polling every 3–5 sec)
- 10 organizers (polling every 2 sec)
- 300 public viewers (polling every 5–10 sec)
- **Total**: ~330 concurrent users

**Expected Load**:
- ~39 requests/second sustained (well within shared hosting)
- Database response time: <200ms per query
- Payload per request: 1–5 KB

**Test Scenarios**:
- [ ] Create competition, add teams, assign groups
- [ ] Assign judges panels to apparatus (test fairness invariant)
- [ ] Start rotation (PENDING → ACTIVE)
- [ ] Judges enter 3 routines per apparatus
- [ ] Best 2 appear in results
- [ ] Judges mark apparatus complete
- [ ] Organizer edits score (audit logged)
- [ ] Organizer ends rotation (ACTIVE → COMPLETED, publish)
- [ ] Public view shows published scores
- [ ] Judges try to enter more scores (should fail—rotation COMPLETED)

**Success Criteria**:
- All functional tests pass
- Response time <200ms for typical queries
- No connection pool exhaustion
- Zero unhandled errors in browser console

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| 102-day deadline tight | Phased sprints; parallel work; prioritize core features first |
| Database query performance | Use window functions; add indexes early; load test Sprint 9 |
| Shared hosting resource limits | Monitor CPU/memory; optimize queries; single instance initially |
| Judges lose connectivity | Polling with visible status; v2 adds offline buffer |
| State machine bugs | Comprehensive tests early; explicit state enums; CI/CD catches regressions |
| Python/Node versions missing | Pre-deployment checklist: verify runtimes on hosting |
| Database deployment errors | Test migrations locally; have rollback script |
| SSH credentials leak | Use `.env` file (not in repo); keep secrets off Git; rotate keys post-launch |

---

## Success Criteria (22 August 2026)

### Functional
- [ ] Judges can log in, see assigned apparatus, enter scores (D, E, neutral)
- [ ] Live calculation displays correctly (Total = D + E − Neutral)
- [ ] Organizers can create competition, manage teams, assign rotation groups
- [ ] Organizers can assign judges panels to apparatus (fairness invariant enforced)
- [ ] Organizers can start/end rotations
- [ ] Organizers can edit any score anytime (audit logged)
- [ ] Score aggregation: best 2 of 3 per gender (verified by tests)
- [ ] Public can view published results (no login)
- [ ] Polling updates: judges 3–5 sec, organizers 2 sec, public 5–10 sec
- [ ] Connection loss: show warning, auto-retry
- [ ] Rotation state never moves backward (immutable)

### Non-Functional
- [ ] System handles 100–300 concurrent users (20 judges + 10 organizers + 300 public viewers)
- [ ] Response time <200ms for typical queries
- [ ] Frontend bundle <500KB (gzipped)
- [ ] All tests passing: backend >80%, frontend >70%
- [ ] Zero unhandled promise rejections in browser

### Deployment
- [ ] System deployed to la-webhosting.de
- [ ] Nginx reverse proxy working
- [ ] Database migrations successful
- [ ] GitHub Actions CI/CD pipeline functional
- [ ] Deployment script works (`git pull + build + restart`)
- [ ] All endpoints verified on live server

---

## Post-Competition (v2, Future)

**Deferred to after 22 August**:
- ⏸ WebSocket real-time updates (replace polling)
- ⏸ Offline tablet buffering with auto-sync
- ⏸ Advanced scaling (multi-instance + Redis)
- ⏸ UX refinements & mobile optimization
- ⏸ API versioning, deprecation strategy

---

## Documentation & Artifacts

**Backend**:
- API documentation (Swagger/OpenAPI auto-generated)
- Database schema diagram (from Alembic migrations)
- Service layer architecture (business logic patterns)

**Frontend**:
- Component library (Storybook stories or component documentation)
- State management guide (Zustand stores + React Query hooks)
- Polling strategy documentation (latency, retry logic, connection handling)

**Deployment**:
- Hosting setup runbook (one-time SSH commands)
- Deployment script (`scripts/deploy.sh`)
- Production troubleshooting guide (common issues + fixes)
- Health check monitoring (cron job + alerting)

**Testing**:
- Load testing results (concurrent user capacity verified)
- Test coverage report (backend >80%, frontend >70%)
- Integration test checklist (end-to-end scenarios)

---

## Next Immediate Steps

1. **Create GitHub Repository**
   - Set up `.gitignore` (Python, Node.js, .env)
   - Create branch protection rules (require reviews, pass CI)
   - Initialize CI/CD template (GitHub Actions)

2. **Sprint 1 Kickoff (May 12–26)**
   - Set up Docker Compose local dev environment
   - Design database schema in Alembic
   - Create initial migration + test

3. **Team Assignment**
   - Backend lead: Sprints 2–5 (auth, state machine, team/rotation APIs)
   - Frontend lead: Sprints 5–8 (React components, forms, polling)
   - Overlap in Sprints 5–8 for integration

4. **Weekly Standups**
   - Track progress, unblock issues
   - Adjust scope if needed (prioritize core over nice-to-have)

---

## References

- v1.5 Planning Document: `saarTURNier_Planning_v1.5.md`
- v1.0 Architecture: This document
- Implementation status: GitHub repo (branches by sprint)

---

**Plan Status**: ✅ Approved, Ready to Execute  
**Created**: 13 May 2026  
**Prepared By**: GitHub Copilot  
**Target Launch**: 22 August 2026

---

**End of Document**
