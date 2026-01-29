import uuid
from typing import Optional, List, TYPE_CHECKING
from sqlmodel import Field, SQLModel, Relationship
import uuid6

if TYPE_CHECKING:
    from .user import User
    from .competitor import Competitor

class Project(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid6.uuid7, primary_key=True, index=True, nullable=False)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    url: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)

    user: "User" = Relationship(back_populates="projects")
    competitors: List["Competitor"] = Relationship(back_populates="project")
