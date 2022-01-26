import dash

from dash.dash_table import DataTable

from data import query_data
from config import colors

tab_data = query_data('trading_on')
tab_data['sum_profit'] = tab_data['sum_profit'].map(
    lambda x: '{:.2f} %'.format(x)
)

table = DataTable(
    columns=[{'name': i, 'id': i} for i in tab_data.columns],
    data=tab_data.to_dict('records'),
    fixed_rows={'headers': True},
    style_table={'height': '300px', 'overflowY': 'auto'},
    style_header={'fontWeight': 'bold'},
    style_cell={'textAlign': 'left'},
    style_cell_conditional=[
        {'if': {'column_id': 'count_of_trades'},
         'width': '180px'}],
    style_data_conditional=[
        {
            'if': {'column_id': 'sum_profit'},
            'color': colors.CANDLE_GREEN,
        },
        {
            'if': {
                'filter_query': '{sum_profit} contains "-"',
                'column_id': 'sum_profit'
            },
            'color': colors.CANDLE_RED,
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