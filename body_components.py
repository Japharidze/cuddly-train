import dash
from datetime import datetime

from dash import html
from dash.dash_table import DataTable

from data import query_data, fetch_balance
from utils import get_db_timestamp
from config import colors


def generate_trading_on_table(interval='today'):
    tmstmp = get_db_timestamp(interval)
    tab_data = query_data('trading_on', timestamp=tmstmp)
    tab_data['sum_profit'] = tab_data['sum_profit'].map(
        lambda x: '{:.2f} %'.format(x)
    )
    tab_data.columns = ['Coin', 'Count', 'Profit']

    table = DataTable(
        columns=[{'name': i, 'id': i} for i in tab_data.columns],
        data=tab_data.to_dict('records'),
        fixed_rows={'headers': True},
        style_table={'maxHeight': '300px', 'overflowY': 'auto'},
        style_header={'fontWeight': 'bold'},
        style_cell={'textAlign': 'left'},
        style_cell_conditional=[
            {'if': {'column_id': 'Count'},
            'width': '180px'}
        ],
        # style_data={'backgroundColor': 'gray'},
        style_data_conditional=[
            {
                'if': {'column_id': 'Profit'},
                'color': colors.CANDLE_GREEN,
            },
            {
                'if': {
                    'filter_query': '{Profit} contains "-"',
                    'column_id': 'Profit'
                },
                'color': colors.CANDLE_RED,
            },
            {
                'if': {
                    'filter_query': '{Profit} = "nan %"',
                    'column_id': 'Profit'
                },
                'color': 'black',
            },
            {
                'if': {
                    'state': 'active'
                },
                'backgroundColor': 'silver',
                'border': '1px solid black'
            }
        ]
    )

    return table


table = generate_trading_on_table() # This needs to be changed, moved only cuz it's parameters needed below

def generate_live_trades_table():
    data = query_data('live_trades')
    data['Buy Time'] = (data['Buy Time']/1000).map(
        lambda x: datetime.utcfromtimestamp(x).strftime('%m/%d/%Y %H:%M:%S')
    )

    live_table = DataTable(
        columns=[{'name': i, 'id': i} for i in data.columns],
        data = data.to_dict('records'),
        fixed_rows={'headers': True},
        style_table=table.style_table,
        style_header=table.style_header,
        style_cell=table.style_cell,
        style_data_conditional=table.style_data_conditional
    )

    return live_table

def generate_last_trades_table():
    data = query_data('last_trades')
    data['Profit'] = data['Profit'].map(
        lambda x: '{:.2f} %'.format(x)
    )

    res = DataTable(
        columns = [{'name': i, 'id': i} for i in data.columns],
        data = data.to_dict('records'),
        fixed_rows = {'headers': True},
        style_table = table.style_table,
        style_header=table.style_header,
        style_cell=table.style_cell,
        style_data_conditional=table.style_data_conditional
    )

    return res


def generate_pool_data(interval='today'):
    prefix = 'pool_'
    pools = ['up', 'down', 'profit', 'pool']
    pool_data = dict()
    children = []

    # define interval timestamp
    tmstmp = get_db_timestamp(interval)

    # fetch data from db
    data = query_data('get_pool_data', timestamp=tmstmp)
    pool_data['up'] = data[data['sign'] == 1]['amt'].sum()
    pool_data['down'] = data[data['sign'] == -1]['amt'].sum()
    pool_data['profit'] = (data['amt'] * data['sign']).sum()
    pool_data['pool'] = fetch_balance()

    # generate children result
    for pool in pools:
        children.append(
            html.Div(
                id=prefix + pool,
                children=[
                    html.Label(pool.upper()),
                    html.Label('{:<09}'.format(pool_data[pool]), className='pool_size')
                ]
            )
        )

    return children
