import requests
import json 
rest = 'https://3xw7x7ql7f.execute-api.ap-northeast-2.amazonaws.com/stg/dep'

g_event = {'symbol': 'SHIBUSDT',
         'interval': '1m', 
         'start_time': 1640901096000,
         'end_time':  1640911706000
        }

def fetch_data(**kwargs):
    event = dict(**kwargs)
    if bool(event):
        response = requests.get(rest, params=event)
    else:
        response = requests.get(rest, params=g_event)
    return response.json().get('klines')