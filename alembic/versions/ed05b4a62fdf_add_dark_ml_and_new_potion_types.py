"""Add dark ml and new potion types

Revision ID: ed05b4a62fdf
Revises: e3d509adfb3c
Create Date: 2026-04-12 16:58:58.214991

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ed05b4a62fdf'
down_revision: Union[str, None] = 'e3d509adfb3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add dark_ml column to global_inventory
    op.add_column("global_inventory", sa.Column("dark_ml", sa.Integer(), nullable=False, server_default="0"))

    # Add new potion types
    op.execute(
        """
        INSERT INTO potions (sku, name, red, green, blue, dark, price)
        VALUES
            ('ORANGE_POTION', 'Orange Potion', 50, 50, 0, 0, 55),
            ('TEAL_POTION', 'Teal Potion', 0, 50, 50, 0, 55),
            ('PURE_DARK_POTION', 'Pure Dark Potion', 0, 0, 0, 100, 65),
            ('DARK_RED_POTION', 'Dark Red Potion', 50, 0, 0, 50, 60),
            ('DARK_GREEN_POTION', 'Dark Green Potion', 0, 50, 0, 50, 60),
            ('DARK_BLUE_POTION', 'Dark Blue Potion', 0, 0, 50, 50, 60)
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM potions WHERE sku IN ('ORANGE_POTION', 'TEAL_POTION', 'PURE_DARK_POTION', 'DARK_RED_POTION', 'DARK_GREEN_POTION', 'DARK_BLUE_POTION')")
    op.drop_column("global_inventory", "dark_ml")
