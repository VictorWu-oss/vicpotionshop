1. Sales Per Potion By Hour

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


3. Customer Class vs Potion Type




4. Revenue by Potion Type