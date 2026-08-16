"""Page routing for the multi-page app."""

from dash_extensions.enrich import Input, Output

from pages import experiment, index


def register(app):
    @app.callback(Output('page-content', 'children'),
                  Input('url', 'pathname'))
    def display_page(pathname):
        if pathname == '/':
            return index.serve_layout(app)
        elif pathname == '/ragnaroc':
            return experiment.serve_layout(app)
        else:
            return '404'
