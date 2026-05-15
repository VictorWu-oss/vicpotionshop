"""Update yellow potion price to 30

Revision ID: 6102ee819c8a
Revises: 46abba06068e
Create Date: 2026-05-14 21:22:46.977103

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6102ee819c8a'
down_revision: Union[str, None] = '46abba06068e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE potions SET price = 30 WHERE sku = 'YELLOW_POTION'")

def downgrade() -> None:
    op.execute("UPDATE potions SET price = 40 WHERE sku = 'YELLOW_POTION'")
