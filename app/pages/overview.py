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

dash.register_page(__name__,path='/')

df.result_timestamp = pd.to_datetime(df.result_timestamp)
months = df.month.sort_values().unique()
locations = df.description.sort_values().unique()


fig = px.line(data_frame=df['laeq'].groupby([df.result_timestamp.dt.dayofyear,df.description]).mean().reset_index(),
             x='result_timestamp',
             y='laeq',
             color='description',
             template="simple_white",
             labels={'result_timestamp':'Day of year',
                     'laeq':'Mean level of noise',
                     'description':'Location'},
            )

px.set_mapbox_access_token("pk.eyJ1IjoiYmVydG9sZG9naXVsaWEiLCJhIjoiY2xoZ2FzdXF3MXluYTNmcGNtdWZjbGFwcSJ9.0nLVkEGkQwV5j_QOBfsQeQ")
df['time'] = df['result_timestamp'].dt.time
map = px.scatter_mapbox(df,
              lat="lat" ,
              lon="lon",
              animation_frame= "time",
              mapbox_style='carto-positron',
              size = "laeq",
              color = "laeq",
              color_continuous_scale=px.colors.cyclical.Twilight,  
              hover_data = ['time', "description"], 
              size_max = 10,      
              labels={
                  "laeq": "Mean noise level"
              },         
              zoom=14)


date_range = dcc.DatePickerRange(
    id = 'id_date_range',
    min_date_allowed=datetime.datetime(2022,1,1),
    max_date_allowed=datetime.datetime(2022,12,31),
    start_date=datetime.datetime(2022,1,1),
    end_date=datetime.datetime(2022,12,31),
    display_format='DD MM YYYY',
)


dropdown = dcc.Dropdown(
    id='id_location',
    options=[
        {'label':'All', 'value':'All'},
        {'label':'Naamsestraat 35', 'value':'MP 01: Naamsestraat 35  Maxim'},
        {'label':'Naamsestraat 57', 'value':'MP 02: Naamsestraat 57 Xior'},
        {'label':'Naamsestraat 62', 'value':'MP 03: Naamsestraat 62 Taste'},
        {'label':'His & Hears', 'value':'MP 04: His & Hears'},
        {'label':'Calvariekapel', 'value':'MP 05: Calvariekapel KU Leuven'},
        {'label':'Parkstraat 2', 'value':'MP 06: Parkstraat 2 La Filosovia'},
        {'label':'Naamsestraat 81', 'value':'MP 07: Naamsestraat 81'},
        {'label':'Vrijthof', 'value':'MP08bis - Vrijthof'},
    ],
    value="All",
    clearable=False,
    className="dropdown",
)


layout = dbc.Container(
    [
        html.Hr(),
        dbc.Row(
            [
            dbc.Col(dbc.Stack([html.H4(children='Location:', className='header-description2'),
                    dropdown,
                    html.H4(children='Time period:', className='header-description2'),
                    date_range]), 
                    width=2),
            dbc.Col(dbc.Stack([html.H4(children='...',id='id_title',className='header-description2'),
                               html.Div(children=dcc.Graph(id="id_graph",config={"displayModeBar": False},figure=fig),
                            className='card'),
                            html.H4(children='Noise level during night-time across all days of the year', className='header-description2'),
                            html.Div(children=dcc.Graph(id="id_map",config={"displayModeBar": False},figure=map),
                                     className='card')],
                        ),
                width=10,
                ),
             ],
             align = 'start',
        ),
    ],
    fluid = True    
)


@callback(
    Output('id_title','children'),
    Output('id_graph','figure'),
    [Input('id_location','value'),
     Input('id_date_range','start_date'),
     Input('id_date_range','end_date')
    ]
)
def updated_chart(location, start_date, end_date):
    try:
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
    except:
        id_graph_figure = px.line(data_frame=df.groupby([df.result_timestamp.dt.day_of_year,
                                                                df.description]).mean('laeq').reset_index(),
                x='result_timestamp',
                y='laeq',
                color='description',
                template="simple_white",
                labels={'result_timestamp':'Day of year',
                        'laeq':'Mean level of noise'},
                )



    if location != 'All':
        filtered_data = df.query(
            'description == @location'
        )
    else:
        filtered_data = df
    
    filtered_data = filtered_data[(filtered_data['result_timestamp'] >= start_date)]
    filtered_data = filtered_data[(filtered_data['result_timestamp'] <= end_date)]

    id_graph_figure = px.line(data_frame=filtered_data.
                              groupby([filtered_data.result_timestamp.dt.day_of_year,
                                    filtered_data.description]).mean(['laeq','lc_dwptemp']).reset_index(),
            x='result_timestamp',
            y='laeq',
            color='description',
            template="simple_white",
            labels={'result_timestamp':'Day of year',
                    'laeq':'Mean level of noise',
                    'lc_dwptemp': 'Average temperature',
                    'description':'Location'},
            hover_data={'result_timestamp': True,
                        'description': False,
                        'laeq': False,
                        'lc_dwptemp': True,
                        }
            )
    id_graph_figure.update_traces(mode="markers+lines")
    
    
    
    return 'Average daily noise level between: ' + start_date.strftime('%d-%m-%Y') + ' -> ' + end_date.strftime('%d-%m-%Y'), id_graph_figure
  