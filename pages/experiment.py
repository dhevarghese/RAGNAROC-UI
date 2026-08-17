"""Experiment builder page: a guided four-step flow plus the results section.

Step 1 defines stimulus types, step 2 places visual objects on the canvas
(with a live preview), step 3 sets the simulation parameters, and step 4 names
and runs the experiment. Results appear below once a simulation finishes.
"""

from dash import dash_table, dcc, html
import dash_bootstrap_components as dbc

from pages.experiment_results import experimentResults

TABLE_STYLE = dict(
    row_deletable=True,
    style_as_list_view=True,
    editable=True,
    style_cell={'padding': '8px', 'backgroundColor': 'transparent', 'fontFamily': 'inherit'},
    style_header={
        'padding': '8px',
        'backgroundColor': 'rgba(0,0,0,0.25)',
        'color': '#aab0bc',
        'fontWeight': '600',
        'border': 'none',
        'textTransform': 'uppercase',
        'fontSize': '0.72rem',
        'letterSpacing': '0.06em',
    },
    style_data={'backgroundColor': 'transparent', 'color': 'white', 'border': '1px solid rgba(255,255,255,0.06)'},
    style_data_conditional=[
        {"if": {"state": "active"}, "backgroundColor": "rgba(252,205,97,0.12)", "border": "1px solid #fccd61", "color": "#fccd61"},
        {"if": {"state": "selected"}, "backgroundColor": "rgba(255,255,255,0.08)"},
    ],
)


def serve_layout(app):
    return html.Div(
        id="exp-page",
        children=[
            topBar(app),
            html.Div(id="garbage-output-0"),
            html.Div(
                className="exp-main",
                children=[
                    introCard(),
                    stepStimulusTypes(),
                    stepVisualObjects(),
                    stepSettingsAndRun(),
                ],
            ),
            experimentResults(),
            saveModal(),
            rewriteModal(),
            loadModal(),
            toasts(),
        ],
    )


def topBar(app):
    return html.Div(
        className="top-bar",
        children=[
            dcc.Link(
                className="top-bar-brand",
                href="/",
                children=[
                    html.Img(className="top-bar-logo", src=app.get_asset_url("logo.png")),
                    html.Span("Ragnaroc", className="top-bar-title"),
                ],
            ),
            html.Div(
                className="top-bar-actions",
                children=[
                    dbc.Button([html.I(className="fa-solid fa-folder-open me-2"), "Load"], id="load-sim", outline=True, color="light", size="sm"),
                    dbc.Button([html.I(className="fa-solid fa-floppy-disk me-2"), "Save"], id="save-exp", outline=True, color="light", size="sm"),
                ],
            ),
        ],
    )


def introCard():
    presets = [
        {"label": "Brisson — single relevant target", "value": "Brisson"},
        {"label": "Single — one lasting object", "value": "Single"},
        {"label": "Same — two objects, same place", "value": "Same"},
        {"label": "Diff — two objects, different places", "value": "Diff"},
        {"label": "MidTLateralD — target + distractor", "value": "MidTLateralD"},
        {"label": "EimerGrubert — two rapid targets", "value": "EimerGrubert"},
    ]
    return html.Div(
        className="step-card intro-card",
        children=[
            html.H1("Build an experiment", className="page-heading"),
            html.P(
                "RAGNAROC simulates how visual attention reacts to objects appearing in the visual field. "
                "Define what can appear (step 1), where and when it appears (step 2), then run the model to "
                "watch attention unfold across simulated brain maps and EEG.",
                className="page-lede",
            ),
            html.Div(
                className="preset-row",
                children=[
                    html.Div(
                        children=[
                            html.Label("Quick start with a preset", htmlFor="preset-experiment-choice", className="field-label"),
                            dcc.Dropdown(
                                options=presets,
                                value=None,
                                id="preset-experiment-choice",
                                placeholder="Choose a preset experiment…",
                            ),
                        ],
                        className="preset-picker",
                    ),
                    html.P(
                        "Pick a preset to fill every step with a ready-made experiment — or skip this and build your own below.",
                        id="preset-description",
                        className="field-help preset-description",
                    ),
                ],
            ),
        ],
    )


def stepHeader(number, title, subtitle):
    return html.Div(
        className="step-header",
        children=[
            html.Span(number, className="step-number"),
            html.Div([
                html.H2(title, className="step-title"),
                html.P(subtitle, className="step-subtitle"),
            ]),
        ],
    )


