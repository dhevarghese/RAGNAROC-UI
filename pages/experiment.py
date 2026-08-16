from dash import dcc, html
import dash_bootstrap_components as dbc

from pages.experiment_sidebar import  *
from pages.experiment_results import  *

def serve_layout(app):
    return html.Div(
        children=[
            html.Div(
                id="root",
                children=[
                    mainBody(app),
                    sideBar(),
                ],
            ),
            experimentResults(),
        ],
    )

def mainBody(app):
    return html.Div(
        id="app-container",
        children=[
            # Banner display
            html.Div(
                id="top-bar",
                children= banner(app),
                style={
                    "display":"flex",
                    "justify-content":"space-between",
                }
            ),
            html.Div(
                id="experiment-settings",
                children= experimentForms(),
            ),
            html.Div(id="garbage-output-0"),
            html.Div(
                [
                    dcc.Loading(
                        [
                            dcc.Store(id='sim-store'),
                            dcc.Store(id='original-store'),
                            saveModal(),
                            rewriteModal(),
                            loadModal(),
                            simulationOperationButtons(),
                        ],
                        type="circle",
                        color="#fccd61",
                        style={"marginTop":"1rem", "marginLeft":"1rem"},
                    ),
                ],
            ),
            html.Div(
                children= alerts(),
                style={"marginTop":"1.5rem"}
            ),
        ],
    )

def banner(app):
    return [
        html.Div(
            id="banner",
            children=[
                html.Img(
                    id="logo", src=app.get_asset_url("logo.png")
                ),
                html.H2("Ragnaroc", id="title", style={"font-family":"Norse", "marginTop":"1rem",}),
            ],
        ),
        html.Div(
            [
                html.P("Run time", style={"display":"contents", "color":"white"}),
                dcc.Input(
                    id="exp-total-time",
                    className="form-name-input",
                    placeholder='ms',
                    type='number',
                    value='',
                    style= {"width":"30%", "text-align": "center"}
                ),
            ],
            style={
                "alignSelf":"center",
                "text-align":"end",
            }
        ),
    ]

def experimentForms():
    return html.Div(
        id="experiment-forms",
        children=[
            html.Div(
                [
                    html.H1('Experiment ', style={"display": "inline", }),
                    dcc.Input(
                        id="exp-name",
                        className="bottom-white-outline-input",
                        placeholder='Name',
                        type='text',
                    ),
                ],
                className="exp-header",
            ),
            
            html.Div(
                className="tabs-div",
                children=[
                    dcc.Tabs(
                        id="exp-form-tabs",
                        value="stim-form",
                        children=[
                            dcc.Tab(
                                label='Stimulus Types', 
                                value="stim-form",
                                children=stim_type_form(),
                                className='custom-tab-2',
                                selected_className='custom-tab-2--selected',
                            ),
                            dcc.Tab(
                                label='Visual Objects', 
                                value="vo-form",
                                children=visual_objects_form(),
                                className='custom-tab-2',
                                selected_className='custom-tab-2--selected',
                            ),
                        ],
                        style={"margin":"2rem",}
                    ),
                ],
            ),
        ],
    )

def stim_type_form():
    return html.Div(
        className="form-spacing",
        children=[
            html.P("Stimulus",style={"display":"inline"}),
            dcc.Input(
                id="stim-type-name",
                className="form-name-input",
                placeholder='Name',
                type='text',
                value='',
            ),

            html.Div(children=[
                html.Div(
                    children=[
                        html.P("Top-Down Weight", style={"margin": "1.5rem 0rem" }),
                        dcc.Input(
                            id="text-td-weight",
                            className="hideNumScroll weight-texts",
                            type='number', value=0.5, step=0.01, min=0, max=1,
                        ),
                    ],
                    className="stim-form-weights-div",
                ),
                dcc.Slider(0,1,value=0.5, id="top-down", tooltip={"placement": "bottom", }, className="slider-margin"),
                
                html.Div(
                    children=[
                        html.P("Bottom-Up Weight", style={"margin": "1.5rem 0rem"}),
                        dcc.Input(
                            id="text-bu-weight",
                            className="hideNumScroll weight-texts",
                            type='number', value=0.5, step=0.01, min=0, max=1,
                        ),
                    ],
                    className="stim-form-weights-div",
                ),
                dcc.Slider(0,1,value=0.5, id="bottom-up", tooltip={"placement": "bottom", }, className="slider-margin"),
                
                html.Button(
                    html.I(className="fas fa-solid fa-plus"),
                    id="add-stim-type",
                    className="form-add-btn",
                    form="stim-type-form",
                    n_clicks=0,
                    style={"marginTop": "20px",}
                ),
            ], style={"margin": "0rem 1rem 0.5rem"}
            ), 
        ]
    )

