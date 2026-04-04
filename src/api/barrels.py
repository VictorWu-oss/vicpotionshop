import random
from dataclasses import dataclass
from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field, field_validator
from typing import List

import sqlalchemy

from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/barrels",
    tags=["barrels"],
    dependencies=[Depends(auth.get_api_key)],
)

class Barrel(BaseModel):
    sku: str
    ml_per_barrel: int = Field(gt=0, description="Must be greater than 0")
    potion_type: List[float] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Must contain exactly 4 elements: [r, g, b, d] that sum to 1.0",
    )
    price: int = Field(ge=0, description="Price must be non-negative")
    quantity: int = Field(ge=0, description="Quantity must be non-negative")

    @field_validator("potion_type")
    @classmethod
    def validate_potion_type(cls, potion_type: List[float]) -> List[float]:
        if len(potion_type) != 4:
            raise ValueError("potion_type must have exactly 4 elements: [r, g, b, d]")
        if not abs(sum(potion_type) - 1.0) < 1e-6:
            raise ValueError("Sum of potion_type values must be exactly 1.0")
        return potion_type

class BarrelOrder(BaseModel):
    sku: str
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")

@dataclass
class BarrelSummary:
    gold_paid: int
    red_ml_added: int
    green_ml_added: int
    blue_ml_added: int

def calculate_barrel_summary(barrels: List[Barrel]) -> BarrelSummary:
    gold_paid = 0
    red_ml_added = 0
    green_ml_added = 0
    blue_ml_added = 0

    for barrel in barrels:
        gold_paid += barrel.price * barrel.quantity

        if barrel.potion_type[0] == 1:
            red_ml_added += barrel.ml_per_barrel * barrel.quantity
        elif barrel.potion_type[1] == 1:
            green_ml_added += barrel.ml_per_barrel * barrel.quantity
        elif barrel.potion_type[2] == 1:
            blue_ml_added += barrel.ml_per_barrel * barrel.quantity

    return BarrelSummary(gold_paid=gold_paid, red_ml_added=red_ml_added, green_ml_added=green_ml_added, blue_ml_added=blue_ml_added)

@router.post("/deliver/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_deliver_barrels(barrels_delivered: List[Barrel], order_id: int):
    """
    Processes barrels delivered based on the provided order_id. order_id is a unique value representing
    a single delivery; the call is idempotent based on the order_id.
    """
    print(f"barrels delivered: {barrels_delivered} order_id: {order_id}")

    delivery = calculate_barrel_summary(barrels_delivered)

    # Subtracts gold, adds ml to correct color when barrels are delivered.
    with db.engine.begin() as connection:
        connection.execute(
            sqlalchemy.text(
                """
                UPDATE global_inventory 
                SET gold = gold - :gold_paid, red_ml = red_ml + :red_ml_added, green_ml = green_ml + :green_ml_added, blue_ml = blue_ml + :blue_ml_added
                """
            ),
            {
                "gold_paid": delivery.gold_paid, "red_ml_added": delivery.red_ml_added,
                "green_ml_added": delivery.green_ml_added, "blue_ml_added": delivery.blue_ml_added
            },
        )

def create_barrel_plan(
    gold: int,
    current_red_ml: int,
    current_green_ml: int,
    current_blue_ml: int,
    current_red_potions: int,
    current_green_potions: int,
    current_blue_potions: int,
    wholesale_catalog: List[Barrel],
) -> List[BarrelOrder]:
    print(
        f"gold: {gold}, current_red_ml: {current_red_ml}, current_green_ml: {current_green_ml}, current_blue_ml: {current_blue_ml}, current_red_potions: {current_red_potions}, current_green_potions: {current_green_potions}, current_blue_potions: {current_blue_potions}, wholesale_catalog: {wholesale_catalog}"
    )

    # Change to pick randomly between r, g, b
    color = random.choice(["red", "green", "blue"])

    # If both true then purchase a small barrel of that color
    if color == "red":
        current_potions = current_red_potions
        matching_barrels = [barrel for barrel in wholesale_catalog if barrel.potion_type[0] == 1]

    elif color == "green":
        current_potions = current_green_potions
        matching_barrels = [barrel for barrel in wholesale_catalog if barrel.potion_type[1] == 1]

    else:
        current_potions = current_blue_potions
        matching_barrels = [barrel for barrel in wholesale_catalog if barrel.potion_type[2] == 1]

    # Check whether color has fewer than 5 potions in inventory
    if current_potions >= 5:
        return []

    # and if you can afford a small barrel of that color
    affordable_barrels = [barrel for barrel in matching_barrels if barrel.price <= gold]

    # make sure we can afford it
    if not affordable_barrels:
        return []

    cheapest_affordable_barrel = min(affordable_barrels, key=lambda b: b.ml_per_barrel)

    # Returns a plan only
    # Does not update the DB
    return [BarrelOrder(sku=cheapest_affordable_barrel.sku, quantity=1)]

# Reads gold, but also needs to read potion color ml and potion color
@router.post("/plan", response_model=List[BarrelOrder])
def get_wholesale_purchase_plan(wholesale_catalog: List[Barrel]):
    """
    Gets the plan for purchasing wholesale barrels. The call passes in a catalog of available barrels
    and the shop returns back which barrels they'd like to purchase and how many.
    """
    print(f"barrel catalog: {wholesale_catalog}")

    with db.engine.begin() as connection:
        row = connection.execute(
            sqlalchemy.text(
                """
                SELECT gold, red_ml, green_ml, blue_ml, red_potions, green_potions, blue_potions
                FROM global_inventory
                """
            )
        ).one()

    # TODO: fill in values correctly based on what is in your database
    return create_barrel_plan(
        gold=row.gold,
        current_red_ml=row.red_ml,
        current_green_ml=row.green_ml,
        current_blue_ml=row.blue_ml,
        current_red_potions=row.red_potions,
        current_green_potions=row.green_potions,
        current_blue_potions=row.blue_potions,
        wholesale_catalog=wholesale_catalog,
    )
