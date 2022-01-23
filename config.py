import os

class DBConfig:
    URL = os.environ.get('DATABASE_URL')

class Colors:
    CANDLE_RED = '#ef5350'
    CANDLE_GREEN = '#26a69a'


db_config = DBConfig()
colors = Colors()