"""feat: add species and level to carts,fix: potion_inventory table to include ml amounts

Revision ID: f71d36832221
Revises: 6c2af603d64b
Create Date: 2026-05-10 17:58:15.222050

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f71d36832221'
down_revision: Union[str, None] = '6c2af603d64b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add species and level to carts
    op.add_column("carts", sa.Column("character_species", sa.String(), nullable=True))
    op.add_column("carts", sa.Column("level", sa.Integer(), nullable=True))

    # Update potion_inventory view to include ml amounts
    op.execute(
        """
        CREATE OR REPLACE VIEW potion_inventory AS
        SELECT 
            p.id,
            p.sku,
            p.name,
            p.red,
            p.green,
            p.blue,
            p.dark,
            p.price,
            COALESCE(SUM(ale.potion_change), 0) as current_inventory
        FROM potions p
        LEFT JOIN account_ledger_entries ale ON ale.potion_id = p.id
        GROUP BY p.id, p.sku, p.name, p.red, p.green, p.blue, p.dark, p.price
        ORDER BY p.id
        """
    )

def downgrade() -> None:
    """Downgrade schema."""
    pass
