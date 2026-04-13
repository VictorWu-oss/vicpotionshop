"""Version 2 custom potions and order management

Revision ID: e3d509adfb3c
Revises: b8ff5b82a304
Create Date: 2026-04-11 15:11:01.691141

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3d509adfb3c'
down_revision: Union[str, None] = 'b8ff5b82a304'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Create table, each row indicates a unique potion mixture.
    Each row: type of potion (color amounts), relevant catalog information needed to offer them for sale, and available inventory of that potion
    EX: 1239 (identify specific potion, for database), RED_POTION (code name for API calls), Red_potion (code name for customers, 100 0 0 0, 50 gold, 5 in stock
    """
    op.create_table(
        "potions",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("sku", sa.String(), nullable =False, unique = True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("red", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("green", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("blue", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("dark", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("inventory", sa.Integer(), nullable=False, server_default="0"),
    )

    """
    Create table for carts 
    Stores each shopping cart created by a customer. Represented by inserting a new row. 
    """
    op.create_table(
        "carts",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("customer_name", sa.String(), nullable=False),
        sa.Column("customer_id", sa.String(), nullable=False),
        sa.Column("customer_class", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()")),
    )

    """
    Create table for cart_items
    Stores each item added to a cart. Represented by inserting a new row. Links back to carts using cart_id and potions using potion_id.
    """
    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("cart_id", sa.Integer(), sa.ForeignKey("carts.id"), nullable=False),
        sa.Column("potion_id", sa.Integer(),sa.ForeignKey("potions.id"), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
    )

# NO MORE HARDCODING REFERENCES TO POTIONS, drop previous implementations to memory to now being stored in databse
def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("cart_items")
    op.drop_table("carts")
    op.drop_table("potions")

