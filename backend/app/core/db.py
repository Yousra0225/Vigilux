from sqlmodel import SQLModel, create_engine, Session

from app.core.config import settings

# Create the engine
# check_same_thread is needed for SQLite, not PostgreSQL, but good to know
engine = create_engine(settings.DATABASE_URL, echo=settings.DEBUG)

def get_session() -> Session:
    """Dependency to get a database session."""
    with Session(engine) as session:
        yield session

def init_db():
    """Create the database tables."""
    SQLModel.metadata.create_all(engine)
