import os

class DBConfig:
    URL = os.environ.get('DATABASE_URL')
    # URL = 'postgresql://postgres:admin@localhost:5432/kucoin'

class Colors:
    CANDLE_RED = '#ef5350'
    CANDLE_GREEN = '#26a69a'
    EMA5 = 'DarkOrange'
    EMA9 = 'LightSeaGreen'
    EMA12 = 'RoyalBlue'



db_config = DBConfig()
colors = Colors()