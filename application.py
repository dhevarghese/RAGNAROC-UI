"""RAGNAROC-UI entry point.

Creates the Dash app, sets the routing shell, and registers all callbacks.
The callbacks live in the callbacks/ package, split by functional area; the
page layouts live in pages/.

    AUTHOR: DHEERAJ V
"""

import os

import dash_bootstrap_components as dbc
from dash import dcc, html
from dash_extensions.enrich import Dash

import callbacks

external_stylesheets = [
    dbc.themes.BOOTSTRAP,
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css',
]

app = Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=external_stylesheets,
    prevent_initial_callbacks=True,
    update_title=None,
    assets_folder="static",
    assets_url_path="static",
)
app.title = 'Ragnaroc'
application = app.server

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content'),
])

callbacks.register_all(app)

if __name__ == '__main__':
    debug = os.getenv("RAGNAROC_DEBUG", "").lower() in ("1", "true", "yes")
    app.run(debug=debug, port=int(os.getenv("PORT", "8050")))
