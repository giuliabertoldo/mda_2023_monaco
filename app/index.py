import dash
import dash_bootstrap_components as dbc
from dash import html, dcc
from dash.dependencies import Input, Output

from app import app
from pages import page1, page2, home

navbar = dbc.NavbarSimple(
    children=[
        dbc.NavItem(dbc.NavLink('Home',href='/pages/home')),
        dbc.DropdownMenu(
            children=[
                dbc.DropdownMenuItem(
                    'First Page', href='/pages/page1'),
                dbc.DropdownMenuItem(
                    'Second Page',href='/pages/page2'
                ),
            ],
            nav=True,
            in_navbar=True,
            label='Pages',
        ),
    ],
    brand='Navigation Bar',
    brand_href='/pages/home',
    style={"margin-bottom": 5},
    color="primary",
    dark=True,
)


app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    navbar,
    html.Div(id='page-content', children=[])
])

default_template = home.layout

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/pages/page1':
        return page1.layout
    elif pathname == '/pages/page2':
        return page2.layout
    elif pathname == '/apps/home':
        return home.layout
    else:
        return default_template
    
if __name__ == '__main__':
    app.run_server(debug=False)




