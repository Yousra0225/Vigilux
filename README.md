# Vigilux

AI-powered competitive intelligence platform. Vigilux monitors your competitors and provides real-time insights and alerts based on market movements.

## Tech Stack

- **Backend:** FastAPI, SQLModel (SQLAlchemy + Pydantic), PostgreSQL, Alembic, JWT Auth.
- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Lucide React, Recharts, Sonner.
- **DevOps:** Docker, Docker Compose, GitHub Actions.
- **Testing:** Pytest (Backend), Vitest (Frontend), Playwright (E2E).

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Node.js 18+ (optional, for local frontend dev)
- Python 3.11+ (optional, for local backend dev)

### Running with Docker

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/vigilux.git
   cd vigilux
   ```

2. Start the services:
   ```bash
   docker-compose up --build
   ```

3. Access the applications:
   - **Frontend:** [http://localhost:3000](http://localhost:3000)
   - **API Backend:** [http://localhost:8000](http://localhost:8000)
   - **API Documentation (Swagger):** [http://localhost:8000/docs](http://localhost:8000/docs)

### Database Seeding

To seed the database with test data (users, projects, competitors):
```bash
docker-compose exec api python -m app.db.seed
```
*Seeded Users:*
- `starter@example.com` / `password123`
- `growth@example.com` / `password123`
- `ultimate@example.com` / `password123`

## Testing

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### End-to-End Tests (Playwright)
```bash
cd e2e
npm install
npx playwright install chromium
npm test
```

## Documentation

- [Architecture Overview](./docs/ARCHITECTURE.md)
