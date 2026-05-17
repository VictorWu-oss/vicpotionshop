"""Update yellow potion price to 23

Revision ID: c7183b76637c
Revises: 1bb147063d0c
Create Date: 2026-05-16 21:29:23.645235

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7183b76637c'
down_revision: Union[str, None] = '1bb147063d0c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE potions SET price = 23 WHERE sku = 'TEAL_POTION'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