def visual_objects_form():
    return html.Div(
        className="form-spacing",
        children=[
            html.P("Visual Objects",style={"display":"inline"}),
            dcc.Input(
                id="vis-obj-name",
                className="form-name-input",
                placeholder='Name',
                type='text',
                value='',
            ),

            html.Div(children=[
                html.Div(children=[
                    html.P("X", 
                        style={
                                "paddingTop":"16px", 
                                "paddingRight":"44px", 
                                "paddingLeft":"28px" 
                            }
                        ),
                    dcc.Input(
                        id="vis-obj-x",
                        placeholder="Coordinate",
                        type='number', min=1, max=27,
                        className="hideNumScroll vis-obj-form-input",
                    ),
                    dbc.Tooltip(
                        "Range: (1,27) ",
                        target="vis-obj-x",
                        id="vis-obj-x-tooltip",
                        placement="top",
                    ),

                    html.P("Y", style={"paddingTop":"16px", "paddingRight":"36px", "paddingLeft":"72px"}),
                    dcc.Input(
                        id="vis-obj-y",
                        placeholder="Coordinate",
                        type='number', min=1, max=27,
                        className="hideNumScroll  vis-obj-form-input",
                    ),
                    dbc.Tooltip(
                        "Range: (1,27) ",
                        target="vis-obj-y",
                        id="vis-obj-y-tooltip",
                        placement="top",
                    ),
                ], style={"display":"flex", "marginBottom":"2rem", "marginTop":"2rem", "justifyContent":"space-around"}),

                html.Div(children=[
                    html.P("Duration", style={"paddingTop":"16px", "paddingRight":"12px" }),
                    dcc.Input(
                        id="vis-obj-duration",
                        placeholder="in milli-seconds",
                        type='number', min=0, max=1000,
                        className="hideNumScroll  vis-obj-form-input",
                    ),
                    dbc.Tooltip(
                        "Maximum: 1000 ms ",
                        target="vis-obj-duration",
                        placement="bottom",
                    ),

                    html.P("Latency", style={"paddingTop":"16px", "paddingRight":"12px", "paddingLeft":"48px"}),
                    dcc.Input(
                        id="vis-obj-latency",
                        placeholder="in milli-seconds",
                        type='number',
                        min=0, max=1000,
                        className="hideNumScroll vis-obj-form-input",
                    ),
                    dbc.Tooltip(
                        "Maximum: 1000 ms ",
                        target="vis-obj-latency",
                        placement="bottom",
                    ),
                ], style={"display":"flex", "justifyContent":"space-around", "marginBottom":"2rem", "marginTop":"2rem"}),
                
                html.Div(
                    children=[
                        html.P("Stimulus type", 
                            style={"width":"50%", "textAlign": "center"}
                        ),
                        html.Div(
                            dcc.Dropdown(options=[], value='', id="vis-obj-stim-type",), 
                            style={"width":"35%",}
                        ),
                    ],
                    style={
                        "display":"flex",
                        "margin":"2.6rem 1rem 1.6rem",
                    }
                ),
                
                html.Button(
                    html.I(className="fas fa-solid fa-plus"),
                    id="vis-obj-add",
                    className="form-add-btn",
                    n_clicks=0,
                    style={"marginTop": "1.625rem",}
                    ),
            ], style={"margin": "1rem 1rem 0.5rem",}
            ), 
        ]
    )

def saveModal():
    return dbc.Modal(
        [
            dbc.ModalHeader( dbc.ModalTitle("But, who are you?"), className="sl-modal-header",),
            dbc.ModalBody(
                className="sl-modal-body",
                children=[
                    html.P("Let us know your code name, experimenter."),
                    dcc.Input(
                        id="exp-creator-name",
                        placeholder='Thor',
                        type='text',
                    ),          
                    html.P("Note: This name may not be unique. This place attracts experimenters..."),
                    html.Div(
                        [
                            dbc.Button(
                                children = ["Save"],
                                id="save-creator-exp",
                                className="sl-button",
                                color="warning",
                            ),
                        ],
                        className="d-grid gap-2 col-3 mx-auto",
                    ),
                ], 
            ),
        ],
        id="creator-modal",
        centered=True,
        is_open=False,
    )

def rewriteModal():
    return dbc.Modal(
        [
            dbc.ModalHeader( dbc.ModalTitle("But, who are you?"), className="sl-modal-header",),
            dbc.ModalBody(
                className="sl-modal-body",
                children=[
                    html.P("This experiment name already exists in our records, in your name. Would you like to overwrite the setup?"),
                    html.Div(
                        [
                            dbc.Button(
                                children = ["Yes"],
                                id="rewrite-accept",
                                className="sl-button",
                                color="warning",
                            ),
                            dbc.Button(
                                children = ["No"],
                                id="rewrite-deny",
                                className="sl-button",
                                color="warning",
                            ),
                        ],
                        className="d-grid gap-2 col-3 mx-auto",
                    ),
                ], 
            ),
        ],
        id="rewrite-modal",
        centered=True,
        is_open=False,
    )

