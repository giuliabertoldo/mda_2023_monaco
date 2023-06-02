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
import plotly.figure_factory as ff
import plotly.express as px
import plotly.io as pio

from data import df

dash.register_page(__name__)

pio.templates.default = "simple_white"

df['result_timestamp'] = pd.to_datetime(df['result_timestamp'], format="%Y-%m-%d %H:%M:%S")
df['time'] = df['result_timestamp'].dt.time
df['date'] = df['result_timestamp'].dt.date

df_loc = df.query("description == 'MP 01: Naamsestraat 35  Maxim'")

df_temp = df_loc.groupby(["count", "night_of_week"]).mean('laeq').reset_index()

df_night = df_loc.groupby(['night_of_week','month']).mean('laeq').reset_index()
df_night['night_of_week']=pd.Categorical(df_night['night_of_week'],['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
df_night = df_night.sort_values('night_of_week')

vals = df_loc['hour'].unique()
group_labels = []
for name in vals:
    group_labels.append('Hour ' + str(name))
    hist_data = []
for c in vals:
    ls = df_loc.loc[df_loc['hour']==c, 'laeq']
    hist_data.append(list(ls))

fig1 = px.line_polar(df_night,r='laeq',theta='night_of_week', color='month', title='Noise level per day for each month',
                     labels={
                         'month': 'Month'
                     }, line_close=True)

fig2 = px.line(df_temp, x='count', y='laeq', color='night_of_week', title = 'Noise level per number of bars open',
               labels={
                     'laeq': 'Noise Level',
                     'count': 'Number of local establishments open',
                     'night_of_week': 'Night of the week'
                 },
                 category_orders={
                     'night_of_week': ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
                 },)
fig3 = px.density_heatmap(df_loc, x='month',y='laeq', title='Frequency of noise levels per month',
                          labels={
                     'laeq': 'Noise Level',
                     'month': 'Month',
                 })
fig4 = ff.create_distplot(hist_data, group_labels, show_hist=False, show_curve=True, show_rug=False)
fig4.update_layout(title='Distribution of the noise level per hour')
fig4.update_xaxes(title='Noise level')
fig4.update_traces(hovertemplate=None, hoverinfo ='skip')


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
                        [html.H4(children='Location:',className='header-description2'),
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
    Output('id_graph_1','figure'),
    [Input('id_location_2','value'),
    ]
)
def update_graph1(location):
    filtered_data = df.query(
        'description == @location'
        )
    df_night_2 = filtered_data.groupby(['night_of_week','month']).mean('laeq').reset_index()
    df_night_2['night_of_week']=pd.Categorical(df_night_2['night_of_week'],['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'])
    df_night_2 = df_night_2.sort_values('night_of_week')

    id_graph_figure = px.line_polar(df_night_2,r='laeq',theta='night_of_week', color='month', title='Noise level per day for each month',
                                    labels={
                         'month': 'Month'
                     }, line_close=True)

    id_graph_figure.update_traces()

    return id_graph_figure


@callback(
        Output('id_title_2','children'),
        Output('id_graph_2','figure'),
        [Input('id_location_2','value')
         ]
)
def update_graph2(location):
    filtered_data = df.query(
        'description == @location'
        )
    graph2_data = filtered_data.groupby(["count", "night_of_week"]).mean('laeq').reset_index()
    id_graph_figure_2 = px.line(graph2_data,  x='count', y='laeq', color='night_of_week', 
                                title = 'Noise level per number of bars open',
                                category_orders={
                                    'night_of_week': ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
                                    },
                                labels={
                     'laeq': 'Noise Level',
                     'count': 'Number of local establishments open',
                     'night_of_week': 'Night of the week'
                 },)

    id_graph_figure_2.update_traces(mode="markers+lines")

    return 'Analysis for location: ' + location , id_graph_figure_2


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
                                           labels={
                                                'laeq': 'Noise Level',
                                                'month': 'Month',
                                                'count': 'Count'
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
    vals = filtered_data['hour'].unique()
    group_labels = []
    for name in vals:
        group_labels.append('Hour ' + str(name))
    hist_data_2 = []
    for c in vals:
        ls = filtered_data.loc[filtered_data['hour']==c, 'laeq']
        hist_data_2.append(list(ls))

    id_graph_figure_4 = ff.create_distplot(hist_data_2, group_labels, show_hist=False, show_curve=True, show_rug=False)
    id_graph_figure_4.update_layout(title='Distribution of the noise level per hour')
    id_graph_figure_4.update_xaxes(title='Noise level')
    id_graph_figure_4.update_traces(hovertemplate=None, hoverinfo ='skip')

    id_graph_figure_4.update_traces()

    return id_graph_figure_4
