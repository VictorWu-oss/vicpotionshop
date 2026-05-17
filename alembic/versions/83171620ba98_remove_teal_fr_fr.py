"""REMOVE TEAL FR FR

Revision ID: 83171620ba98
Revises: 0e9f311afacd
Create Date: 2026-05-17 11:35:43.194819

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '83171620ba98'
down_revision: Union[str, None] = '0e9f311afacd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE account_ledger_entries 
        SET potion_id = NULL 
        WHERE potion_id = (SELECT id FROM potions WHERE sku = 'TEAL_POTION');
        DELETE FROM potions WHERE sku = 'TEAL_POTION';
        """
    )

def downgrade() -> None:
    """Downgrade schema.
    qeoiqesqoiuwhdoiu9qawhdu9ioqwahdhwqd    DWQ"""
    pass