def loadModal():
    return dbc.Modal(
        [
            dbc.ModalHeader( dbc.ModalTitle("Do I remember you?"), className="sl-modal-header",),
            dbc.ModalBody(
                className="sl-modal-body",
                children=[
                    html.Div(
                        children=[
                            html.P("Creator name:"),
                            dcc.Input(
                                id="load-exps-creator",
                                className="bottom-white-outline-input",
                                placeholder='Thor',
                                type='text',
                                debounce=True,
                                style={ "marginLeft" : "3rem", "borderTop" : "none",}
                            ),        
                        ],
                        style = {"display" : "flex", "marginTop" : "1rem", "marginBottom" : "2rem",}
                    ),
                    
                    html.Div(
                        children = [
                            html.P("Select experiment: "), 
                            html.Div(
                                children=[
                                    dcc.Dropdown(
                                        [], 
                                        id='loaded-exps-dropdown',
                                    ),
                                ],
                                style={ "width" : "45%", "marginLeft" : "1rem",}
                            ),
                            
                        ],
                        style={ "display":"flex", "marginTop" : "1rem",},
                    ),
                    html.Div(
                        [
                            dbc.Button(
                                children = ["Load"],
                                id="load-creator-exp",
                                className="sl-button",
                                color="warning",
                                style={"marginTop" : "1rem",}
                            ),
                        ],
                        className="d-grid gap-2 col-3 mx-auto",
                    ),
                ],
            ),
        ],
        id="load-exp-modal",
        centered=True,
        is_open=False,
    )

def simulationOperationButtons():
    return html.Div(
        children=[
            html.Div(
                [
                    dbc.Button(
                        children = [ html.I(className="fas fa-solid fa-vial", style={"margin-right":"1rem"}), "Load"],
                        id="load-sim",
                        className="sim-btns",
                        color="warning",
                    ),
                ],
                className="d-grid gap-2 col-3 mx-auto",
            ),

            html.Div(
                [
                    dbc.Button(
                        #fa-bolt-lightning, fa-gears, "Run Simulation", 
                        children = [ html.I(className="fas fa-solid fa-bolt-lightning", style={"margin-right":"1rem"}), "Simulate"],
                        id="run-sim",
                        className="sim-btns",
                        color="warning",
                    ),
                ],
                className="d-grid gap-2 col-3 mx-auto",
            ),

            html.Div(
                [
                    dbc.Button(#"Save experiment", 
                        children = [ html.I(className="fas fa-solid fa-file-pen", style={"margin-right":"1rem"}), "Save"],
                        id="save-exp",
                        className="sim-btns",
                        color="warning",
                    ),
                ],
                className="d-grid gap-2 col-3 mx-auto",
            ),
        ],
        style={
            "display":"flex",
            "margin-top":"1rem",
        }
    )

def alerts():
    return [
        dbc.Alert(
            "Experiment has been saved",
            id="save-alert",
            is_open=False,
            fade=True,
            duration=4000,
            color="success",
            style={"margin":"0", "padding":"0.80rem"},
        ),
        dbc.Alert(
            "Please enter valid inputs for stimulus type",
            id="stim-alert",
            is_open=False,
            fade=True,
            duration=4000,
            color="danger",
            style={"margin":"0", "padding":"0.80rem"},
        ),
        dbc.Alert(
            "Duplicate stimulus are not allowed",
            id="stim-dup-alert",
            is_open=False,
            fade=True,
            duration=4000,
            color="warning",
            style={"margin":"0", "padding":"0.80rem"},
        ),
        dbc.Alert(
            "Please enter valid inputs for visual object",
            id="vo-alert",
            is_open=False,
            fade=True,
            duration=4000,
            color="danger",
            style={"margin":"0", "padding":"0.80rem"},
        ),
        dbc.Alert(
            "Duplicate visual objects are not allowed",
            id="vo-dup-alert",
            is_open=False,
            fade=True,
            duration=4000,
            color="warning",
            style={"margin":"0", "padding":"0.80rem"},
        ),
        dbc.Alert(
            children=[],
            id="run-sim-alert",
            is_open=False,
            fade=True,
            duration=4000,
            color="danger",
            style={"margin":"0", "padding":"0.80rem"},
        ),
        dbc.Alert(
            "An error occured while loading the requested experiment...",
            id="load-alert",
            is_open=False,
            fade=True,
            duration=4000,
            color="danger",
            style={"margin":"0", "padding":"0.80rem"},
        ),
        dbc.Alert(
            "Experiment name already exists. Please use another name!",
            id="trial-dup-alert",
            is_open=False,
            fade=True,
            duration=4000,
            color="warning",
            style={"margin":"0", "padding":"0.80rem"},
        ),
    ]