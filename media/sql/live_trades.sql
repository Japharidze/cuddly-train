select
    t.symbol,
    t."createdAt",
    t."dealSize",
    t."dealFunds"::DECIMAL / t."dealSize"::DECIMAL as Price
from coins c
    join trades t 
        on c.bought_id = t.id
where c.bought_id <> ''