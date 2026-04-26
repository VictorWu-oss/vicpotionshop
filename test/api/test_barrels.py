from src.api.barrels import (
    calculate_barrel_summary,
    create_barrel_plan,
    Barrel,
    BarrelOrder,
)
from typing import List


def test_barrel_summary_gold_paid() -> None:
    barrels = [
        Barrel(sku="SMALL_RED_BARREL", ml_per_barrel=500, potion_type=[1.0, 0, 0, 0], price=100, quantity=1),
        Barrel(sku="SMALL_GREEN_BARREL", ml_per_barrel=500, potion_type=[0, 1.0, 0, 0], price=150, quantity=2),
    ]
    summary = calculate_barrel_summary(barrels)
    assert summary.gold_paid == 400  # 100 + 150*2


def test_barrel_summary_ml_added() -> None:
    barrels = [
        Barrel(sku="SMALL_RED_BARREL", ml_per_barrel=500, potion_type=[1.0, 0, 0, 0], price=100, quantity=2),
    ]
    summary = calculate_barrel_summary(barrels)
    assert summary.red_ml_added == 1000
    assert summary.green_ml_added == 0
    assert summary.blue_ml_added == 0
    assert summary.dark_ml_added == 0


def test_barrel_plan_buys_affordable() -> None:
    catalog = [
        Barrel(sku="SMALL_RED_BARREL", ml_per_barrel=500, potion_type=[1.0, 0, 0, 0], price=100, quantity=10),
        Barrel(sku="SMALL_GREEN_BARREL", ml_per_barrel=500, potion_type=[0, 1.0, 0, 0], price=100, quantity=10),
    ]
    orders = create_barrel_plan(gold=200, total_potions=0, total_ml=0, wholesale_catalog=catalog)
    assert len(orders) == 2
    assert all(isinstance(o, BarrelOrder) for o in orders)


def test_barrel_plan_cant_afford() -> None:
    catalog = [
        Barrel(sku="SMALL_RED_BARREL", ml_per_barrel=500, potion_type=[1.0, 0, 0, 0], price=100, quantity=10),
    ]
    orders = create_barrel_plan(gold=50, total_potions=0, total_ml=0, wholesale_catalog=catalog)
    assert len(orders) == 0


def test_barrel_plan_too_many_potions() -> None:
    catalog = [
        Barrel(sku="SMALL_RED_BARREL", ml_per_barrel=500, potion_type=[1.0, 0, 0, 0], price=100, quantity=10),
    ]
    orders = create_barrel_plan(gold=1000, total_potions=15, total_ml=0, wholesale_catalog=catalog)
    assert len(orders) == 0


def test_barrel_plan_ml_cap() -> None:
    catalog = [
        Barrel(sku="SMALL_RED_BARREL", ml_per_barrel=500, potion_type=[1.0, 0, 0, 0], price=100, quantity=10),
    ]
    # Already at 9900 ml, barrel would push to 10400 which exceeds 10000
    orders = create_barrel_plan(gold=1000, total_potions=0, total_ml=9900, wholesale_catalog=catalog)
    assert len(orders) == 0