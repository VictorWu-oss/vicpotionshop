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
    with db.engine.begin() as connection:
        # Read curr capacity from global inventory
        capacity = connection.execute(
            sqlalchemy.text(
                """
                SELECT 10000 + COALESCE(SUM(ml_capacity), 0) as ml_capacity, 50 + COALESCE(SUM(potion_capacity), 0) as potion_capacity
                FROM account_ledger_entries
                """
            )
        ).one()

        # Read curr gold, ml, potions from ledger
        account_ledger = connection.execute(
            sqlalchemy.text(
                """
                SELECT SUM(gold) as gold, SUM(red_ml) + SUM(green_ml) + SUM(blue_ml) as total_ml, SUM(potion_change) as total_potions
                FROM account_ledger_entries
                """
            )
        ).one()

    gold = account_ledger.gold or 0
    total_ml = account_ledger.total_ml or 0
    total_potions = account_ledger.total_potions or 0

    potion_cap_tobuy = 0
    ml_cap_tobuy = 0

    # Buy ml capacity if halfway full and can afford it
    if total_ml >= capacity.ml_capacity * 0.5 and gold >= 1000:
        ml_cap_tobuy = 1
        gold -= 1000

    # Buy potion capacity if halfway full and can afford it
    if total_potions >= capacity.potion_capacity * 0.5 and gold >= 1000:
        potion_cap_tobuy = 1

    return CapacityPlan(potion_capacity=potion_cap_tobuy, ml_capacity=ml_cap_tobuy)


@router.post("/deliver/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
def deliver_capacity_plan(capacity_purchase: CapacityPlan, order_id: int):
    """
    Processes the delivery of the planned capacity purchase. order_id is a
    unique value representing a single delivery; the call is idempotent.

    - Start with 1 capacity for 50 potions and 1 capacity for 10,000 ml of potion.
    - Each additional capacity unit costs 1000 gold.
    """
    with db.engine.begin() as connection:
        # Receives capacity_purchase a CapacityPlan and order_id

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

        # Don't try to return an error or else I will get null, don't want that
        if existing: return

        # Insert into account_transactions
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
                "description": "Increased capacity"
            }
        ).scalar_one()

        gold_cost = (capacity_purchase.potion_capacity + capacity_purchase.ml_capacity) * 1000

        # Insert into ledgers with neg gold
        connection.execute(
            sqlalchemy.text
                (
                """
                INSERT INTO account_ledger_entries (account_transaction_id, gold, ml_capacity, potion_capacity)
                VALUES(:transaction_id, :gold, :ml_capacity, :potion_capacity)
                """
            ),
            {
                "transaction_id": transaction,
                "gold": -gold_cost,
                "ml_capacity": capacity_purchase.ml_capacity * 10000,
                "potion_capacity": capacity_purchase.potion_capacity * 50
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

        print(f"capacity delivered: {capacity_purchase} order_id: {order_id}")
