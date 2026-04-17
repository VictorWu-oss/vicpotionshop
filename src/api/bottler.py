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
        for potion in potions_delivered:
            r, g, b, d = potion.potion_type
            #ml_used = potion.quantity * 100  # 100 ml per potion

            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE global_inventory
                    SET red_ml = red_ml - :red_ml_used, 
                        green_ml = green_ml - :green_ml_used, 
                        blue_ml = blue_ml - :blue_ml_used,
                        dark_ml = dark_ml - :dark_ml_used
                    """
                ),
                {
                    "red_ml_used": r * potion.quantity,
                    "green_ml_used": g * potion.quantity,
                    "blue_ml_used": b * potion.quantity,
                    "dark_ml_used": d * potion.quantity,
                }
            )

            connection.execute(
                sqlalchemy.text(
                    """
                    UPDATE potions
                    SET inventory = inventory + :quantity
                    WHERE red = :r AND green = :g AND blue = :b AND dark = :d
                    """
                ),
                {"quantity": potion.quantity, "r": r, "g": g, "b": b, "d": d}
            )

'''
No longer needed 

def create_bottle_plan(
    red_ml: int,
    green_ml: int,
    blue_ml: int,
) -> List[PotionMixes]:
    plan = []

    #TODO: Create a real bottle plan logic
    red_potions_tomake = red_ml // 100
    green_potions_tomake = green_ml // 100
    blue_potions_tomake = blue_ml // 100

    if red_potions_tomake > 0:
        plan.append(
            PotionMixes(
                potion_type = [100, 0, 0, 0],
                quantity=red_potions_tomake,
            )
        )

    if green_potions_tomake > 0:
        plan.append(
            PotionMixes(
                potion_type=[0, 100, 0, 0],
                quantity=green_potions_tomake,
            )
        )

    if blue_potions_tomake > 0:
        plan.append(
            PotionMixes(
                potion_type = [0, 0, 100, 0],
                quantity=blue_potions_tomake,
            )
        )
    return plan
'''

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
                SELECT red_ml, green_ml, blue_ml, dark_ml
                FROM global_inventory
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
    red_ml = inventory.red_ml
    green_ml = inventory.green_ml
    blue_ml = inventory.blue_ml
    dark_ml = inventory.dark_ml

    for potion in potions:
        r, g, b, d = potion.red, potion.green, potion.blue, potion.dark
        quantity = min(
            red_ml // r if r> 0 else float('inf'),
            green_ml // g if g > 0 else float('inf'),
            blue_ml // b if b > 0 else float('inf'),
            dark_ml // d if d > 0 else float('inf')
        )
        quantity = int(quantity)
        if quantity > 0:
            plan.append(PotionMixes(potion_type=[r,g,b,d], quantity=quantity))
            red_ml -= r * quantity
            green_ml -= g * quantity
            blue_ml -= b * quantity
            dark_ml -= d * quantity

    return plan

if __name__ == "__main__":
    print(get_bottle_plan())
