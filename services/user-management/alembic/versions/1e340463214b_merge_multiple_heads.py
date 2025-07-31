"""Merge multiple heads

Revision ID: 1e340463214b
Revises: 22130e9524da, add_refresh_tokens
Create Date: 2025-07-23 11:12:37.610898

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1e340463214b'
down_revision: Union[str, Sequence[str], None] = ('22130e9524da', 'add_refresh_tokens')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
