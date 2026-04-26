"""Version 3 ledgers and idempotency

Revision ID: 20b3c8adcd12
Revises: 0f3146be6645
Create Date: 2026-04-25 12:55:22.202120

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20b3c8adcd12'
down_revision: Union[str, None] = '0f3146be6645'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Represents a transaction
    op.create_table(
        "account_transactions",
        sa.Column("id" , sa.Integer(), primary_key=True, autoincrement=True, nullable = False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable = False),
        sa.Column("description", sa.String(), nullable = False),
    )

    # Represent the changes and this is where to sum up to represent the changes in the inventory
    op.create_table(
        "account_ledger_entries",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True, nullable=False),
        sa.Column("account_transaction_id", sa.Integer(), sa.ForeignKey("account_transactions.id"), nullable=False),
        sa.Column("gold", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("red_ml", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("blue_ml", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("green_ml", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("dark_ml", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("potion_id", sa.Integer(), sa.ForeignKey("potions.id"), nullable=True),
        sa.Column("potion_change", sa.Integer(), nullable=False, server_default="0"),
    )

    # Stores order_id and response for idempotency, stored response for retries in case fails
    op.create_table(
        "processed_requests",
        sa.Column("order_id", sa.Integer(), primary_key=True),
        sa.Column("response", sa.String(), nullable=False),
    )

    # Default values
    op.execute(
        """
        INSERT INTO account_transactions (description)
        VALUES('Starting gold');
        
        INSERT INTO account_ledger_entries(account_transaction_id, gold)
        VALUES (1, 100);
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("processed_requests")
    op.drop_table("account_ledger_entries")
    op.drop_table("account_transactions")
