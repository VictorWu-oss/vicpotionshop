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
    op.create_table(
        "barrel_offers",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sku", sa.String(), nullable=False),
        sa.Column("ml_per_barrel", sa.Integer(), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("red", sa.Float(), nullable=False, server_default="0"),
        sa.Column("green", sa.Float(), nullable=False, server_default="0"),
        sa.Column("blue", sa.Float(), nullable=False, server_default="0"),
        sa.Column("dark", sa.Float(), nullable=False, server_default="0"),
        sa.Column("offered_at", sa.DateTime(), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
