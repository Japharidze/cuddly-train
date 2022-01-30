select
    c.binance_name "Coin",
    (bt."dealFunds"::DECIMAL / bt."dealSize"::DECIMAL)::DECIMAL(10,8) as "Buy price",
    (st."dealFunds"::DECIMAL / st."dealSize"::DECIMAL)::DECIMAL(10,8) as "Sell price",
    tp.profit as "Profit"
from trade_pairs tp 
    join trades bt on tp.buy_id = bt.id
    join trades st on tp.sell_id = st.id
    join coins c on bt.symbol = c.kucoin_name
order by bt."createdAt" desc
fetch first 20 rows only