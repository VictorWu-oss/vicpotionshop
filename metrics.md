1. Sales Per Potion By Hour

```sql
SELECT 
DATE_TRUNC('hour', at.created_at) as hour,
    p.name as potion_name,
    SUM(-ale.potion_change) as potions_sold
FROM account_ledger_entries ale
JOIN account_transactions at ON ale.account_transaction_id = at.id
JOIN potions p ON ale.potion_id = p.id
WHERE ale.potion_change < 0
GROUP BY DATE_TRUNC('hour', at.created_at), p.name
ORDER BY hour, potion_name
```



| hour                | potion_name   | potions_sold |
| ------------------- | ------------- | ------------ |
| 2026-04-29 20:00:00 | Red Potion    | 5            |
| 2026-04-30 04:00:00 | Red Potion    | 5            |
| 2026-05-01 02:00:00 | Yellow Potion | 10           |
| 2026-05-01 08:00:00 | Red Potion    | 28           |
| 2026-05-01 10:00:00 | Red Potion    | 2            |
| 2026-05-01 16:00:00 | Red Potion    | 17           |
| 2026-05-01 18:00:00 | Red Potion    | 33           |
| 2026-05-01 22:00:00 | Red Potion    | 50           |
| 2026-05-02 16:00:00 | Yellow Potion | 11           |
| 2026-05-02 20:00:00 | Blue Potion   | 4            |
| 2026-05-02 22:00:00 | Blue Potion   | 3            |
| 2026-05-03 00:00:00 | Blue Potion   | 7            |
| 2026-05-03 00:00:00 | Yellow Potion | 6            |
| 2026-05-03 04:00:00 | Yellow Potion | 9            |
| 2026-05-03 06:00:00 | Yellow Potion | 2            |
| 2026-05-03 08:00:00 | Blue Potion   | 7            |
| 2026-05-03 08:00:00 | Yellow Potion | 14           |
| 2026-05-09 16:00:00 | Yellow Potion | 11           |
| 2026-05-09 18:00:00 | Blue Potion   | 5            |
| 2026-05-09 20:00:00 | Blue Potion   | 2            |
| 2026-05-10 00:00:00 | Blue Potion   | 7            |
| 2026-05-10 00:00:00 | Yellow Potion | 6            |
| 2026-05-10 02:00:00 | Yellow Potion | 2            |
| 2026-05-10 04:00:00 | Yellow Potion | 9            |
| 2026-05-10 08:00:00 | Blue Potion   | 7            |
| 2026-05-10 08:00:00 | Yellow Potion | 14           |

Observations:
It looks like Red Potions sell in large bursts, probably due to an influx of warrior class customers. 
Yellow potions have steady sails and Blue potions primarily sell after midnight.


2. Barrel Types Reference Table
```sql
SELECT
    sku,
    CASE 
        WHEN sku LIKE '%RED%' THEN 'Red'
        WHEN sku LIKE '%GREEN%' THEN 'Green'
        WHEN sku LIKE '%BLUE%' THEN 'Blue'
        WHEN sku LIKE '%DARK%' THEN 'Dark'
        ELSE 'Mixed'
    END as liquid_type,
    CASE
        WHEN sku LIKE 'LARGE%' THEN 10000
        WHEN sku LIKE 'MEDIUM%' THEN 2500
        WHEN sku LIKE 'SMALL%' THEN 500
        WHEN sku LIKE 'MINI%' THEN 200
        ELSE 100
    END as ml_per_barrel,
    price
FROM barrels
```
| sku                 | liquid_type | ml_per_barrel | price |
| ------------------- | ----------- | ------------- | ----- |
| LARGE_RED_BARREL    | Red         | 10000         | 500   |
| LARGE_GREEN_BARREL  | Green       | 10000         | 400   |
| LARGE_BLUE_BARREL   | Blue        | 10000         | 600   |
| LARGE_DARK_BARREL   | Dark        | 10000         | 750   |
| MEDIUM_RED_BARREL   | Red         | 2500          | 250   |
| MEDIUM_GREEN_BARREL | Green       | 2500          | 250   |
| MEDIUM_BLUE_BARREL  | Blue        | 2500          | 300   |
| SMALL_RED_BARREL    | Red         | 500           | 100   |
| SMALL_GREEN_BARREL  | Green       | 500           | 100   |
| SMALL_BLUE_BARREL   | Blue        | 500           | 100   |
| MINI_RED_BARREL     | Red         | 200           | 60    |
| MINI_GREEN_BARREL   | Green       | 200           | 60    |
| MINI_BLUE_BARREL    | Blue        | 200           | 60    |
Large barrels offer the best cost per ml. Dark barrels are the most expensive and green large barrels are the cheapest.

3. Customer Class vs Potion Type
```sql
SELECT 
    c.customer_class,
    p.name as potion_name,
    COUNT(*) as purchases
FROM carts c
JOIN cart_items ci ON ci.cart_id = c.id
JOIN potions p ON p.id = ci.potion_id
GROUP BY c.customer_class, p.name
ORDER BY purchases DESC
```

| Customer Class                 | Potion | Purchases 
| ------------------- | ----------- | ------------- | 
| Warrior    | Red Potion         | 33         | 
| Hunter  | Yellow Potion       | 24         | 
| Runesmith   | Blue Potion        | 8         | 

Warriors are my most frequent buyers and strongly prefer Red Potions. Hunters exclusively buy Yellow potions.
Runesmiths prefer Blue potions. 


4. Revenue by Potion Type
```sql
SELECT 
    p.name as potion_name,
    SUM(-ale.potion_change) as total_sold,
    p.price,
    SUM(-ale.potion_change) * p.price as total_gold_earned
FROM account_ledger_entries ale
JOIN potions p ON ale.potion_id = p.id
WHERE ale.potion_change < 0
GROUP BY p.name, p.price
ORDER BY total_gold_earned DESC
```

| Potion     | Total Sold | Price | Total Gold Earned | 
|------------|------------|-------|-------------------|
| Red Potion | 140        | 30    | 4200              | 
| Yellow Potion     | 94         | 40    | 3760              | 
| Blue Potion  | 42         | 35    | 1470              | 

Red potions generate the most revenue despite the lowest price due to high influx of warriors.
Yellow potions have the best price to sales ratio. Blue potions are underwhelming. Total revenue is 9430 gold.