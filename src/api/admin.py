from fastapi import APIRouter, Depends, status
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(auth.get_api_key)],
)


@router.post("/reset", status_code=status.HTTP_204_NO_CONTENT)
def reset():
    """
    Reset the game state. Gold goes to 100, all potions are removed from
    inventory, and all barrels are removed from inventory. Carts are all reset.
    """
    # TODO: Implement database write logic here
    with db.engine.begin() as connection:
        # Since rows are not removed after admin reset implement
        connection.execute(sqlalchemy.text("DELETE FROM cart_items"))
        connection.execute(sqlalchemy.text("DELETE FROM carts"))

        connection.execute(sqlalchemy.text("DELETE FROM account_ledger_entries"))
        connection.execute(sqlalchemy.text("DELETE FROM account_transactions"))

        connection.execute(sqlalchemy.text("DELETE FROM processed_requests"))

        transaction_id = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO account_transactions (description)
                VALUES('Reset')
                RETURNING id 
                """
            )
        ).scalar_one()

        # Defaults the MLS to 0 so fine
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO account_ledger_entries (account_transaction_id, gold)
                VALUES (:transaction_id, 100)
                """
            ),
            {
                "transaction_id": transaction_id
            }
        )

