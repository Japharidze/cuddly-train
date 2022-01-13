from datetime import date, timedelta
from datetime import datetime

import dash
import pandas as pd
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from data import fetch_data


klines = fetch_data()
df = pd.DataFrame(klines[1:], columns=klines[0])


dash = dash.Dash(__name__, external_stylesheets=[dbc.themes.COSMO],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}])
server = dash.server

# @dash.callback(
    # Output("graph", "figure"), 
    # [Input("toggle-rangeslider", "value")])
def display_candlestick(value=None):
    fig = go.Figure(go.Candlestick(
        x=df['DateTime'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    ))
    fig.update_layout(xaxis_rangeslider_visible=False)

    # fig.update_layout(
        # xaxis_rangeslider_visible='slider' in value
    # )

    return fig

dash.layout = html.Div([
    dbc.Row([
        dbc.Col([
            html.H1('Bot performance', className='text-center text-primary')
        ], width={'size': 8, 'offset': 2})
    ]),
    dbc.Row([
        dbc.Col(
            [dcc.Dropdown(id='name_dpdn', multi=True, value=['SHIBUSDT'],
                options=[{'label': x, 'value':x} for x in ['SHIBUSDT', 'RAME']
                ])], width={'size': 8, 'offset': 2})
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
                placeholder='Min %'
            )
        ], width=1),
        dbc.Col([
            dcc.Input(
                id='max_percent',
                type='number',
                placeholder='Max %'
            )
        ], width=1),
        dbc.Col([
            dbc.Button('Submit', id='submit', n_clicks=0),
        ], width={'size': 1, 'offset': 1})
    ], align='center'),
    html.Br(),
    dbc.Row([
        dbc.Col([
            dcc.Graph(id="graph", figure=display_candlestick()),
        ], width={'size': 8, 'offset': 2})
    ])
    ,html.Div(id='debug')
])


@dash.callback(
    Output(component_id="debug", component_property="children"),
    [
        State(component_id="name_dpdn", component_property="value"),
        State(component_id="date-range", component_property="start_date"),
        State(component_id="date-range", component_property="end_date"),
        State(component_id="min_percent", component_property="value"),
        State(component_id="max_percent", component_property="value"),
        Input(component_id="submit", component_property="n_clicks")
    ])
def update_candlestick(coins, start_date, end_date, min_percent, max_percent, n_clicks):

    start_time = datetime.strptime(start_date or '2021-12-14', '%Y-%m-%d').timestamp()
    end_time = datetime.strptime(end_date or '2021-12-14', '%Y-%m-%d').timestamp()
    for coin in coins:
        params = {'interval': '1m', 'start_time': int(start_time * 1000), 'end_time': int(end_time * 1000)}
        params['symbol'] = coin
        klines = fetch_data(**params)

    return coins


# start Flask server
if __name__ == '__main__':
    dash.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050
    )