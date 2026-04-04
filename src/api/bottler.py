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
    red_ml_used = 0
    green_ml_used = 0
    blue_ml_used = 0

    red_potions_added = 0
    green_potions_added = 0
    blue_potions_added = 0

    for potion in potions_delivered:
        if potion.potion_type == [100, 0, 0, 0]:
            red_potions_added += potion.quantity
            red_ml_used += potion.quantity * 100
        elif potion.potion_type == [0, 100, 0, 0]:
            green_potions_added += potion.quantity
            green_ml_used += potion.quantity * 100
        elif potion.potion_type == [0, 0, 100, 0]:
            blue_potions_added += potion.quantity
            blue_ml_used += potion.quantity * 100

    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
            """
            UPDATE global_inventory
            SET red_ml = red_ml - :red_ml_used, 
            green_ml = green_ml - :green_ml_used, 
            blue_ml = blue_ml - :blue_ml_used, 
            red_potions = red_potions + :red_potions_added, 
            green_potions = green_potions + :green_potions_added, 
            blue_potions = blue_potions + :blue_potions_added
            """
            ),
            {
                "red_ml_used": red_ml_used,
                "green_ml_used": green_ml_used,
                "blue_ml_used": blue_ml_used,
                "red_potions_added": red_potions_added,
                "green_potions_added": green_potions_added,
                "blue_potions_added": blue_potions_added,
            },
        )

def create_bottle_plan(
    red_ml: int,
    green_ml: int,
    blue_ml: int,
) -> List[PotionMixes]:
    plan = []

    '''TODO: Create a real bottle plan logic'''
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

@router.post("/plan", response_model=List[PotionMixes])
def get_bottle_plan():
    """
    Gets the plan for bottling potions.
    Each bottle has a quantity of what proportion of red, green, blue, and dark potions to add.
    Colors are expressed in integers from 0 to 100 that must sum up to exactly 100.
    """

    with db.engine.begin() as connection:
        row = connection.execute(
            sqlalchemy.text(
                """
                SELECT red_ml, green_ml, blue_ml
                FROM global_inventory
                """
            )
        ).one()

    return create_bottle_plan(
        red_ml=row.red_ml,
        green_ml=row.green_ml,
        blue_ml=row.blue_ml,
    )

if __name__ == "__main__":
    print(get_bottle_plan())
