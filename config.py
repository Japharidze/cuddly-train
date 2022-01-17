import os

class DBConfig:
    URL = os.environ.get('DATABASE_URL')


db_config = DBConfig()