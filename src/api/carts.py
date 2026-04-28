from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
import sqlalchemy
from src.api import auth
from enum import Enum
from typing import List, Optional
from src import database as db

router = APIRouter(
    prefix="/carts",
    tags=["cart"],
    dependencies=[Depends(auth.get_api_key)],
)


class SearchSortOptions(str, Enum):
    customer_name = "customer_name"
    item_sku = "item_sku"
    line_item_total = "line_item_total"
    timestamp = "timestamp"


class SearchSortOrder(str, Enum):
    asc = "asc"
    desc = "desc"


class LineItem(BaseModel):
    line_item_id: int
    item_sku: str
    customer_name: str
    line_item_total: int
    timestamp: str


class SearchResponse(BaseModel):
    previous: Optional[str] = None
    next: Optional[str] = None
    results: List[LineItem]


@router.get("/search/", response_model=SearchResponse, tags=["search"])
def search_orders(
    customer_name: str = "",
    potion_sku: str = "",
    search_page: str = "",
    sort_col: SearchSortOptions = SearchSortOptions.timestamp,
    sort_order: SearchSortOrder = SearchSortOrder.desc,
):
    """
    Search for cart line items by customer name and/or potion sku.
    Placeholder Scaramouche below
    """
    return SearchResponse(previous=None, next=None,results=[LineItem(
                line_item_id=1,
                item_sku="1 oblivion potion",
                customer_name="Scaramouche",
                line_item_total=50,
                timestamp="2021-01-01T00:00:00Z",
            )
        ],
    )
'''
No longer needed hardcode
cart_id_counter = 1
carts: dict[int, dict[str, int]] = {}
'''

class Customer(BaseModel):
    customer_id: str
    customer_name: str
    character_class: str
    character_species: str
    level: int = Field(ge=1, le=20)


@router.post("/visits/{visit_id}", status_code=status.HTTP_204_NO_CONTENT)
def post_visits(visit_id: int, customers: List[Customer]):
    """
    Shares the customers that visited the store on that tick.
    """
    print(customers, visit_id)
    pass


class CartCreateResponse(BaseModel):
    cart_id: int


# Update this to be no longer hardcoded
# Inserts carts TABLE and returns the database-generated id instead of in memory counter
@router.post("/", response_model=CartCreateResponse)
def create_cart(new_cart: Customer):
    """
    Creates a new cart for a specific customer.
    """
    with (db.engine.begin() as connection):
        # Insert new row into carts table and return the new cart's id
        result = connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO carts (customer_id, customer_name, customer_class)
                VALUES (:customer_id, :customer_name, :customer_class)
                RETURNING id
                """
            ),
            {
                "customer_id" : new_cart.customer_id,
                "customer_name" : new_cart.customer_name,
                "customer_class" : new_cart.character_class,
            }
        )
        cart_id = result.scalar_one()

        # Returning id gives us back the new cart's id from the result

    return CartCreateResponse(cart_id=cart_id)


class CartItem(BaseModel):
    quantity: int = Field(ge=1, description="Quantity must be at least 1")


# Looks up the cart and potion in 'carts' and 'potions' database. Then inserts into cart_items instead of storing into dict
@router.post("/{cart_id}/items/{item_sku}", status_code=status.HTTP_204_NO_CONTENT)
def set_item_quantity(cart_id: int, item_sku: str, cart_item: CartItem):
    with db.engine.begin() as connection:
        # Check if cart exists
        cart = connection.execute(
            sqlalchemy.text(
                """
                SELECT id 
                FROM carts
                WHERE id = :cart_id
                """
            ),
            {
                "cart_id" : cart_id
            }
        ).one_or_none()

        if cart is None:
            raise HTTPException(status_code=404, detail="Cart not found")

        # Find potion via SKU which is the name used for API calls
        potion = connection.execute(
            sqlalchemy.text(
                """
                SELECT id
                FROM potions
                WHERE sku = :sku
                """
            ),
            {
                "sku" : item_sku
            }
        ).one_or_none()

        # Check if potion exists
        if potion is None:
            raise HTTPException(status_code=404, detail="Potion not found")

        # Add item to the cart
        connection.execute(
            sqlalchemy.text(
                """
                INSERT INTO cart_items (cart_id, potion_id, quantity)
                VALUES (:cart_id, :potion_id, :quantity)
                """
            ),
            {"cart_id": cart_id, "potion_id": potion.id, "quantity": cart_item.quantity}
        )

    # No longer using dictionary below
    #print(
    #    f"cart_id: {cart_id}, item_sku: {item_sku}, cart_item: {cart_item}, carts: {carts}"
    #)
    #carts[cart_id][item_sku] = cart_item.quantity
    #return status.HTTP_204_NO_CONTENT


class CheckoutResponse(BaseModel):
    total_potions_bought: int
    total_gold_paid: int


class CartCheckout(BaseModel):
    payment: str

# JOIN cart_items with potions to receive what was ordered. Update potions.inventory for each tem and adds gold to global_inventory
@router.post("/{cart_id}/checkout", response_model=CheckoutResponse)
def checkout(cart_id: int, cart_checkout: CartCheckout):
    """
    Handles the checkout process for a specific cart.
    """
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
                "order_id": cart_id
            }
        ).one_or_none()

        # I think don't try to return an error or else I will get null barrels, don't want that
        if existing: return CheckoutResponse(total_potions_bought=0,total_gold_paid=0)

        cart = connection.execute(
            sqlalchemy.text(
                """
                SELECT id
                FROM carts
                WHERE id = :cart_id
                """
            ),
            {
                "cart_id": cart_id
            }
        ).one_or_none()

        # Check if cart exists
        if cart is None:
            raise HTTPException(status_code=404, detail="Cart not found")

        # Get all items in the cart with potion details
        # Joins cart_items and potions so we get price and inventory too
        items = connection.execute(
            sqlalchemy.text(
                """
                SELECT potions.sku, potions.price, potions.id as potion_id, ci.quantity,
                COALESCE(SUM(ale.potion_change), 0) as inventory
                FROM cart_items ci
                JOIN potions ON ci.potion_id = potions.id
                LEFT JOIN account_ledger_entries ale ON ale.potion_id = potions.id
                WHERE ci.cart_id = :cart_id
                GROUP BY potions.sku, potions.price, potions.id, ci.quantity
                """
            ),
            {
                "cart_id": cart_id
            }
        ).fetchall()

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
                "description": "Cart: Potions sold"
            }
        ).scalar_one()

        total_potions_bought = 0
        total_gold_added = 0

        # Check global inventory that counts from ledger for the total number of potions in inventory
        for item in items:
            # Check if enough in stock to be sold
            if item.inventory < item.quantity:
                raise HTTPException(status_code=404, detail=f"Not enough {item.sku} in inventory")

            total_potions_bought += item.quantity
            total_gold_added += item.price * item.quantity

            # Insert into account_ledger_entries
            connection.execute(
                sqlalchemy.text
                    (
                    """
                    INSERT INTO account_ledger_entries (account_transaction_id, gold, potion_id, potion_change)
                    VALUES(:transaction_id, :gold_added, :potion_id, :potion_change)
                    """
                ),
                {
                    "transaction_id": transaction,
                    "gold_added": +item.price * item.quantity,
                    "potion_id": item.potion_id,
                    "potion_change": -item.quantity
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
                "order_id": cart_id,
                "response": "processed"
            }
        )

    return CheckoutResponse(
        total_potions_bought=total_potions_bought,
        total_gold_paid=total_gold_added
    )
