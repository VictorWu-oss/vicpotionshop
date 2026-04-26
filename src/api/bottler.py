from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/bottler",
    tags=["bottler"],
    dependencies=[Depends(auth.get_api_key)],
)


class PotionMixes(BaseModel):
    potion_type: List[int] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Must contain exactly 4 elements: [r, g, b, d]",
    )
    quantity: int = Field(
        ..., ge=1, le=10000, description="Quantity must be between 1 and 10,000"
    )

    @field_validator("potion_type")
    @classmethod
    def validate_potion_type(cls, potion_type: List[int]) -> List[int]:
        if len(potion_type) != 4:
            raise ValueError("Potion_type must contain exactly 4 elements")
        if sum(potion_type) != 100:
            raise ValueError("Sum of potion_type values must be exactly 100")
        return potion_type


@router.post("/deliver/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_deliver_bottles(potions_delivered: List[PotionMixes], order_id: int):
    """
    Delivery of potions requested after plan. order_id is a unique value representing
    a single delivery; the call is idempotent based on the order_id.
    """
    print(f"potions delivered: {potions_delivered} order_id: {order_id}")

    # TODO: Record values of delivered potions in your database.
    # TODO: Subtract ml based on how much delivered potions used.

    with db.engine.begin() as connection:
        # Check in processed requests to see if order_id already exists, if it does don't do it: uniqueness constraint violation
        existing = connection.execute(
            sqlalchemy.text
                (
                """
                SELECT order_id 
                FROM processed_requests 
                WHERE order_id = :order_id
                """
            ),
            {
                "order_id": order_id
            }
        ).one_or_none()

        # I think don't try to return an error or else I will get null potions, don't want that
        if existing: return

        # Insert into transaction
        transaction = connection.execute(
            sqlalchemy.text
                (
                """
                INSERT INTO account_transactions (description)
                VALUES(:description)
                RETURNING id 
                """
            ),
            {
                "description": "Potion delivery"
            }
        ).scalar_one()

        for potion in potions_delivered:
            r, g, b, d = potion.potion_type

            potionExe = connection.execute(
                sqlalchemy.text(
                    """
                    SELECT id
                    FROM potions
                    WHERE red =:r AND green =:g AND blue = :b AND dark = :d
                    """
                ),
                {
                    "r": r, "g": g, "b": b, "d": d
                }
            ).scalar_one()

            # Insert into account_ledger_entries
            connection.execute(
                sqlalchemy.text
                    (
                    """
                    INSERT INTO account_ledger_entries (account_transaction_id, potion_id, red_ml, green_ml, blue_ml, dark_ml, potion_change)
                    VALUES(:transaction_id, :potion_id, :red_ml, :green_ml, :blue_ml, :dark_ml, :potion_change)
                    """
                ),
                {
                    "transaction_id": transaction,
                    "potion_id": potionExe,
                    "red_ml": -(r * potion.quantity),
                    "green_ml": -(g * potion.quantity),
                    "blue_ml": -(b * potion.quantity),
                    "dark_ml": -(d * potion.quantity),
                    "potion_change": potion.quantity
                }
            )

        # Insert into processed requests
        connection.execute(
            sqlalchemy.text
                (
                """
                INSERT INTO processed_requests (order_id, response)
                VALUES(:order_id, :response)
                """
            ),
            {
                "order_id": order_id,
                "response": "processed"
            }
        )

@router.post("/plan", response_model=List[PotionMixes])
def get_bottle_plan():
    """
    Gets the plan for bottling potions.
    Each bottle has a quantity of what proportion of red, green, blue, and dark potions to add.
    Colors are expressed in integers from 0 to 100 that must sum up to exactly 100.
    """
    with db.engine.begin() as connection:
        inventory = connection.execute(
            sqlalchemy.text(
                """
                SELECT SUM(red_ml) as red_ml, SUM(green_ml) as green_ml, SUM(blue_ml) as blue_ml, SUM(dark_ml) as dark_ml
                FROM account_ledger_entries
                """
            )
        ).one()

        # Prioritize making mixed potions over pure potions
        # Put mixed potions (with more than 1 color) to the top
        potions = connection.execute(
            sqlalchemy.text(
                """
                SELECT red, green, blue, dark
                FROM potions
                ORDER BY (CASE WHEN (red>0)::int + (green>0)::int + (blue>0)::int + (dark>0)::int > 1 THEN 0 ELSE 1 END)
                """
            )
        ).fetchall()

    plan = []
    red_ml = inventory.red_ml or 0
    green_ml = inventory.green_ml or 0
    blue_ml = inventory.blue_ml or 0
    dark_ml = inventory.dark_ml or 0

    for potion in potions:
        r, g, b, d = potion.red, potion.green, potion.blue, potion.dark
        quantity = min(
            red_ml // r if r> 0 else float('inf'),
            green_ml // g if g > 0 else float('inf'),
            blue_ml // b if b > 0 else float('inf'),
            dark_ml // d if d > 0 else float('inf')
        )
        quantity = int(quantity)

        # Cap quantity so the total plan doesn't exceed 50
        remainder = 50 - sum(x.quantity for x in plan)
        if remainder <= 0:
            break
        quantity = min(quantity, remainder)

        if quantity > 0:
            plan.append(PotionMixes(potion_type=[r,g,b,d], quantity=quantity))
            red_ml -= r * quantity
            green_ml -= g * quantity
            blue_ml -= b * quantity
            dark_ml -= d * quantity


    return plan

if __name__ == "__main__":
    print(get_bottle_plan())
