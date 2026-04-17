"""Remove orange potion

Revision ID: 0f3146be6645
Revises: c49237787e58
Create Date: 2026-04-17 15:18:44.634123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0f3146be6645'
down_revision: Union[str, None] = 'c49237787e58'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DELETE FROM potions WHERE sku = 'ORANGE_POTION'")


def downgrade() -> None:
    op.execute(
        """
        INSERT INTO potions (sku, name, red, green, blue, dark, price)
        VALUES ('ORANGE_POTION', 'Orange Potion', 50, 50, 0, 0, 55)
        ON CONFLICT (sku) DO NOTHING
        """
    )
