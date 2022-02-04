select
    t.symbol "Coin",
    t."dealSize"::DECIMAL(10,6) "Deal Size",
    (t."dealFunds"::DECIMAL / t."dealSize"::DECIMAL)::DECIMAL(10,6) as "Price",
    t."createdAt" "Buy Time"
from coins c
    join trades t 
        on c.bought_id = t.id
where c.bought_id <> ''