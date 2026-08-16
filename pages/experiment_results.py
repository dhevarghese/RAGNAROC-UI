"""Results section: 3-D surface plot of a brain map over time + per-location line plots."""

from dash import dcc, html
import plotly.graph_objects as go
import dash_bootstrap_components as dbc


def experimentResults():
    return html.Div(
        id="results-visual",
        style={"display": "none"},
        children=[
            html.Div(
                className="results-header",
                children=[
                    html.H2("Results", className="results-title"),
                    html.Button([html.I(className="fa-regular fa-circle-question me-2"), "How do I read this?"], id="result-info", className="results-help-btn"),
                ],
            ),
            html.P(
                "The surface shows the selected brain map's activation across the canvas at one moment in time — "
                "press play or drag the slider to move through the simulation. Click anywhere on the surface to see "
                "that location's full time course in the line plots on the right.",
                className="results-lede",
            ),
            resultsHelpModal(),
            resultsOptions(),
            resultsGraphs(),
        ],
    )


def resultsHelpModal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Reading the results"), className="sl-modal-header"),
            dbc.ModalBody(
                children=[
                    html.P("The model simulates several interacting brain maps. Early Visual (EV) and Late Visual (LV) "
                           "carry the stimulus signal, the Attention Map (AM) is where attention forms, and the "
                           "Inhibitory Gate (IG) and Inhibitory Interneurons (II) shape and constrain it."),
                    html.P("The surface plot shows one map's activation over the whole canvas at the slider's time "
                           "point. Values are normalized to (0, 256). The AM and IG maps are shared across stimuli; "
                           "EV, LV and II are per-stimulus, so the stimulus selector applies to those."),
                    html.P("Clicking a location on the surface updates the line plots: each row is one map's "
                           "activation at that location over the full runtime. The top row is the simulated EEG "
                           "(N2pc component). The time marker draws a dashed line at a chosen millisecond."),
                ],
                className="sl-modal-body results-modal-body",
            ),
        ],
        id="result-modal",
        centered=True,
        is_open=False,
    )


def resultsOptions():
    return html.Div(
        className="results-options",
        children=[
            html.Div(
                className="results-option",
                children=[
                    html.Label("Brain map", className="field-label"),
                    dcc.Dropdown(
                        options=[
                            {'label': 'Attention Map (AM)', 'value': 'AM'},
                            {'label': 'Inhibitory Gate (IG)', 'value': 'IG'},
                            {'label': 'Inhibitory Interneuron (II)', 'value': 'II'},
                            {'label': 'Late Visual (LV)', 'value': 'LV'},
                            {'label': 'Early Visual (EV)', 'value': 'EV'},
                        ],
                        value='IG',
                        id="map-dropdown",
                        clearable=False,
                        searchable=False,
                    ),
                ],
            ),
            html.Div(
                className="results-option",
                children=[
                    html.Label("Stimulus type (for EV / LV / II)", className="field-label"),
                    dcc.Dropdown(options=[], value='', id='stim-type-dropdown', clearable=False, searchable=False),
                ],
            ),
            html.Div(
                className="results-option",
                children=[
                    html.Label("Time marker (ms)", className="field-label"),
                    dbc.Input(id="lineplot-time", placeholder="e.g. 250", type="number", min=0, debounce=True, className="hideNumScroll"),
                ],
            ),
        ],
    )


def resultsGraphs():
    return html.Div(
        className="results-graphs",
        children=[
            dcc.Loading(
                [
                    dcc.Graph(
                        id="surface-viz",
                        figure={"layout": go.Layout(width=700, height=600, margin=dict(r=35, l=35, b=30, t=30), template="plotly_dark")},
                    ),
                ],
                type="circle",
                color="#fccd61",
            ),
            dcc.Loading(
                [
                    dcc.Graph(
                        id="line-viz",
                        figure={"layout": go.Layout(width=700, height=600, margin=dict(r=35, l=35, b=30, t=30), template="plotly_dark")},
                    ),
                ],
                type="circle",
                color="#fccd61",
            ),
        ],
    )
