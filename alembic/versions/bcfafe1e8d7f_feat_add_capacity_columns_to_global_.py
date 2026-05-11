"""feat: Add capacity columns to global inventory and implement buying additional capacity

Revision ID: bcfafe1e8d7f
Revises: f71d36832221
Create Date: 2026-05-10 18:16:26.911468

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bcfafe1e8d7f'
down_revision: Union[str, None] = 'f71d36832221'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("account_ledger_entries", sa.Column("potion_capacity", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("account_ledger_entries", sa.Column("ml_capacity", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("account_ledger_entries", "potion_capacity")
    op.drop_column("account_ledger_entries", "ml_capacity")