def stepStimulusTypes():
    return html.Div(
        className="step-card",
        children=[
            stepHeader(
                "1", "Define stimulus types",
                "A stimulus type is a kind of thing that can appear — a target, a distractor. Each has a "
                "bottom-up weight (how physically salient it is) and a top-down weight (how relevant it is "
                "to the task), both from 0 to 1.",
            ),
            html.Div(
                className="step-body two-col",
                children=[
                    html.Div(
                        className="form-col",
                        children=[
                            html.Label("Name", htmlFor="stim-type-name", className="field-label"),
                            dcc.Input(id="stim-type-name", className="text-field", placeholder='e.g. "target"', type='text', value=""),
                            html.Div(
                                className="weight-row",
                                children=[
                                    html.Label("Top-down weight (task relevance)", className="field-label"),
                                    dcc.Input(id="text-td-weight", className="text-field weight-field hideNumScroll", type='number', value=0.5, step=0.01, min=0, max=1),
                                ],
                            ),
                            dcc.Slider(0, 1, value=0.5, id="top-down", tooltip={"placement": "bottom"}, className="slider-margin"),
                            html.Div(
                                className="weight-row",
                                children=[
                                    html.Label("Bottom-up weight (salience)", className="field-label"),
                                    dcc.Input(id="text-bu-weight", className="text-field weight-field hideNumScroll", type='number', value=0.5, step=0.01, min=0, max=1),
                                ],
                            ),
                            dcc.Slider(0, 1, value=0.5, id="bottom-up", tooltip={"placement": "bottom"}, className="slider-margin"),
                            dbc.Button("Add stimulus type", id="add-stim-type", n_clicks=0, className="add-btn", color="warning"),
                        ],
                    ),
                    html.Div(
                        className="table-col",
                        children=[
                            html.P("Your stimulus types (click a cell to edit, × to remove):", className="field-help"),
                            dash_table.DataTable(
                                id='stim-types-table',
                                columns=[
                                    {'name': 'Name', 'id': 'stimName'},
                                    {'name': 'Top-down', 'id': 'td', 'type': 'numeric'},
                                    {'name': 'Bottom-up', 'id': 'bu', 'type': 'numeric'},
                                ],
                                data=[],
                                **TABLE_STYLE,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def stepVisualObjects():
    return html.Div(
        className="step-card",
        children=[
            stepHeader(
                "2", "Place visual objects",
                "A visual object is one appearance of a stimulus type on the canvas: it shows up at position "
                "(X, Y) after a delay (latency, ms) and stays visible for a while (duration, ms). The preview "
                "shows your current layout.",
            ),
            html.Div(
                className="step-body two-col",
                children=[
                    html.Div(
                        className="form-col",
                        children=[
                            html.Label("Name", htmlFor="vis-obj-name", className="field-label"),
                            dcc.Input(id="vis-obj-name", className="text-field", placeholder='e.g. "T1"', type='text', value=""),
                            html.Div(
                                className="field-grid",
                                children=[
                                    html.Div([
                                        html.Label("X", htmlFor="vis-obj-x", className="field-label"),
                                        dcc.Input(id="vis-obj-x", className="text-field hideNumScroll", type='number', min=1, max=27, value=None),
                                        dbc.Tooltip("Range: (1,27) ", target="vis-obj-x", id="vis-obj-x-tooltip", placement="top"),
                                    ]),
                                    html.Div([
                                        html.Label("Y", htmlFor="vis-obj-y", className="field-label"),
                                        dcc.Input(id="vis-obj-y", className="text-field hideNumScroll", type='number', min=1, max=27, value=None),
                                        dbc.Tooltip("Range: (1,27) ", target="vis-obj-y", id="vis-obj-y-tooltip", placement="top"),
                                    ]),
                                    html.Div([
                                        html.Label("Latency (ms)", htmlFor="vis-obj-latency", className="field-label"),
                                        dcc.Input(id="vis-obj-latency", className="text-field hideNumScroll", type='number', min=0, max=1000, value=None),
                                    ]),
                                    html.Div([
                                        html.Label("Duration (ms)", htmlFor="vis-obj-duration", className="field-label"),
                                        dcc.Input(id="vis-obj-duration", className="text-field hideNumScroll", type='number', min=0, max=1000, value=None),
                                    ]),
                                ],
                            ),
                            html.Label("Stimulus type", htmlFor="vis-obj-stim-type", className="field-label"),
                            dcc.Dropdown(options=[], value='', id="vis-obj-stim-type", placeholder="Pick from step 1…"),
                            dbc.Button("Add visual object", id="vis-obj-add", n_clicks=0, className="add-btn", color="warning"),
                        ],
                    ),
                    html.Div(
                        className="table-col",
                        children=[
                            dcc.Graph(
                                id="canvas-preview",
                                config={"displayModeBar": False},
                                className="canvas-preview",
                            ),
                            dash_table.DataTable(
                                id='vis-objs-table',
                                columns=[
                                    {'name': 'Name', 'id': 'name'},
                                    {'name': 'X', 'id': 'X'},
                                    {'name': 'Y', 'id': 'Y'},
                                    {'name': 'Duration', 'id': 'duration'},
                                    {'name': 'Latency', 'id': 'latency'},
                                    {'name': 'Stimulus', 'id': 'stimulus'},
                                ],
                                data=[],
                                **TABLE_STYLE,
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def stepSettingsAndRun():
    return html.Div(
        className="step-card",
        children=[
            stepHeader(
                "3", "Configure and run",
                "Set how long and on how big a canvas the simulation runs, give the experiment a name, and hit Run. "
                "Results appear below when it finishes — usually within a few seconds.",
            ),
            html.Div(
                className="step-body settings-row",
                children=[
                    html.Div([
                        html.Label("Runtime (ms)", htmlFor="exp-total-time", className="field-label"),
                        dcc.Input(id="exp-total-time", className="text-field hideNumScroll", type='number', min=1, value=600),
                        html.P("How many milliseconds to simulate.", className="field-help"),
                    ]),
                    html.Div([
                        html.Label("Canvas size", htmlFor="canvas-size", className="field-label"),
                        dcc.Input(id="canvas-size", className="text-field hideNumScroll", type='number', min=1, max=50, value=27),
                        html.P("The visual field is an N×N grid (1–50).", className="field-help"),
                    ]),
                    html.Div([
                        html.Label("Mask size", htmlFor="mask-size", className="field-label"),
                        dcc.Input(id="mask-size", className="text-field hideNumScroll", type='number', min=1, max=10, value=3),
                        html.P("Neighborhood used for lateral interactions (1–10).", className="field-help"),
                    ]),
                ],
            ),
            html.Div(
                className="run-row",
                children=[
                    html.Div(
                        className="run-name",
                        children=[
                            html.Label("Experiment name", htmlFor="exp-name", className="field-label"),
                            dcc.Input(id="exp-name", className="text-field", placeholder='e.g. "my first trial"', type='text', value=""),
                        ],
                    ),
                    dcc.Loading(
                        children=[
                            dcc.Store(id='sim-store'),
                            dcc.Store(id='original-store'),
                            dbc.Button(
                                [html.I(className="fa-solid fa-bolt me-2"), "Run simulation"],
                                id="run-sim", n_clicks=0, color="warning", size="lg", className="run-btn",
                            ),
                        ],
                        type="circle",
                        color="#fccd61",
                        parent_className="run-loading",
                    ),
                ],
            ),
        ],
    )


def saveModal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Save experiment"), className="sl-modal-header"),
            dbc.ModalBody(
                children=[
                    html.P("Whose experiment is this? Saved experiments are grouped by creator name so you can load them back later."),
                    dcc.Input(id="exp-creator-name", className="text-field", placeholder='Your name', type='text', value=""),
                    dbc.Button("Save", id="save-creator-exp", n_clicks=0, className="sl-button"),
                ],
                className="sl-modal-body",
            ),
        ],
        id="creator-modal",
        centered=True,
        is_open=False,
    )


def rewriteModal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Overwrite experiment?"), className="sl-modal-header"),
            dbc.ModalBody(
                children=[
                    html.P("An experiment with this name already exists under your name. Overwrite it?"),
                    html.Div(
                        children=[
                            dbc.Button("Overwrite", id="rewrite-accept", n_clicks=0, className="sl-button me-2"),
                            dbc.Button("Cancel", id="rewrite-deny", n_clicks=0, className="sl-button"),
                        ],
                    ),
                ],
                className="sl-modal-body",
            ),
        ],
        id="rewrite-modal",
        centered=True,
        is_open=False,
    )


def loadModal():
    return dbc.Modal(
        [
            dbc.ModalHeader(dbc.ModalTitle("Load experiment"), className="sl-modal-header"),
            dbc.ModalBody(
                children=[
                    html.P("Enter the creator name the experiment was saved under, then pick it from the list."),
                    dcc.Input(id="load-exps-creator", className="text-field", placeholder='Creator name', type='text', value="", debounce=True),
                    dcc.Dropdown(options=[], value=None, id='loaded-exps-dropdown', placeholder="Saved experiments…", className="load-dropdown"),
                    dbc.Button("Load", id="load-creator-exp", n_clicks=0, className="sl-button"),
                ],
                className="sl-modal-body",
            ),
        ],
        id="load-exp-modal",
        centered=True,
        is_open=False,
    )


def toasts():
    common = dict(is_open=False, fade=True, duration=4000)
    return html.Div(
        className="toast-stack",
        children=[
            dbc.Alert("Experiment saved.", id="save-alert", color="success", **common),
            dbc.Alert("Please enter valid inputs for stimulus type", id="stim-alert", color="danger", **common),
            dbc.Alert("Duplicate stimulus names are not allowed", id="stim-dup-alert", color="warning", **common),
            dbc.Alert("Please enter valid inputs for visual object", id="vo-alert", color="danger", **common),
            dbc.Alert("Duplicate visual object names are not allowed", id="vo-dup-alert", color="warning", **common),
            dbc.Alert("", id="run-sim-alert", color="danger", **common),
            dbc.Alert("Could not load that experiment.", id="load-alert", color="danger", **common),
        ],
    )
