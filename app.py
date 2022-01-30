from datetime import date, timedelta
from datetime import datetime

import dash
from numpy import array
from pandas import melt
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from data import fetch_binance_data, query_trade_data, query_coins
from utils import candle_interval_generator
from config import colors
from body_components import (generate_live_trades_table, generate_pool_data,
                            generate_trading_on_table, generate_last_trades_table)


trades = query_trade_data()
coins = query_coins()['binance_name']

dash = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}])
server = dash.server

dash.layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H4('DEFYTHEODDS - Dashboard - V1')
        ], width={'size': 6, 'offset': 2},
           className='header'),
        dbc.Col([
            html.Label(datetime.now().strftime('%m/%d/%Y $ %H:%M:%S'))
        ], width={'size': 2},
           className='header')
    ]),
    dbc.Row([
        dbc.Col([
            html.H1('Current Stats')
        ], width={'size': 3, 'offset': 5})
    ]),
    dbc.Row([
        dbc.Col([
            dcc.Tabs(id='interval-tabs', value='today', children=[
                dcc.Tab(label='Today', value='today'),
                dcc.Tab(label='This Week', value='week'),
                dcc.Tab(label='This Month', value='month')
            ])
        ], width={'size': 8, 'offset': 2})
    ]),
    dbc.Row([
        dbc.Col([
            html.H2('Trading on'),
            html.Div(id='trading-on-div',
                     children=generate_trading_on_table())
        ], width={'size': 4, 'offset': 2}),
        dbc.Col([
            html.H2('Current Pool'),
            html.Div(
                id='pool_data',
                children=generate_pool_data())
        ], width={'size': 3, 'offset': 1})
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.H2('Live Trades'),
            html.Div(id='live_table',
                     children=generate_live_trades_table()),
            dcc.Interval(
                id='live_trading_interval',
                interval=1000,
                n_intervals=0
            )
        ], width={'size': 4, 'offset': 2}),
        dbc.Col([
            html.H2('Last 20 Trades'),
            html.Div(id='last-20-trades',
                     children=generate_last_trades_table()),
        ], width={'size': 4})
    ]),
    dbc.Row([
        dbc.Col([
            html.H1('Bot performance', className='text-center')
        ], width={'size': 8, 'offset': 2})
    ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.Label('Coins'),
            dcc.Dropdown(id='name_dpdn', multi=True, # value='all_values',
                options=[{'label':x, 'value':x} for x in coins] +\
                        [{'label':'All', 'value':'all_values'}]
                )], width={'size': 8, 'offset': 2})
        ]),
    html.Br(),
    dbc.Row([
        dbc.Col([
            html.Label('Date Interval'),
            dcc.DatePickerRange(
                id='date-range',
                min_date_allowed=date.today() - timedelta(30),
                max_date_allowed=date.today(),
                start_date=date.today() - timedelta(7),
                end_date=date.today()
            )
        ], width={'size': 2, 'offset': 2}),
        dbc.Col([
            html.Label('Candle Interval'),
            dcc.Dropdown(id='interval_dpdn',
                         # value='3m',
                         clearable=False)],
            width=2),
        dbc.Col([
            html.Label('Profit range'),
            dcc.Input(
                id='min_percent',
                type='number',
                placeholder='Min %',
                value=-100,
            )
        ], width=1),
        dbc.Col([
            html.Label('Min/Max'),
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
    dcc.Loading(id='chart_container', children=[])
], className='container')


@dash.callback(
    Output(component_id="chart_container", component_property="children"),
    [
        State(component_id='chart_container', component_property='children'),
        State(component_id="name_dpdn", component_property="value"),
        State(component_id="date-range", component_property="start_date"),
        State(component_id="date-range", component_property="end_date"),
        State(component_id='interval_dpdn', component_property='value'),
        State(component_id="min_percent", component_property="value"),
        State(component_id="max_percent", component_property="value"),
        Input(component_id="submit", component_property="n_clicks")
    ])
def update_container(container, symbols, start_date, end_date, interval, min_percent, max_percent, n_clicks):
    if not n_clicks:
        return container
    container = []

    start_time = datetime.strptime(start_date or '2021-12-14', '%Y-%m-%d').timestamp()
    end_time = datetime.strptime(end_date or '2021-12-14', '%Y-%m-%d').timestamp()

    params = {'profit': (min_percent, max_percent),
              'period': (start_time, end_time)}

    if symbols:
        if 'all_values' not in symbols:
            params['symbols'] = symbols

    trades = query_trade_data(**params)
    klines = fetch_binance_data(trades, interval=interval or '3m')
    print(f'Printing number of charts: {len(klines)}')

    for i, (row, kline) in enumerate(klines):
        symbol = row['symbol']
        profit = row['profit']

        fig = make_subplots(specs=[[{'secondary_y': True}]])
        # add Candlestick
        fig.add_trace(
            go.Candlestick(
                x=kline['DateTime'],
                open=kline['Open'],
                high=kline['High'],
                low=kline['Low'],
                close=kline['Close'],
                name='Candle',
                increasing={'fillcolor': colors.CANDLE_GREEN, 'line': {'color': colors.CANDLE_GREEN}},
                decreasing={'fillcolor': colors.CANDLE_RED, 'line': {'color': colors.CANDLE_RED}}),
            secondary_y=True)

        # add EMAS
        emas = ['EMA5', 'EMA9', 'EMA12']
        for ema in emas:
            if ema in kline.columns:
                fig.add_trace(
                    go.Scatter(x=kline['DateTime'], y=kline[ema],
                               name=ema,
                               line={'color': getattr(colors, ema), 'width': 1}),
                    secondary_y=True
                )

        # add Volume
        color = array([colors.CANDLE_RED] * kline.shape[0], dtype='object')
        mask = kline['Open'] < kline['Close']
        color[mask] = colors.CANDLE_GREEN
        fig.add_trace(
            go.Bar(
                x=kline['DateTime'],
                y=kline['Volume'],
                name='Volume',
                opacity=0.5,
                marker={'color': color}),
            secondary_y=False)

        # add trade marks
        coin_trades = trades[trades['symbol'] == symbol]
        fig.add_trace(
            go.Scatter(x=(coin_trades['start_time']/1000).map(datetime.utcfromtimestamp),
                       y=coin_trades['buy_price'],
                       name='Buy points',
                       mode='markers',
                       marker={'color': colors.CANDLE_GREEN, 'size': 15, 'symbol': 'triangle-up',
                               'line': {'color': 'white', 'width': 1}}),
            secondary_y=True
        )
        fig.add_trace(
            go.Scatter(
                x=(coin_trades['end_time']/1000).map(datetime.utcfromtimestamp),
                y=coin_trades['sell_price'],
                name='Sell points',
                mode='markers',
                marker={'color': colors.CANDLE_RED, 'size': 15, 'symbol': 'triangle-down',
                        'line': {'color': 'white', 'width': 1}}
            ),
            secondary_y=True
        )

        fig.update_layout(
            title_text='{} {:0.2f}%'.format(symbol, profit),
            xaxis_rangeslider_visible=False,
            height=600,
            paper_bgcolor='#161a25',
            plot_bgcolor='#161a25',
            font_color='Silver',
            yaxis={'title': 'Volume'},
            yaxis2={'title': 'Price'}
        )
        fig.update_xaxes(showline=True, gridcolor='#242732', title='Time')
        fig.update_yaxes(showline=True, gridcolor='#242732')

        new_child = html.Div([
            dbc.Row(dbc.Col([
                dcc.Graph(className='graph', id=f'graph{i}', figure=fig)],
                width={'offset':1}
            ))
        ])

        container.append(new_child)
    return container

# callback for dynamic Dropdown
@dash.callback(
    Output('interval_dpdn', 'options'),
    [Input('date-range', 'start_date'),
     Input('date-range', 'end_date')]
)
def update_candle_interval_dpdn(start_date, end_date):
    start_time = datetime.strptime(start_date or '2021-12-14', '%Y-%m-%d')
    end_time = datetime.strptime(end_date or '2021-12-14', '%Y-%m-%d')
    return candle_interval_generator(start_time, end_time)

# callback for trading on table
@dash.callback(
    Output('trading-on-div', 'children'),
    [Input('interval-tabs', 'value')]
)
def update_trading_on_table(interval):
    return generate_trading_on_table(interval)

# callback for live trading table
@dash.callback(
    Output('live_table', 'children'),
    [Input('live_trading_interval', 'n_intervals')]
)
def update_live_table(n_intervals):
    return generate_live_trades_table()

# callback for last trades table
@dash.callback(
    Output('last-20-trades', 'children'),
    [Input('live_trading_interval', 'n_intervals')]
)
def update_last_trades_table(_):
    return generate_last_trades_table()

# callback for pool data
@dash.callback(
    Output('pool_data', 'children'),
    [Input('interval-tabs', 'value')]
)
def update_pool_div(interval):
    return generate_pool_data(interval)

# start Flask server
if __name__ == '__main__':
    dash.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050
    )