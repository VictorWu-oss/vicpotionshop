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
    dark_ml_added: int

def calculate_barrel_summary(barrels: List[Barrel]) -> BarrelSummary:
    gold_paid = 0
    red_ml_added = 0
    green_ml_added = 0
    blue_ml_added = 0
    dark_ml_added = 0

    for barrel in barrels:
        gold_paid += barrel.price * barrel.quantity

        if barrel.potion_type[0] == 1:
            red_ml_added += barrel.ml_per_barrel * barrel.quantity
        elif barrel.potion_type[1] == 1:
            green_ml_added += barrel.ml_per_barrel * barrel.quantity
        elif barrel.potion_type[2] == 1:
            blue_ml_added += barrel.ml_per_barrel * barrel.quantity
        elif barrel.potion_type[3] == 1:
            dark_ml_added += barrel.ml_per_barrel * barrel.quantity

    return BarrelSummary(gold_paid=gold_paid, red_ml_added=red_ml_added, green_ml_added=green_ml_added, blue_ml_added=blue_ml_added, dark_ml_added=dark_ml_added)

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
                SET gold = gold - :gold_paid, red_ml = red_ml + :red_ml_added, green_ml = green_ml + :green_ml_added, blue_ml = blue_ml + :blue_ml_added, dark_ml = dark_ml + :dark_ml_added
                """
            ),
            {
                "gold_paid": delivery.gold_paid, "red_ml_added": delivery.red_ml_added,
                "green_ml_added": delivery.green_ml_added, "blue_ml_added": delivery.blue_ml_added, "dark_ml_added": delivery.dark_ml_added
            },
        )

def create_barrel_plan(
    gold: int,
    total_potions: int,
        total_ml,
    wholesale_catalog: List[Barrel],
) -> List[BarrelOrder]:

    # Plan:
    # If I already have 15 potions, don't buy more barrels
    # Per barrel:
    #   If my total_ml would exceed 10000 by purchasing another barrel dont buy, if not continue
    #   Audit says: Cannot have more than 10000 ml in inventory. With current barrel request would have 17500 ml.
    #
    #   If I can afford it, then do so

    if total_potions >= 15:
        return []

    plan = []
    for barrel in wholesale_catalog:
        if total_ml + barrel.ml_per_barrel > 10000:
            continue
        # If barrel's price is less than the gold
        if barrel.price <= gold:
            plan.append(BarrelOrder(sku=barrel.sku, quantity=1))
            gold -= barrel.price
            total_ml += barrel.ml_per_barrel

    return plan


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
                SELECT gold
                FROM global_inventory
                """
            )
        ).one()

        # Get total potion inventory via potions table
        # Fill in values correctly based on what is in your database
        total_potions = connection.execute(
            sqlalchemy.text(
                "SELECT SUM(inventory) as total FROM potions")
        ).one()

    return create_barrel_plan(
        gold=row.gold,
        total_potions=total_potions.total or 0,
        wholesale_catalog=wholesale_catalog,
    )
