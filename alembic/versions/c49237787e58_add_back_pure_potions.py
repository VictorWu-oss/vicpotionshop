"""Add back pure potions

Revision ID: c49237787e58
Revises: 5becb8ca73fd
Create Date: 2026-04-16 18:10:29.876582

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c49237787e58'
down_revision: Union[str, None] = '5becb8ca73fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        INSERT INTO potions (sku, name, red, green, blue, dark, price)
        VALUES
            ('RED_POTION', 'Red Potion', 100, 0, 0, 0, 50),
            ('GREEN_POTION', 'Green Potion', 0, 100, 0, 0, 50),
            ('BLUE_POTION', 'Blue Potion', 0, 0, 100, 0, 50)
        ON CONFLICT (sku) DO NOTHING
        """
    )


def downgrade() -> None:
    op.execute(
        """
        DELETE FROM potions 
        WHERE sku IN ('RED_POTION', 'GREEN_POTION', 'BLUE_POTION')
        """
    )
