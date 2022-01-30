SELECT SIGN((ST."dealFunds"::DECIMAL - ST.FEE::DECIMAL) - (BT."dealFunds"::DECIMAL - BT.FEE::DECIMAL)) AS SIGN,
	SUM((ST."dealFunds"::DECIMAL - ST.FEE::DECIMAL) - (BT."dealFunds"::DECIMAL - BT.FEE::DECIMAL)) AMT
FROM TRADE_PAIRS TP
JOIN TRADES BT ON TP.BUY_ID = BT.ID
JOIN TRADES ST ON TP.SELL_ID = ST.ID
WHERE BT."createdAt"::DECIMAL >= {timestamp}
GROUP BY SIGN((ST."dealFunds"::DECIMAL - ST.FEE::DECIMAL) - (BT."dealFunds"::DECIMAL - BT.FEE::DECIMAL))