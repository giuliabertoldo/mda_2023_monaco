import pandas as pd
import dash
from dash import html
from dash import dcc

import numpy as np
import datetime
import plotly
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

from data import df


app = dash.Dash(__name__,title='MDA_project', external_stylesheets=[dbc.themes.BOOTSTRAP],serve_locally = False,use_pages=True)

server = app.server

navBar = html.Nav(children=[
        dcc.Link('Overview',
                href='/',
                className='link',),
        dcc.Link('Details',
                href='/details',
                className='link',),
        dcc.Link('Model',
                href='/model',
                className='link',),
                ],
        style={
        'display': 'flex',
        "background-color": "#F7F7F7",
        "height": "50px",
        "align-items": "center",
        "justify-content": "space-between",
        "margin-left": "500px",  
        "margin-right": "500px", 
        "font-family": "'Roghiska', sans-serif",
        },
)


app.layout = html.Div(
    [ 
        html.Div(children=[html.H1(children='MDA Project', className="header-title"),
                            html.H2(children='Monaco',className="header-description"),
                            ],
                            className="header",
        ),
        html.Link(
            rel="stylesheet",
            href="/assets/styles.css"
        ),
        navBar,
        dash.page_container,
])


if __name__ == '__main__':
    app.run_server(debug=True, use_reloader=False)