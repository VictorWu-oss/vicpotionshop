"""Remove pure potions and fix bugs

Revision ID: 5becb8ca73fd
Revises: 0b2bacb42d59
Create Date: 2026-04-15 21:04:41.795173

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5becb8ca73fd'
down_revision: Union[str, None] = '0b2bacb42d59'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
