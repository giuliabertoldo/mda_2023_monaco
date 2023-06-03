import pandas as pd
import dash
from dash import html
from dash import dcc, callback

import numpy as np
import datetime
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px
import pickle

from data import df


dash.register_page(__name__)


df_pred = pd.DataFrame()
df_pred[['description', 'day_of_week', 'night_of_week', 'month', 'hour', 'lc_dwptemp','lc_windspeed', 'lc_rainin',
          'lc_dailyrain', 'count']] = [['MP 01: Naamsestraat 35  Maxim','Monday','Monday',1,1,10,2,0.015,0.025,3]]

model = pd.read_pickle('s3://mda.project.monaco/new_model_2.pkl')
pred = model.predict(df_pred)


clf = model.best_estimator_[-1]
feat_imp = list(zip(clf.feature_names_in_, clf.feature_importances_))
df_importances = pd.DataFrame(feat_imp, columns=['Feature', 'Importance']).sort_values(by='Importance', ascending=False)
df_imp = df_importances.groupby('Feature').sum('Importance').sort_values(by='Importance', ascending=False).reset_index()
df_imp = df_imp.iloc[:15]
fig = px.bar(df_imp, y='Feature', x='Importance', orientation='h', template="simple_white", height=375)


location_drop = dcc.Dropdown(
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

night_drop = dcc.Dropdown(
    id='id_night',
    options=[
        {'label':'Monday', 'value':'Monday'},
        {'label':'Tuesday', 'value':'Tuesday'},
        {'label':'Wednesday', 'value':'Wednesday'},
        {'label':'Thursday', 'value':'Thursday'},
        {'label':'Friday', 'value':'Friday'},
        {'label':'Saturday', 'value':'Saturday'},
        {'label':'Sunday', 'value':'Sunday'},
    ],
    value="Monday",
    clearable=False,
    className="dropdown",
)

day_drop = dcc.Dropdown(
    id='id_day',
    options=[
        {'label':'Monday', 'value':'Monday'},
        {'label':'Tuesday', 'value':'Tuesday'},
        {'label':'Wednesday', 'value':'Wednesday'},
        {'label':'Thursday', 'value':'Thursday'},
        {'label':'Friday', 'value':'Friday'},
        {'label':'Saturday', 'value':'Saturday'},
        {'label':'Sunday', 'value':'Sunday'},
    ],
    value="Monday",
    clearable=False,
    className="dropdown",
)

numeric = html.Div([
    dbc.InputGroup([
        dbc.Input(id='id_month',value=1,type='number', min=1, max=12, step=1)]),
    dbc.InputGroup([
        dbc.Input(id='id_hour',value=1,type='number', min=0, max=24, step=1)]),
    dbc.InputGroup([
        dbc.Input(id='id_temp',value=10,type='number', min=-20, max=30)]),
    dbc.InputGroup([
        dbc.Input(id='id_wind',value=2,type='number', min=0, max=5)]),
    dbc.InputGroup([
        dbc.Input(id='id_lc_rainin',value=0.015,type='number', min=0, max=0.03)]),
    dbc.InputGroup([
        dbc.Input(id='id_daily_rain',value=0.025,type='number', min=0, max=0.05)]),
    dbc.InputGroup([
        dbc.Input(id='id_count',value=3,type='number', min=0, max=14, step=1)]),
],
)


layout = dbc.Container(
    [   
        html.Hr(),
        html.H5(children="We have built a model that aims to predict the noise level given a range of features, including the month,\
                 day of the week and temperature. We found the a random forest model performed the best, with an R2 score of 0.868, \
                 a median absolute error of 1.23 and a negative RMSE of -2.47.\
                Below, you can see our model's predicted noise level based on the feature values that you specify.",
                ),
        html.Hr(),
        dbc.Row(
            [
            dbc.Col(
                dbc.Stack([html.H4(children='Location:',className='header-description2'),
                    html.H4(children='Day of the week:',className='header-description2'),
                    html.H4(children='Night of the week:',className='header-description2'),
                    html.H4(children='Month:',className='header-description2'),
                    html.H4(children='Hour:',className='header-description2'),
                    html.H4(children='Temperature:',className='header-description2'),
                    html.H4(children='Wind speed:',className='header-description2'),
                    html.H4(children='Lc_rain',className='header-description2'),
                    html.H4(children='Daily rain:',className='header-description2'),
                    html.H4(children='No. bars open:',className='header-description2'),
                    
                    ],
                    ), 
                    width=3,
                    align='start',
            ),
            dbc.Col(
                [
                dbc.Stack([
                    location_drop,
                    night_drop,
                    day_drop,
                    numeric,
                ],
                ),
                ],
                width=2,
                align='start',
            ),
            dbc.Col(
                dbc.Stack([
                    html.Div(dcc.Graph(config={"displayModeBar": False},figure=fig),className='card')
                    ],
                    ),
            ),
            ],
        ),
        dbc.Row(
            [
            dbc.Col(
                dbc.Stack([
                    html.H5(children='Based on the feature values that have been specified, \
                            our model predicts the following value for the noise level:'),
                    html.H5(children='...',id='id_text', style={
                        'font-weight': 'bold',
                        }),
                    ],
                    ),
                    width = 5,
            ),
            dbc.Col(
                html.H5(children='Above we see a representation of the 15 most important features\
                         as determined by our model')
            )
            ]
        )
    ],
    fluid=True,
)

@callback(
    Output('id_text','children'),
    [
        Input('id_location_2','value'),
        Input('id_night','value'),
        Input('id_day','value'),
        Input('id_month','value'),
        Input('id_hour','value'),
        Input('id_temp','value'),
        Input('id_wind','value'),
        Input('id_lc_rainin','value'),
        Input('id_daily_rain','value'),
        Input('id_count','value'),
    ]
)
def update_prediction(location,night,day,month,hour,temp,wind,lc_rain,daily_rain,count):
    df_pred_new = pd.DataFrame()
    df_pred_new[['description', 'day_of_week', 'night_of_week', 'month', 'hour', 'lc_dwptemp','lc_windspeed', 'lc_rainin',
          'lc_dailyrain', 'count']] = [[location,day,night,month,hour,temp,wind,lc_rain,daily_rain,count]]
    
    pred_new = model.predict(df_pred_new)
    pred_new = str(pred_new[0])[:6]

    return  pred_new
