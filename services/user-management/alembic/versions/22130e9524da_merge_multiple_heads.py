"""Merge multiple heads

Revision ID: 22130e9524da
Revises: 15eda0c5b884, add_image_urls_to_user, add_timestamps_to_roles, 12345678abcd
Create Date: 2025-07-23 08:15:21.555112

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '22130e9524da'
down_revision: Union[str, Sequence[str], None] = ('15eda0c5b884', 'add_image_urls_to_user', 'add_timestamps_to_roles', '12345678abcd')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
