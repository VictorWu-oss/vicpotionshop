"""Add yellow potion

Revision ID: 0b2bacb42d59
Revises: ed05b4a62fdf
Create Date: 2026-04-12 18:13:13.242430

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0b2bacb42d59'
down_revision: Union[str, None] = 'ed05b4a62fdf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        INSERT INTO potions (sku, name, red, green, blue, dark, price)
        VALUES ('YELLOW_POTION', 'Yellow Potion', 50, 50, 0, 0, 60)
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM potions WHERE sku = 'YELLOW_POTION'")
