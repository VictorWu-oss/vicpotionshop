"""Update potion prices

Revision ID: de38d93f95bb
Revises: 20b3c8adcd12
Create Date: 2026-04-25 17:26:07.948118

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'de38d93f95bb'
down_revision: Union[str, None] = '20b3c8adcd12'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE potions 
        SET price = CASE sku
            WHEN 'RED_POTION' THEN 30
            WHEN 'GREEN_POTION' THEN 35
            WHEN 'BLUE_POTION' THEN 35
            WHEN 'PURPLE_POTION' THEN 40
            WHEN 'TEAL_POTION' THEN 40
            WHEN 'YELLOW_POTION' THEN 40
            WHEN 'PURE_DARK_POTION' THEN 40
            WHEN 'DARK_RED_POTION' THEN 45
            WHEN 'DARK_GREEN_POTION' THEN 45
            WHEN 'DARK_BLUE_POTION' THEN 45
            ELSE price
        END
        """
    )

def downgrade() -> None:
    op.execute(
        """
        UPDATE potions
        SET price = 50
        """
    )



