"""Remove teal potion

Revision ID: 0e9f311afacd
Revises: 372051a4f72f
Create Date: 2026-05-17 11:18:19.251505

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0e9f311afacd'
down_revision: Union[str, None] = '372051a4f72f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DELETE FROM potions WHERE sku = 'TEAL_POTION'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
