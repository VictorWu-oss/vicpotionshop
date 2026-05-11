"""Add barrel offers tracking table

Revision ID: 434d3aab03a3
Revises: bcfafe1e8d7f
Create Date: 2026-05-10 20:11:04.736000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '434d3aab03a3'
down_revision: Union[str, None] = 'bcfafe1e8d7f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """
        CREATE TABLE IF NOT EXISTS barrel_offers (
            id SERIAL PRIMARY KEY,
            sku VARCHAR NOT NULL,
            ml_per_barrel INTEGER NOT NULL,
            price INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            red FLOAT NOT NULL DEFAULT 0,
            green FLOAT NOT NULL DEFAULT 0,
            blue FLOAT NOT NULL DEFAULT 0,
            dark FLOAT NOT NULL DEFAULT 0,
            offered_at TIMESTAMP DEFAULT now()
        )
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
