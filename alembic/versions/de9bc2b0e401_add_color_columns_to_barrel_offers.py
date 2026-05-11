"""Add color columns to barrel offers

Revision ID: de9bc2b0e401
Revises: 434d3aab03a3
Create Date: 2026-05-11 11:50:54.245601

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de9bc2b0e401'
down_revision: Union[str, None] = '434d3aab03a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TABLE barrel_offers 
        ADD COLUMN IF NOT EXISTS red FLOAT NOT NULL DEFAULT 0,
        ADD COLUMN IF NOT EXISTS green FLOAT NOT NULL DEFAULT 0,
        ADD COLUMN IF NOT EXISTS blue FLOAT NOT NULL DEFAULT 0,
        ADD COLUMN IF NOT EXISTS dark FLOAT NOT NULL DEFAULT 0
        """
    )

def downgrade() -> None:
    op.drop_column("barrel_offers", "red")
    op.drop_column("barrel_offers", "green")
    op.drop_column("barrel_offers", "blue")
    op.drop_column("barrel_offers", "dark")
