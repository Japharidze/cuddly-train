from datetime import date, timedelta
from datetime import datetime

import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from data import fetch_binance_data, query_trade_data, query_coins


trades = query_trade_data()
coins = query_coins()

dash = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}])
server = dash.server

dash.layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H1('Bot performance', className='text-center')
        ], width={'size': 8, 'offset': 2})
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col(
            [dcc.Dropdown(id='name_dpdn', multi=True, value='all_values',
                options=[{'label':x, 'value':x} for x in coins] +\
                        [{'label':'All', 'value':'all_values'}]
                )], width={'size': 8, 'offset': 2})
        ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.DatePickerRange(
                id='date-range',
                min_date_allowed=date.today() - timedelta(30),
                max_date_allowed=date.today(),
                start_date=date.today() - timedelta(7),
                end_date=date.today()
            )
        ], width={'size': 2, 'offset': 2}),
        dbc.Col([
            dcc.Input(
                id='min_percent',
                type='number',
                placeholder='Min %',
                value=-100,
            )
        ], width=1),
        dbc.Col([
            dcc.Input(
                id='max_percent',
                type='number',
                placeholder='Max %',
                value=100
            )
        ], width=1),
        dbc.Col([
            dbc.Button('Submit', id='submit', n_clicks=0),
        ], width={'size': 1, 'offset': 1})
    ], align='center'),
    html.Br(),
    html.Div(id='container', children=[])
    # ,html.Div(id='debug')
])


@dash.callback(
    Output(component_id="container", component_property="children"),
    [
        State(component_id='container', component_property='children'),
        State(component_id="name_dpdn", component_property="value"),
        State(component_id="date-range", component_property="start_date"),
        State(component_id="date-range", component_property="end_date"),
        State(component_id="min_percent", component_property="value"),
        State(component_id="max_percent", component_property="value"),
        Input(component_id="submit", component_property="n_clicks")
    ])
def update_container(container, symbols, start_date, end_date, min_percent, max_percent, n_clicks):
    container = []

    start_time = datetime.strptime(start_date or '2021-12-14', '%Y-%m-%d').timestamp()
    end_time = datetime.strptime(end_date or '2021-12-14', '%Y-%m-%d').timestamp()

    params = {'profit': (min_percent, max_percent),
              'period': (start_time, end_time)}
    if symbols != 'all_values':
        params['symbols'] = symbols

    trades = query_trade_data(**params)
    klines = fetch_binance_data(trades)
    print(f'Printing number of charts: {len(klines)}')

    for i, (row, kline) in enumerate(klines):
        symbol = row['symbol']
        profit = row['profit']
        fig = go.Figure([
                go.Candlestick(
                    x=kline['DateTime'],
                    open=kline['Open'],
                    high=kline['High'],
                    low=kline['Low'],
                    close=kline['Close'],
                    name='Candle'),
                go.Scatter(x=kline['DateTime'], y=kline['EMA10'],
                           line={'color':'green', 'width': 1},
                           name='EMA10')
            ], layout_title_text='{} {:0.2f}%'.format(symbol, profit))
        fig.update_layout(xaxis_rangeslider_visible=False)

        new_child = html.Div(
            dbc.Row(dbc.Col(
                [dcc.Graph(className='graph', id=f'graph{i}', figure=fig)],
                width={'size':8, 'offset':2}
            ))
        )

        container.append(new_child)
    return container


# start Flask server
if __name__ == '__main__':
    dash.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050
    )