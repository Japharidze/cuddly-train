from datetime import datetime

import dash
import pandas as pd
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from data import fetch_data


klines = fetch_data()
df = pd.DataFrame(klines[1:], columns=klines[0])


dash = dash.Dash(__name__)
server = dash.server

dash.layout = html.Div([
    dcc.Checklist(
        id='toggle-rangeslider',
        options=[{'label': 'Include Rangeslider', 
                  'value': 'slider'}],
        value=['slider']
    ),
    dcc.Graph(id="graph"),
])

@dash.callback(
    Output("graph", "figure"), 
    [Input("toggle-rangeslider", "value")])
def display_candlestick(value):
    fig = go.Figure(go.Candlestick(
        x=df['DateTime'],
        open=df['Open'],
        high=df['High'],
        low=df['Low'],
        close=df['Close']
    ))

    fig.update_layout(
        xaxis_rangeslider_visible='slider' in value
    )

    return fig

# start Flask server
if __name__ == '__main__':
    dash.run_server(
        debug=True,
        host='0.0.0.0',
        port=8050
    )