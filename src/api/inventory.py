from fastapi import APIRouter, Depends, status
from pydantic import BaseModel, Field
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/inventory",
    tags=["inventory"],
    dependencies=[Depends(auth.get_api_key)],
)


class InventoryAudit(BaseModel):
    number_of_potions: int
    ml_in_barrels: int
    gold: int


class CapacityPlan(BaseModel):
    potion_capacity: int = Field(
        ge=0, le=10, description="Potion capacity units, max 10"
    )
    ml_capacity: int = Field(ge=0, le=10, description="ML capacity units, max 10")


@router.get("/audit", response_model=InventoryAudit)
def get_inventory():
    """
    Returns an audit of the current inventory. Any discrepancies between
    what is reported here and my source of truth will be posted
    as errors on potion exchange.
    """

    # NOW GET GOLD, ML, AND POTIONS VIA SUMMING LEDGER ENTRIES
    with db.engine.begin() as connection:
        ledger = connection.execute(
            sqlalchemy.text(
                """
                SELECT SUM(gold) as gold, SUM(red_ml) as red_ml, SUM(green_ml) as green_ml, SUM(blue_ml) as blue_ml, SUM(dark_ml) as dark_ml
                FROM account_ledger_entries
                """
            )
        ).one()

        number_of_potions = connection.execute(
            sqlalchemy.text(
                """
                SELECT SUM(potion_change) as total
                FROM account_ledger_entries
                """
            )
        ).one()

    return InventoryAudit(
        number_of_potions=number_of_potions.total or 0,
        ml_in_barrels=(ledger.red_ml or 0) + (ledger.green_ml or 0) + (ledger.blue_ml or 0) + (ledger.dark_ml or 0), gold=ledger.gold or 0,)


@router.post("/plan", response_model=CapacityPlan)
def get_capacity_plan():
    """
    Provides a daily capacity purchase plan.

    - Start with 1 capacity for 50 potions and 1 capacity for 10,000 ml of potion.
    - Each additional capacity unit costs 1000 gold.
    """
    return CapacityPlan(potion_capacity=0, ml_capacity=0)


@router.post("/deliver/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def deliver_capacity_plan(capacity_purchase: CapacityPlan, order_id: int):
    """
    Processes the delivery of the planned capacity purchase. order_id is a
    unique value representing a single delivery; the call is idempotent.

    - Start with 1 capacity for 50 potions and 1 capacity for 10,000 ml of potion.
    - Each additional capacity unit costs 1000 gold.
    """
    print(f"capacity delivered: {capacity_purchase} order_id: {order_id}")
