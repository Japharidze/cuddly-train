SELECT KUCOIN_NAME,
	COUNT(*) AS COUNT_OF_TRADES,
	SUM(PROFIT) AS SUM_PROFIT
FROM PUBLIC.COINS C
JOIN TRADES T ON T.SYMBOL = C.KUCOIN_NAME
LEFT JOIN TRADE_PAIRS TD ON T.ID = TD.BUY_ID
WHERE C.ALLOW_TRADE = 1
AND T."createdAt" > {timestamp}
GROUP BY KUCOIN_NAME