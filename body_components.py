import dash
from datetime import datetime, date, timedelta

from dash import html
from dash.dash_table import DataTable

from data import query_data
from config import colors


tab_data = query_data('trading_on')
tab_data['sum_profit'] = tab_data['sum_profit'].map(
    lambda x: '{:.2f} %'.format(x)
)
tab_data.columns = ['Coin name', 'Count', 'Profit']

table = DataTable(
    columns=[{'name': i, 'id': i} for i in tab_data.columns],
    data=tab_data.to_dict('records'),
    fixed_rows={'headers': True},
    style_table={'height': '300px', 'overflowY': 'auto'},
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




def update_live_trades_table():
    data = query_data('live_trades')
    data['createdAt'] = (data['createdAt']/1000).map(
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


def update_pool_data(interval='today'):
    prefix = 'pool_'
    pools = ['up', 'down', 'pool']
    pool_data = dict()
    children = []

    # define interval timestamp
    if interval == 'today':
        dt = datetime.combine(date.today(), datetime.min.time())
    if interval == 'week':
        dt = date.today()
        dt = dt - timedelta(days=dt.weekday())
        dt = datetime.combine(dt, datetime.min.time())
    if interval == 'month':
        dt = date.today().replace(day=1)
        dt = datetime.combine(dt, datetime.min.time())
    interval = dt.timestamp() * 1000

    # fetch data from db
    data = query_data('get_pool_data', timestamp=interval)
    pool_data['up'] = data[data['sign'] == 1]['amt'].sum()
    pool_data['down'] = data[data['sign'] == -1]['amt'].sum()
    pool_data['pool'] = (data['amt'] * data['sign']).sum()

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