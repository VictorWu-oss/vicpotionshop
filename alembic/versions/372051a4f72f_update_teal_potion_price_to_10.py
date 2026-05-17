"""Update teal potion price to 10

Revision ID: 372051a4f72f
Revises: c7183b76637c
Create Date: 2026-05-16 23:19:41.670010

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '372051a4f72f'
down_revision: Union[str, None] = 'c7183b76637c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE potions SET price = 10 WHERE sku = 'TEAL_POTION'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
