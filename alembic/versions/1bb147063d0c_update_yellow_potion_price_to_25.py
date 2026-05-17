"""Update yellow potion price to 25

Revision ID: 1bb147063d0c
Revises: a604b5f4e62e
Create Date: 2026-05-16 19:09:51.955147

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1bb147063d0c'
down_revision: Union[str, None] = 'a604b5f4e62e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE potions SET price = 25 WHERE sku = 'TEAL_POTION'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
