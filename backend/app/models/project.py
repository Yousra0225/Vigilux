import uuid
from typing import TYPE_CHECKING

import uuid6
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .competitor import Competitor
    from .user import User

class Project(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid6.uuid7, primary_key=True, index=True, nullable=False)
    user_id: uuid.UUID = Field(foreign_key="user.id", nullable=False)
    url: str = Field(nullable=False)
    description: str | None = Field(default=None)

    user: "User" = Relationship(back_populates="projects")
    competitors: list["Competitor"] = Relationship(back_populates="project")
