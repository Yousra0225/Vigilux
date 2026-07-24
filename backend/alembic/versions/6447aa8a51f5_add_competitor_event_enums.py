"""Add_competitor_event_enums

Revision ID: 6447aa8a51f5
Revises: 89a8eb33fab5
Create Date: 2026-01-30 00:10:15.249422

"""
from collections.abc import Sequence

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = '6447aa8a51f5'
down_revision: str | None = '89a8eb33fab5'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create new ENUM types
    tracking_status_enum = postgresql.ENUM('ACTIVE', 'ARCHIVED', name='trackingstatus')
    tracking_status_enum.create(op.get_bind())
    
    event_type_enum = postgresql.ENUM('PRICE', 'FEATURE', 'HEALTH', 'NEW_ENTRANT', name='eventtype')
    event_type_enum.create(op.get_bind())

    # Alter columns to use new types
    # Note: explicit cast might be needed if data exists, but assuming empty/compatible for now.
    # Postgres requires 'USING status::text::trackingstatus' if types are incompatible.
    
    op.execute('ALTER TABLE competitor ALTER COLUMN status TYPE trackingstatus USING status::text::trackingstatus')
    op.execute('ALTER TABLE event ALTER COLUMN type TYPE eventtype USING type::text::eventtype')
    
    # Drop old ENUM type if exists
    op.execute('DROP TYPE competitorstatus')


def downgrade() -> None:
    # Create old ENUM type
    competitor_status_enum = postgresql.ENUM('active', 'archived', name='competitorstatus')
    competitor_status_enum.create(op.get_bind())

    # Revert columns
    op.execute('ALTER TABLE competitor ALTER COLUMN status TYPE competitorstatus USING status::text::competitorstatus')
    op.alter_column('event', 'type',
               type_=sa.VARCHAR(),
               existing_nullable=False)

    # Drop new ENUM types
    op.execute('DROP TYPE trackingstatus')
    op.execute('DROP TYPE eventtype')