import requests
from pathlib import Path
from threading import Thread

from psycopg2 import connect
from pandas import read_sql, DataFrame

from config import LambdaConfig, RestConfig, DBConfig

conn = connect(DBConfig.URL)
lambda_url = LambdaConfig.URL
rest = RestConfig.URL

g_event = {'symbol': 'SHIBUSDT',
         'interval': '1m', 
         'start_time': 1640901096000,
         'end_time':  1640911706000
        }

def fetch_data_test(**kwargs):
    event = dict(**kwargs)
    if bool(event):
        response = requests.get(lambda_url, params=event)
    else:
        response = requests.get(lambda_url, params=g_event)
    return response.json().get('klines')

def fetch_binance_data(data: DataFrame, interval='1m'):
    data = data.groupby('symbol').agg({
        'start_time': 'min',
        'end_time': 'max',
        'profit': 'sum'
    }).reset_index()

    res = []
    def fetch(row):
        params = dict(row)
        params['interval'] = interval
        response = requests.get(lambda_url, params=params)
        klines = response.json().get('klines')
        if klines:
            res.append((row, DataFrame(klines[1:], columns=klines[0])))

    threads = []
    for _, row in data.iterrows():
        t = Thread(target=fetch, args=[row], daemon=True)
        threads.append(t)
        t.start()
        if _ > 10:
            break

    for t in threads:
        t.join()

    return res

def query_trade_data(**kwargs):
    """DOCSTRING"""

    with open('media/sql/get_trades.sql') as f:
        query = f.read()

    dt = read_sql(query, conn)
    for k, v in kwargs.items():
        if k == 'profit':
            dt = dt[dt['profit'].between(v[0], v[1])]
        elif k == 'symbols':
            dt = dt[dt['symbol'].isin(v)]
        elif k == 'period':
            dt = dt[(dt['start_time']/1000).between(v[0], v[1])]

    return dt

def query_coins():
    """DOCSTRING"""

    with open('media/sql/get_coins.sql') as f:
        query = f.read()

    dt = read_sql(query, conn)
    return dt

def query_data(sql_file: str, **kwargs):
    if not sql_file:
        return
    path = Path('media/sql', sql_file + '.sql')

    with open(path) as f:
        query = f.read()

    if kwargs:
        for k, v in kwargs.items():
            query = query.replace(f'{{{k}}}', f'{v}')

    dt = read_sql(query, conn)
    return dt

def fetch_balance():
    """DOCSTRING"""

    # generate url
    url = f'{rest}get_balance'
    try:
        response = requests.get(url)
    except:
        raise Exception(f'RestError while requesting get_balance from {url}')

    return response.text