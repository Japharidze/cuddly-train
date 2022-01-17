select
    c.binance_name symbol,
    bt."createdAt" start_time,
    st."createdAt" end_time,
    tp.profit
from trade_pairs tp 
    join trades bt on tp.buy_id = bt.id
    join trades st on tp.sell_id = st.id
    join coins c on bt.symbol = c.kucoin_name