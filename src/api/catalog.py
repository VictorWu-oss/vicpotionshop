from fastapi import APIRouter
from pydantic import BaseModel, Field
from typing import List, Annotated
import sqlalchemy
from src import database as db

router = APIRouter()

class CatalogItem(BaseModel):
    sku: Annotated[str, Field(pattern=r"^[a-zA-Z0-9_]{1,20}$")]
    name: str
    quantity: Annotated[int, Field(ge=1, le=10000)]
    price: Annotated[int, Field(ge=1, le=500)]
    potion_type: List[int] = Field(
        ...,
        min_length=4,
        max_length=4,
        description="Must contain exactly 4 elements: [r, g, b, d]",
    )


@router.get("/catalog/", tags=["catalog"], response_model=List[CatalogItem])
def get_catalog() -> List[CatalogItem]:
    """
    Retrieves the catalog of items. Each unique item combination should have only a single price.
    You can have at most 6 potion SKUs offered in your catalog at one time.
    """
    with db.engine.begin() as connection:
        potions = connection.execute(
            # LEFT join with ledger, connects potion to ledger entries
            # SUM potion_change to get curr inventory.
            # GROUP BY sorts the final output
            # HAVING used over WHERE bc there's aggregate functions. It also works only as a post-aggregate-op clause.
            sqlalchemy.text(
                """
                SELECT sku, name, inventory, red, green, blue, dark, price
                FROM potions 
                LEFT JOIN account_ledger_entries ON account_ledger_entries.potion_id = potions.id
                GROUP BY potions.id, potions.sku, potions.name, potions.red, potions.green, potions.blue, potions.dark, potions.price
                HAVING SUM(account_ledger_entries.potion_change) > 0
                """
            )
        ).fetchall()

    catalog = []
    for potion in potions:
        catalog.append(
            CatalogItem(
                sku=potion.sku,
                name=potion.name,
                quantity=potion.inventory,
                price=potion.price,
                potion_type=[potion.red, potion.green, potion.blue, potion.dark]
            )
        )
    return catalog
