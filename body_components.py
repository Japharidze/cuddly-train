import dash
from datetime import datetime

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
         'width': '180px'}],
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