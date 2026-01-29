"""Initial schema

Revision ID: 89a8eb33fab5
Revises: 
Create Date: 2026-01-29 23:50:56.272140

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '89a8eb33fab5'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # User
    op.create_table('user',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('email', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('hashed_password', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('plan_type', sa.Enum('starter', 'growth', 'ultimate', name='plantype'), nullable=False),
        sa.Column('trial_start_date', sa.DateTime(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_email'), 'user', ['email'], unique=True)
    op.create_index(op.f('ix_user_id'), 'user', ['id'], unique=False)

    # Project
    op.create_table('project',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('url', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_project_id'), 'project', ['id'], unique=False)

    # Competitor
    op.create_table('competitor',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('project_id', sa.Uuid(), nullable=False),
        sa.Column('name', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('url', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('status', sa.Enum('active', 'archived', name='competitorstatus'), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['project_id'], ['project.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_competitor_id'), 'competitor', ['id'], unique=False)

    # Event
    op.create_table('event',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('competitor_id', sa.Uuid(), nullable=False),
        sa.Column('type', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('description', sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column('score', sa.Float(), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['competitor_id'], ['competitor.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_event_id'), 'event', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_event_id'), table_name='event')
    op.drop_table('event')
    op.drop_index(op.f('ix_competitor_id'), table_name='competitor')
    op.drop_table('competitor')
    op.drop_index(op.f('ix_project_id'), table_name='project')
    op.drop_table('project')
    op.drop_index(op.f('ix_user_id'), table_name='user')
    op.drop_index(op.f('ix_user_email'), table_name='user')
    op.drop_table('user')
    # Drop enums
    sa.Enum(name='competitorstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='plantype').drop(op.get_bind(), checkfirst=True)