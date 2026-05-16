"""Update teal potion price to 30

Revision ID: a604b5f4e62e
Revises: 6102ee819c8a
Create Date: 2026-05-16 09:48:49.677444

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a604b5f4e62e'
down_revision: Union[str, None] = '6102ee819c8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("UPDATE potions SET price = 30 WHERE sku = 'TEAL_POTION'")


def downgrade() -> None:
    """Downgrade schema."""
    pass
