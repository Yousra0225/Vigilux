# Architecture Overview - Vigilux

## System Design

Vigilux follows a decoupled client-server architecture.

### Backend (FastAPI)

The backend is structured using **Clean Architecture** principles:
- **`app/api`**: Entry points, route definitions, and request/response handling.
- **`app/core`**: Global configuration, security settings (JWT), and database connection.
- **`app/models`**: Database schemas using SQLModel.
- **`app/services`**: Business logic (Scoring, Quota management, Notification dispatching).
- **`app/repositories`**: Data access abstraction (CRUD operations).

### Frontend (Next.js)

- **Framework**: Next.js 14 with App Router.
- **State Management**: React Context for Authentication.
- **UI Components**: Custom components built with Tailwind CSS and Lucide React.
- **Data Fetching**: Axios with interceptors for JWT handling.

### Data Model

- **User**: Authentication and Plan management (Starter, Growth, Ultimate).
- **Project**: A user's workspace containing tracked competitors.
- **Competitor**: Tracked entities with name, URL, and threat score.
- **Event**: Individual movements detected for competitors (Price change, New feature, etc.).
- **NotificationSetting**: Per-user configuration for alert channels (Email, SMS, Slack, etc.).

## Infrastructure

- **Containerization**: Docker Compose manages three main services: `db` (Postgres), `api` (Backend), and `web` (Frontend).
- **CI/CD**: GitHub Actions automates linting and testing for both stacks on every push to `main` or `develop`.
- **Security**: JWT-based authentication with password hashing using Bcrypt. CORS is configured to allow communication between frontend and backend.

## Scalability Considerations

- **Asynchronous Processing**: FastAPI's async nature allows for high concurrency.
- **Stateless API**: The backend can be scaled horizontally behind a load balancer.
- **Database**: PostgreSQL is used for structured data, ensuring ACID compliance.
