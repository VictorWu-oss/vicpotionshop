"""Drop potion_type column from barrel offers

Revision ID: 46abba06068e
Revises: de9bc2b0e401
Create Date: 2026-05-11 16:19:19.347399

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46abba06068e'
down_revision: Union[str, None] = 'de9bc2b0e401'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE barrel_offers DROP COLUMN IF EXISTS potion_type")

def downgrade() -> None:
    op.add_column("barrel_offers", sa.Column("potion_type", sa.String(), nullable=True))
