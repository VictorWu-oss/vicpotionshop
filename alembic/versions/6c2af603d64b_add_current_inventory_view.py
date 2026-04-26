"""Add current inventory view

Revision ID: 6c2af603d64b
Revises: de38d93f95bb
Create Date: 2026-04-25 17:35:26.907630

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c2af603d64b'
down_revision: Union[str, None] = 'de38d93f95bb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE VIEW current_inventory AS
        SELECT 
            SUM(gold) as gold,
            SUM(red_ml) as red_ml,
            SUM(green_ml) as green_ml,
            SUM(blue_ml) as blue_ml,
            SUM(dark_ml) as dark_ml,
            SUM(potion_change) as total_potions
        FROM account_ledger_entries
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
