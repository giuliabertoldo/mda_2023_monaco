import pandas as pd
import dash
from dash import html
from dash import dcc, callback

import numpy as np
import datetime
import plotly
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots
import plotly.graph_objects as go
import plotly.express as px

from data import df

dash.register_page(__name__)

df['result_timestamp'] = pd.to_datetime(df['result_timestamp'], format="%Y-%m-%d %H:%M:%S")
df['time'] = df['result_timestamp'].dt.time
df['date'] = df['result_timestamp'].dt.date

df_loc = df.query("description == 'MP 01: Naamsestraat 35  Maxim'")

df_temp = df_loc.groupby(by=["night_of_week", "time"]).mean('laeq').reset_index()
df_temp2 = df_loc.groupby(["count", "night_of_week"]).mean('laeq').reset_index()


fig = px.line_3d(df_temp, x="time", y="night_of_week", z= "laeq", color='night_of_week')
fig1 = px.violin(df_loc, y='laeq', title='Distribution of noise level',template="simple_white",
                 labels={
                     'laeq': 'Noise Level'
                 })
fig2 = px.line(df_temp2, x='count', y='laeq', color='night_of_week', title = 'think',template="simple_white",
               labels={
                     'laeq': 'Noise Level',
                     'count': 'Number of local establishments open',
                     'night_of_week': 'Night of the week'
                 },
                 category_orders={
                     'night_of_week': ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
                 })
fig3 = px.density_heatmap(df_loc, x='month',y='laeq', title='Frequency of noise levels per month',template="simple_white",
                          labels={
                     'laeq': 'Noise Level',
                     'month': 'Month'
                 })
fig4 = px.strip(df_loc, x='laeq',y='hour', title='Noise level for each hour',template="simple_white",
                labels={
                     'laeq': 'Noise Level'
                 })


dropdown = dcc.Dropdown(
    id='id_location_2',
    options=[
        {'label':'Naamsestraat 35', 'value':'MP 01: Naamsestraat 35  Maxim'},
        {'label':'Naamsestraat 57', 'value':'MP 02: Naamsestraat 57 Xior'},
        {'label':'Naamsestraat 62', 'value':'MP 03: Naamsestraat 62 Taste'},
        {'label':'His & Hears', 'value':'MP 04: His & Hears'},
        {'label':'Calvariekapel', 'value':'MP 05: Calvariekapel KU Leuven'},
        {'label':'Parkstraat 2', 'value':'MP 06: Parkstraat 2 La Filosovia'},
        {'label':'Naamsestraat 81', 'value':'MP 07: Naamsestraat 81'},
        {'label':'Vrijthof', 'value':'MP08bis - Vrijthof'},
    ],
    value="MP 01: Naamsestraat 35  Maxim",
    clearable=False,
    className="dropdown",
)

layout = dbc.Container(
    [
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(
                        [html.H4(children='Location:',className='header-description'),
                        dropdown]
                ),
                dbc.Col(
                        html.H4(children='...',id='id_title_2',style={
                            'text-align':'left',
                        }),
                        width=10,
                        
                ),
            ],
            align='center',
        ),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col([
                        dcc.Graph(id='id_graph_1',config={"displayModeBar": False},figure=fig1),
                            ],
                        width=6,
                        className='card',
                ),
                dbc.Col(
                        dcc.Graph(id='id_graph_2',config={"displayModeBar": False},figure=fig2),
                        width=6,
                        className='card',
                ),
             ],
             align = 'start',
        ),
        dbc.Row(
            [
                dbc.Col([
                        dcc.Graph(id='id_graph_3',config={"displayModeBar": False},figure=fig3),
                            ],
                        width=6,
                        className='card',
                ),
                dbc.Col(
                        dcc.Graph(id='id_graph_4',config={"displayModeBar": False},figure=fig4),
                        width=6,
                        className='card',
                ),
             ],
             align = 'start',
        ),
    ],
    fluid = True,
)


@callback(
    Output('id_title_2','children'),
    Output('id_graph_1','figure'),
    [Input('id_location_2','value'),
    ]
)
def update_graph1(location):
    filtered_data = df.query(
        'description == @location'
        )
    id_graph_figure = px.violin(filtered_data, y='laeq', title='Distribution of noise level',template="simple_white",
                                labels={
                     'laeq': 'Noise Level'
                 })

    id_graph_figure.update_traces()

    return 'Analysis for location: ' + location , id_graph_figure


@callback(
        Output('id_graph_2','figure'),
        [Input('id_location_2','value')
         ]
)
def update_graph2(location):
    filtered_data = df.query(
        'description == @location'
        )
    graph2_data = filtered_data.groupby(["count", "night_of_week"]).mean('laeq').reset_index()
    id_graph_figure_2 = px.line(graph2_data,  x='count', y='laeq', color='night_of_week',template="simple_white",
                                labels={
                     'laeq': 'Noise Level',
                     'count': 'Number of local establishments open',
                     'night_of_week': 'Night of the week'
                 })

    id_graph_figure_2.update_traces(mode="markers+lines")

    return id_graph_figure_2


@callback(
        Output('id_graph_3','figure'),
        [Input('id_location_2','value')
         ]
)
def update_graph3(location):
    filtered_data = df.query(
        'description == @location'
        )
    id_graph_figure_3 = px.density_heatmap(filtered_data, x='month', y='laeq', title='Frequency of noise levels per month',
                                           template="simple_white",
                                           labels={
                                                'laeq': 'Noise Level',
                                                'month': 'Month'
                                                })

    id_graph_figure_3.update_traces()

    return id_graph_figure_3


@callback(
        Output('id_graph_4','figure'),
        [Input('id_location_2','value')
         ]
)
def update_graph4(location):
    filtered_data = df.query(
        'description == @location'
        )
    id_graph_figure_4 = px.strip(filtered_data, x='laeq', y='hour', title='Noise level for each hour',template="simple_white",
                                 labels={
                     'laeq': 'Noise Level'
                 })

    id_graph_figure_4.update_traces()

    return id_graph_figure_4
