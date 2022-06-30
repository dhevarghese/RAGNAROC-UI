import os
import pickle
import sys
import numpy as np

from dash import dcc, html, dash_table, callback_context
from plotly.subplots import make_subplots
from dash_extensions.enrich import Dash, Output, Input, State, ServersideOutput, Trigger, EnrichedOutput

import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

# from model import ragnaroc
import ragnaroc


def stim_type_form():
    return html.Div(
        id="stim-type-form",
        style={"color":"White", "marginLeft": "2.1rem", "marginRight": "2rem"},
        children=[
            html.P("Stimulus",style={"display":"inline"}),
            #html.P("Stimulus Type",style={"color":"#EE4B2B", "display":"inline"}),
            dcc.Input(
                id="stim-type-name",
                placeholder='Name',
                type='text',
                # type='number',
                # readOnly=True,
                value='',
                style=
                {
                    "color":"white",
                    "marginLeft":"16px",
                    "background": "transparent",
                    "borderBottomColor": "white",
                    "borderInlineStyle": "none",
                    "padding":"4px",
                    "borderRadius":"4px",
                    "borderTop": "transparent",
                }
            ),

            html.Div(children=[
                html.Div(
                    children=[
                        html.P("Top-Down Weight", style={"margin": "1.5rem 0rem" }),
                        dcc.Input(
                            id="text-td-weight",
                            className="hideNumScroll",
                            type='number',
                            value=0.5,
                            step=0.01,
                            min=0, max=1,
                            style=
                            {
                                "color":"white",
                                "backgroundColor": "black",
                                # "borderBottomColor": "white",
                                # "borderInlineStyle": "none",
                                "padding":"4px",
                                "verticalAlign": "text-bottom",

                                "borderRadius": "5rem",
                                "border": "2px solid white",
                                #"text-indent": "1.4rem",
                                "width":"10%",
                                "textAlign": "center",
                            }
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "space-between",
                        "marginTop": "1rem",
                    }
                ),
                
                dcc.Slider(0,1,value=0.5, id="top-down", tooltip={"placement": "bottom", }, className="slider-margin"),
                
                html.Div(
                    children=[
                        html.P("Bottom-Up Weight", style={"margin": "1.5rem 0rem"}),
                        dcc.Input(
                            id="text-bu-weight",
                            className="hideNumScroll",
                            type='number',
                            value=0.5,
                            step=0.01,
                            min=0, max=1,
                            style=
                            {
                                "color":"white",
                                "backgroundColor": "black", # #272a31
                                # "borderBottomColor": "white",
                                # "borderInlineStyle": "none",
                                "padding":"4px",
                                "verticalAlign": "text-bottom",

                                "borderRadius": "5rem", #0.5rem
                                "border": "2px solid white", #none
                                #"text-indent": "1.4rem",

                                "width":"10%", #15%
                                "textAlign": "center",
                            }
                        ),
                    ],
                    style={
                        "display": "flex",
                        "alignItems": "center",
                        "justifyContent": "space-between",
                        "marginTop": "1rem",
                    }
                ),
                
                dcc.Slider(0,1,value=0.5, id="bottom-up", tooltip={"placement": "bottom", }, className="slider-margin"), # "always_visible": True
                html.Button(#"Add", 
                    html.I(className="fas fa-solid fa-plus"),
                    id="add-stim-type",
                    form="stim-type-form",
                    n_clicks=0,
                    style={
                            #"width": "30%", 
                            "width": "20%", 
                            "marginTop": "20px", 
                            "marginBottom" : "1.5rem",
                            "marginInline": "auto", 
                            "display": "block", "border": "2px solid #fccd61", 
                            "borderRadius": "8px", 
                            "backgroundColor":"#fccd61", 
                            "color": "darkslateblue", 
                            "fontWeight": "bold"
                        }
                    ),
                # html.Hr(
                #     style={
                #         "height": "2px",
                #         "borderWidth": "0",
                #         "margin": "2rem" #"1rem 1rem"
                #     }
                # ),
            ], style={
                # "marginLeft": "16px", "marginTop":"16px", "marginBottom":"8px"
                "margin": "0rem 1rem 0.5rem"
            }), 
        ]
    )

def visual_objects_form():
    return html.Div(
        style={"color":"White", "marginLeft": "2.1rem", "marginRight": "2rem"},
        children=[
            html.P("Visual Objects",style={"display":"inline"}),
            dcc.Input(
                id="vis-obj-name",
                placeholder='Name',
                type='text',
                value='',
                style=
                {
                    "color":"white",
                    "marginLeft":"16px",
                    "background": "transparent",
                    "borderBottomColor": "white",
                    "borderInlineStyle": "none",
                    "padding":"4px",
                    "borderRadius":"4px",
                    "borderTop": "transparent",
                }
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
                    #dbc.Input(id="vis-obj-x", placeholder="Coordinate..?", type="number", min=1, max=27),
                    dcc.Input(
                        id="vis-obj-x",
                        placeholder="Coordinate",
                        type='number',
                        min=1, max=27,
                        className="hideNumScroll",
                        style=
                        {
                            "color":"white",
                            "backgroundColor": "black",
                            "borderBottomColor": "white",
                            "borderInlineStyle": "none",
                            "padding":"4px",
                            "verticalAlign": "text-bottom",

                            "borderRadius": "0.5rem",
                            # "border": "none",
                            "border-top": "hidden",
                            "textIndent": "1rem",
                        }
                    ),
                    dbc.Tooltip(
                        "Range: (1,27) ",
                        target="vis-obj-x",
                        placement="top",
                    ),

                    html.P("Y", style={"paddingTop":"16px", "paddingRight":"36px", "paddingLeft":"72px"}),
                    #dbc.Input(id="vis-obj-y", placeholder="Coordinate..?", type="number", min=1, max=27),
                    dcc.Input(
                        id="vis-obj-y",
                        placeholder="Coordinate",
                        type='number',
                        min=1, max=27,
                        className="hideNumScroll",
                        style=
                        {
                            "color":"white",
                            "backgroundColor": "black",
                            "borderBottomColor": "white",
                            "borderInlineStyle": "none",
                            "padding":"4px",
                            "verticalAlign": "text-bottom",

                            "borderRadius": "0.5rem",
                            #"border": "none",
                            "border-top": "hidden",
                            "textIndent": "1rem",
                        }
                    ),
                    
                    dbc.Tooltip(
                        "Range: (1,27) ",
                        target="vis-obj-y",
                        placement="top",
                    ),
                ], style={"display":"flex", "marginBottom":"2rem", "marginTop":"2rem", "justifyContent":"space-around"}),
                #1,1.5

                html.Div(children=[
                    html.P("Duration", style={"paddingTop":"16px", "paddingRight":"12px" }),
                    #dbc.Input(id="vis-obj-duration", placeholder="in milli-seconds..?", type="number", min=0, max=1000),
                    dcc.Input(
                        id="vis-obj-duration",
                        placeholder="in milli-seconds",
                        type='number',
                        min=0, max=1000,
                        className="hideNumScroll",
                        style=
                        {
                            "color":"white",
                            "backgroundColor": "black",
                            "borderBottomColor": "white",
                            "borderInlineStyle": "none",
                            "padding":"4px",
                            "verticalAlign": "text-bottom",

                            "borderRadius": "0.5rem",
                            # "border": "none",
                            "border-top": "hidden",
                            "textIndent": "1rem",
                        }
                    ),

                    dbc.Tooltip(
                        "Maximum: 1000 ms ",
                        target="vis-obj-duration",
                        placement="bottom",
                    ),
                    html.P("Latency", style={"paddingTop":"16px", "paddingRight":"12px", "paddingLeft":"48px"}),
                    #dbc.Input(id="vis-obj-latency", placeholder="in milli-seconds..?", type="number", min=0, max=1000),
                    dcc.Input(
                        id="vis-obj-latency",
                        placeholder="in milli-seconds",
                        type='number',
                        min=0, max=1000,
                        className="hideNumScroll",
                        style=
                        {
                            "color":"white",
                            "backgroundColor": "black",
                            "borderBottomColor": "white",
                            "borderInlineStyle": "none",
                            "padding":"4px",
                            "verticalAlign": "text-bottom",

                            "borderRadius": "0.5rem",
                            #"border": "none",
                            "border-top": "hidden",
                            "textIndent": "1rem",
                            
                        }
                    ),
                    dbc.Tooltip(
                        "Maximum: 1000 ms ",
                        target="vis-obj-latency",
                        placement="bottom",
                    ),
                ], style={"display":"flex", "justifyContent":"space-around", "marginBottom":"2rem", "marginTop":"2rem"}),
                #1,1.1

                # html.Div(children=[
                #     html.P("Stimulus Type", style={"paddingBottom":"4px", "paddingTop": "36px"}),
                #     dcc.Dropdown(options=[], value='', style={"width":"75%", "marginLeft":"36px", "marginTop":"16px"}),
                # ], style={"display":"flex"}),
                
                html.Div(
                    children=[
                        html.P(
                            "Stimulus type", 
                            style={
                                "width":"50%", 
                                "textAlign": "center"
                            }
                        ),
                        html.Div(
                            dcc.Dropdown(options=[], value='', id="vis-obj-stim-type",), 
                            style={
                                "width":"35%",
                            }
                        ),
                    ],
                    style={
                        "display":"flex",
                        "margin":"2.6rem 1rem 1.6rem",
                    }
                    #1.5,1,1.5
                ),
                
                html.Button(#"Add", 
                    html.I(className="fas fa-solid fa-plus"),
                    id="vis-obj-add",
                    n_clicks=0,
                    style={
                            #"width": "30%", 
                            "width": "20%",
                            "marginTop": "1.625rem",  #1.5
                            "marginBottom":"1.5rem",
                            "marginInline": "auto", 
                            "display": "block", "border": "2px solid #fccd61", 
                            "borderRadius": "8px", 
                            "backgroundColor":"#fccd61", 
                            "color": "darkslateblue", 
                            "fontWeight": "bold"
                        }
                    ),
            ], style={
                # "marginLeft": "16px", "marginTop":"16px",
                "margin": "1rem 1rem 0.5rem",
            }), 
        ]
    )

def getStimulusTable():
    return html.Div(
        id="stim-table",
        children=[
            html.P("Stimulus Types"),
            dash_table.DataTable(
                id='stim-types-table',
                columns=[
                    {
                        'name': 'Stimulus name',
                        'id': 'stimName',
                    },
                    {
                        'name': 'Top Down',
                        'id': 'td',
                    },
                    {
                        'name': 'Bottom Up',
                        'id': 'bu',
                    }
                ],
                #data=[{'stim-type-item': 1, 'td-weights': 1, 'bu-weights': 1 }]
                data=[],
                row_deletable=True,
                style_as_list_view=True,
                #editable=True,
                style_cell={
                    'padding': '5px',
                },
                style_header={
                    'padding': '5px',
                    'backgroundColor': 'rgb(30, 30, 30)',
                    'color': 'white',
                    'border': '1px solid black',                            
                },
                style_data={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white'
                },
                css=[
                    {"selector": ".dash-spreadsheet-container table", "rule": '--text-color: #fccd61 !important'},
                ],
                style_data_conditional=[
                    {
                        "if": {"state": "active"},  # 'active' | 'selected'
                        "backgroundColor": "black",
                        "border": "3px solid white",
                        "color": "#fccd61",
                    },{
                        "if": {"state": "selected"},
                        # "backgroundColor": "rgba(255,255,255, 0.1)",
                        "backgroundColor": "#444444",
                    },
                ],
            ),
        ],
        style={
            #"paddingTop": 72,
            "marginTop": "6rem",
            "display":"block",
        },
    )

def getVisualObjectsTable():
    return html.Div(
        id="vo-table",
        children=[
            html.P("Visual Objects"),
            dash_table.DataTable(
                id='vis-objs-table',
                columns=[
                    {
                        'name': 'Name',
                        'id': 'name',
                    },
                    {
                        'name': 'X',
                        'id': 'X',
                    },
                    {
                        'name': 'Y',
                        'id': 'Y',
                    },
                    {
                        'name': 'Duration',
                        'id': 'duration',
                    },
                    {
                        'name': 'Latency',
                        'id': 'latency',
                    },
                    {
                        'name': 'Stimulus',
                        'id': 'stimulus',
                    }
                ],
                data=[],
                row_deletable=True,
                style_as_list_view=True,
                #editable=True,
                style_cell={
                    'padding': '5px',
                },
                style_header={
                    'padding': '5px',
                    'backgroundColor': 'rgb(30, 30, 30)',
                    'color': 'white',
                    'border': '1px solid black',                            
                },
                style_data={
                    'backgroundColor': 'rgb(50, 50, 50)',
                    'color': 'white'
                },
                css=[
                    {"selector": ".dash-spreadsheet-container table", "rule": '--text-color: #fccd61 !important'},
                ],
                style_data_conditional=[
                    {
                        "if": {"state": "active"},  # 'active' | 'selected'
                        "backgroundColor": "black",
                        "border": "3px solid white",
                        "color": "#fccd61",
                    },{
                        "if": {"state": "selected"},
                        # "backgroundColor": "rgba(255,255,255, 0.1)",
                        "backgroundColor": "#444444",
                    },
                ],
            ),
        ],
        style={
            "marginTop": "6rem",
            "display":"none",
        },
    )

def serve_layout(app):
    return html.Div(children=[html.Div(
        id="root",
        children=[
            # Main body
            html.Div(
                id="app-container",
                children=[
                    # Banner display
                    html.Div(
                        id="top-bar",
                        children=[
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
                                        placeholder='ms',
                                        type='number',
                                        value='',
                                        style=
                                        {
                                            "color":"white",
                                            "marginLeft":"16px",
                                            "background": "transparent",
                                            "borderBottomColor": "white",
                                            "borderInlineStyle": "none",
                                            "padding":"4px",
                                            "borderRadius":"4px",
                                            "borderTop": "transparent",
                                            "width":"30%",
                                        }
                                    ),
                                ],
                                style={
                                    "alignSelf":"center",
                                    "text-align":"end",
                                }
                            ),
                        ],
                        style={
                            "display":"flex",
                            "justify-content":"space-between",
                        }
                    ),
                    html.Div(
                        id="experiment-settings",
                        children=[
                            html.Div(
                                id="experiment-forms",
                                children=[
                                    html.Div(
                                        [
                                            html.H1('Experiment ', style={"display": "inline", }),
                                            dcc.Input(
                                                id="exp-name",
                                                placeholder='Name',
                                                type='text',
                                                # value='sample',
                                                style=
                                                {
                                                    "color":"white",
                                                    "backgroundColor": "black",
                                                    "borderBottomColor": "white",
                                                    "borderInlineStyle": "none",
                                                    "padding":"4px",
                                                    "verticalAlign": "text-bottom",
                                                    "textIndent":"0.5rem",
                                                    #"borderRadius":"4px",
                                                }
                                            ),                                             
                                            dbc.Badge(" ! ", color="danger", className="me-1", style={"fontSize":"Large", "fontFamily":"Auto", "margin": "0px 8px 12px", "verticalAlign": "super", "display":"none"}), #display on error
                                        ],
                                        style={"color":"White", "textAlign": "center", "marginBottom":"1rem", "marginTop":"1rem"},
                                    ),
                                    
                                    html.Div(
                                        children=[
                                            dcc.Tabs(
                                                id="exp-form-tabs",
                                                value="stim-form",
                                                children=[
                                                    dcc.Tab(
                                                        label='Stimulus Types', 
                                                        value="stim-form",
                                                        children=stim_type_form(),
                                                        # className='custom-tab no-left-border',
                                                        # selected_className='custom-tab--selected no-left-border',
                                                        className='custom-tab-2',
                                                        selected_className='custom-tab-2--selected',
                                                    ),
                                                    dcc.Tab(
                                                        label='Visual Objects', 
                                                        value="vo-form",
                                                        children=visual_objects_form(),
                                                        # className='custom-tab no-right-border',
                                                        # selected_className='custom-tab--selected no-right-border',
                                                        className='custom-tab-2',
                                                        selected_className='custom-tab-2--selected',
                                                    ),
                                                ],
                                                style={
                                                    "margin":"2rem",
                                                }
                                            ),
                                        ],
                                        style={
                                            "background-color": "black",
                                            "border-radius": "1rem",
                                            "border": "2px solid white",
                                            "margin-top": "2rem",
                                            "margin-bottom": "1rem",
                                        }
                                    ),

                                    # stim_type_form(),
                                    # #html.Br(),
                                    # visual_objects_form(), 
                                ],
                            )
                        ],
                    ),
                    html.Div(id="garbage-output-0"),
                    html.Div(
                        [
                            dcc.Loading(
                                [
                                    dcc.Store(id='sim-store'),
                                    dcc.Store(id='original-store'),
                                    # html.Div(
                                    #     [
                                    #         dbc.Button(#"Run Simulation", 
                                    #             children = [ html.I(className="fas fa-solid fa-bolt-lightning", style={"margin-right":"1rem"}), "Simulate"],
                                    #             id="run-sim",
                                    #             color="warning",
                                    #             style={
                                    #                 "color": "darkslateblue", 
                                    #                 "fontWeight": "bold",
                                    #                 "marginTop":"16px",
                                    #             }
                                    #         ),
                                    #         dbc.Button(#"Save experiment", 
                                    #             html.I(className="fas fa-solid fa-file-pen"),
                                    #             color="warning",
                                    #             disabled="True",
                                    #             style={
                                    #                 "color": "darkslateblue", 
                                    #                 "fontWeight": "bold",
                                    #                 #"marginTop":"70%",
                                    #                 "marginTop":"4rem",
                                    #                 "position": "relative"
                                    #             }
                                    #         ),
                                    #     ],
                                    #     className="d-grid gap-2 col-6 mx-auto",
                                    # ),
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader( dbc.ModalTitle("But, who are you?"),
                                                style={
                                                    "color":"white",
                                                    "background":"black",
                                                }
                                            ),
                                            dbc.ModalBody(
                                                children=[
                                                    html.P("Let us know your code name, experimenter."),
                                                    dcc.Input(
                                                        id="exp-creator-name",
                                                        placeholder='Thor',
                                                        type='text',
                                                        style=
                                                        {
                                                            "color":"white",
                                                            "backgroundColor": "black",
                                                            "border": "2px solid white",
                                                            "border-radius": "5rem",
                                                            "margin" : "1rem",
                                                            "padding":"4px",
                                                            "verticalAlign": "text-bottom",
                                                            "textIndent":"1rem",
                                                        }
                                                    ),          
                                                    html.P("Note: This name may not be unique. This place attracts experimenters..."),
                                                    html.Div(
                                                        [
                                                            dbc.Button(
                                                                children = ["Save"],
                                                                id="save-creator-exp",
                                                                color="warning",
                                                                style={
                                                                    "color": "white", 
                                                                    "background-color":"transparent",
                                                                    "border-color" : "white",
                                                                    "fontWeight": "bold",
                                                                }
                                                            ),
                                                        ],
                                                        # className="d-grid gap-2 col-4 mx-auto",
                                                        className="d-grid gap-2 col-3 mx-auto",
                                                    ),
                                                ],   
                                                style={
                                                    "color":"white",
                                                    "background":"black",
                                                    "text-align" : "center",
                                                } 
                                            ),
                                        ],
                                        id="creator-modal",
                                        centered=True,
                                        is_open=False,
                                    ),
                                    dbc.Modal(
                                        [
                                            dbc.ModalHeader( dbc.ModalTitle("Do I remember you?"),
                                                style={
                                                    "color":"white",
                                                    "background":"black",
                                                }
                                            ),
                                            dbc.ModalBody(
                                                children=[
                                                    html.Div(
                                                        children=[
                                                            html.P("Creator name:"),
                                                            dcc.Input(
                                                                id="load-exps-creator",
                                                                placeholder='Thor',
                                                                type='text',
                                                                debounce=True,
                                                                style=
                                                                {
                                                                    "color":"white",
                                                                    "backgroundColor": "black",
                                                                    "borderBottomColor": "white",
                                                                    "borderInlineStyle": "none",
                                                                    "padding":"4px",
                                                                    "verticalAlign": "text-bottom",
                                                                    "textIndent":"0.5rem",
                                                                    "marginLeft" : "3rem",
                                                                    "borderTop" : "none",
                                                                }
                                                            ),        
                                                        ],
                                                        style = {
                                                            "display" : "flex",
                                                            "marginTop" : "1rem",
                                                            "marginBottom" : "2rem",
                                                        }
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
                                                                style={
                                                                    "width" : "45%",
                                                                    "marginLeft" : "1rem",
                                                                }
                                                            ),
                                                            
                                                        ],
                                                        style={
                                                            "display":"flex",
                                                            "marginTop" : "1rem",
                                                        },
                                                        #id="loaded-div",
                                                    ),
                                                    html.Div(
                                                        [
                                                            dbc.Button(
                                                                children = ["Load"],
                                                                id="load-creator-exp",
                                                                color="warning",
                                                                style={
                                                                    "color": "white", 
                                                                    "background-color":"transparent",
                                                                    "border-color" : "white",
                                                                    "fontWeight": "bold",
                                                                    "marginTop" : "1rem",
                                                                }
                                                            ),
                                                        ],
                                                        # className="d-grid gap-2 col-4 mx-auto",
                                                        className="d-grid gap-2 col-3 mx-auto",
                                                    ),
                                                ],   
                                                style={
                                                    "color":"white",
                                                    "background":"black",
                                                    "text-align" : "center",
                                                } 
                                            ),
                                        ],
                                        id="load-exp-modal",
                                        centered=True,
                                        is_open=False,
                                    ),
                                    html.Div(
                                        children=[
                                            html.Div(
                                                [
                                                    dbc.Button(#"Run Simulation", 
                                                        #fa-bolt-lightning, fa-gears
                                                        children = [ html.I(className="fas fa-solid fa-vial", style={"margin-right":"1rem"}), "Load"],
                                                        id="load-sim",
                                                        color="warning",
                                                        style={
                                                            "color": "darkslateblue", 
                                                            "fontWeight": "bold",
                                                        }
                                                    ),
                                                ],
                                                # className="d-grid gap-2 col-4 mx-auto",
                                                className="d-grid gap-2 col-3 mx-auto",
                                            ),

                                            html.Div(
                                                [
                                                    dbc.Button(#"Run Simulation", 
                                                        #fa-bolt-lightning, fa-gears
                                                        children = [ html.I(className="fas fa-solid fa-bolt-lightning", style={"margin-right":"1rem"}), "Simulate"],
                                                        id="run-sim",
                                                        color="warning",
                                                        style={
                                                            "color": "darkslateblue", 
                                                            "fontWeight": "bold",
                                                        }
                                                    ),
                                                ],
                                                # className="d-grid gap-2 col-4 mx-auto",
                                                className="d-grid gap-2 col-3 mx-auto",
                                            ),

                                            html.Div(
                                                [
                                                    dbc.Button(#"Save experiment", 
                                                        #html.I(className="fas fa-solid fa-file-pen"),
                                                        children = [ html.I(className="fas fa-solid fa-file-pen", style={"margin-right":"1rem"}), "Save"],
                                                        id="save-exp",
                                                        color="warning",
                                                        # disabled="True",
                                                        style={
                                                            "color": "darkslateblue", 
                                                            "fontWeight": "bold",
                                                        }
                                                    ),
                                                ],
                                                # className="d-grid gap-2 col-4 mx-auto",
                                                className="d-grid gap-2 col-3 mx-auto",
                                            ),
                                        ],
                                        style={
                                            "display":"flex",
                                            "margin-top":"1rem",
                                        }
                                    ),
                                ],
                                type="circle",
                                color="#fccd61",
                                style={"marginTop":"1rem", "marginLeft":"1rem"},
                            ),
                        ],
                    ),
                    html.Div(
                        children=[
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
                                "Maximum stimuli count reached",
                                id="stim-count-alert",
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
                                color="danger",
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
                                color="danger",
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
                        ],
                        style={"marginTop":"1.5rem"}
                    ),
                ],
            ),
            html.Div(
                id="sidebar",
                children=[
                    html.Div(
                        children=[
                            html.P("Use preset?",
                                style={
                                    "width":"50%",
                                    "paddingTop":"0.2rem",
                                }
                            ),
                            html.Div(
                                dcc.Dropdown(options=["Brisson", "Single", "Same", "Diff", "MidTLateralD", "EimerGrubert"], value='', id="preset-experiment-choice",), # "Same", throws errors
                                style={
                                    "width":"70%",
                                },
                            ),

                        ],
                        style={
                            "display":"flex",
                        },
                    ),
                    # html.Div(id='tabs-table',
                    #     children=[
                    #         getStimulusTable()
                    #     ],
                    # ),
                    getStimulusTable(),
                    getVisualObjectsTable(),
                    # html.Div(
                    #     [
                    #         dbc.Button("Save experiment", 
                    #             id="save-exp",
                    #             color="warning",
                    #             disabled="True",
                    #             style={
                    #                 "color": "darkslateblue", 
                    #                 "fontWeight": "bold",
                    #                 #"marginTop":"70%",
                    #                 "marginTop":"4rem",
                    #                 "position": "relative"
                    #             }
                    #         ),
                    #     ],
                    #     className="d-grid gap-2 col-6 mx-auto",
                    #     style={"marginTop":"16px"}
                    # ),
                ]
            ),
        ],),
        html.Div(
            id="results-visual",
            children=[
                # html.H1('Results ', style={"color": "White", "fontFamily": "Playfair Display, serif", "margin":"3rem"}),
                html.Div(
                    children=[
                        html.H1('Results ', style={"color": "White", "fontFamily": "Norse", "margin":"3rem", "font-size":"3rem"}), #Playfair Display, serif | Norse
                        html.H1(' ? ', id="result-info", style={"fontFamily": "Playfair Display, serif", "margin":"3rem", "paddingRight":"2rem"}),
                    ],
                    style={
                        "display":"flex",
                        "justifyContent":"space-between"
                    },
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader( dbc.ModalTitle("Info"),
                            style={
                                "color":"white",
                                "background":"black",
                            }
                        ),
                        dbc.ModalBody(
                            children=[
                                html.P("The AM and IG Maps are independent of stimulus"),
                                html.P("Clicking on the 3D surface plots update the line plots"),
                                html.P("The line plots display activations of the chosen map, at the clicked point"),
                            ],   
                            style={
                                "color":"white",
                                "background":"black",
                            } 
                        ),
                    ],
                    id="result-modal",
                    centered=True,
                    is_open=False,
                ),
                html.Div(
                    className="row", 
                    children=[
                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.P("Select map", style={"fontSize": "large", "marginTop": "4px"}),
                                    ], 
                                    style={
                                        "width":'50%', 
                                        "color":"White", 
                                        "textAlign":"center"
                                    },
                                ),
                                html.Div(
                                    className='six columns', 
                                    children=[
                                        dcc.Dropdown(
                                            # options=["IG", "AM", "II", "LV", "EV"],
                                            options=[
                                                {'label': 'Inhibitory Gate (IG)', 'value': 'IG'},
                                                {'label': 'Attention Map (AM)', 'value': 'AM'},
                                                {'label': 'Inhibitory Interneuron (II)', 'value': 'II'},
                                                {'label': 'Late Visual (LV)', 'value': 'LV'},
                                                {'label': 'Early Visual (EV)', 'value': 'EV'},
                                            ],
                                            value='IG',
                                            id= "map-dropdown",
                                            clearable=False,
                                            searchable=False,
                                        )
                                    ],
                                    style={
                                        "width":'40%', 
                                    },
                                ),
                            ],
                            style = {
                                "display":'flex',
                                "width":"40%",
                                "backgroundColor": "#272a31", # rgb(39, 42, 49)
                                "borderRadius": "1rem",
                                "paddingTop": "1rem",
                                # "padding-bottom": "0.5rem",
                                "marginLeft" : "10rem",
                            }
                        ),

                        html.Div(
                            children=[
                                html.Div(
                                    children=[
                                        html.P("Select stimulus", style={"fontSize": "large", "marginTop": "4px"}),
                                    ], 
                                    style={
                                        "width":'50%', 
                                        "color":"White", 
                                        "textAlign":"center"
                                    },
                                ),
                                html.Div(
                                    className='six columns', 
                                    children=[
                                        dcc.Dropdown(
                                            options=[], 
                                            value='', 
                                            id='stim-type-dropdown',
                                            clearable=False, 
                                            searchable=False,
                                        ),
                                    ], 
                                    style={
                                        "width":'40%', 
                                    },
                                ),
                            ],
                            style = {
                                "display":'flex',
                                "width":"40%",
                                "backgroundColor": "#272a31", # rgb(39, 42, 49)
                                "borderRadius": "1rem",
                                "paddingTop": "1rem",
                                "marginLeft" : "4rem",
                            }
                        ),
                    
                    ], 
                    style={
                        "display":'flex',
                        # "marginRight":"5rem",
                        "marginRight":"2rem",
                        "marginLeft":"2rem",
                        "marginBottom":"1rem",
                    },
                ),

                html.Div(
                    className="row", 
                    children=[
                        html.Div(
                            children=[
                                dcc.Loading(
                                    [
                                        dcc.Graph(id="surface-viz", 
                                            figure={
                                                "layout": go.Layout(width=700, height=600, margin=dict(r=35, l=35, b=30, t=30), template= "plotly_dark",),
                                            },
                                            style={
                                                "paddingLeft" : "1.5rem",
                                                "marginRight" : "1rem",
                                                # 'border':'1px solid', 'border-radius': "10px", 'backgroundColor':'#FFFFFF'
                                            },
                                        ),
                                    ],
                                    type="circle", # cube, default, circle
                                    color="#fccd61",
                                    
                                ),
                                dcc.Loading(
                                    [
                                        dcc.Graph(id="line-viz", 
                                            figure={
                                                "layout": go.Layout(width=700, height=600, margin=dict(r=35, l=35, b=30, t=30), template= "plotly_dark",),
                                            },
                                            style={
                                                "paddingLeft" : "1rem",
                                                "marginLeft":"3rem", #1rem
                                            },
                                        ),
                                        html.Div(
                                            children = [
                                                html.P(
                                                    "Time Marker", 
                                                    style={
                                                        "fontSize": "large", 
                                                        "color": "white",
                                                        "marginRight": "3rem",
                                                    }),
                                                dbc.Input(
                                                    id="lineplot-time", placeholder="ms", type="number", min=0, max=600, debounce=True, className="hideNumScroll",
                                                    style={
                                                        "width":"30%",
                                                        "backgroundColor":"black"
                                                        #"margin": "1rem 15rem 1rem",
                                                    },
                                                ),
                                            ],
                                            style={
                                                #"margin": "1rem 15rem",
                                                "margin": "1rem 5rem 0rem",
                                                "placeContent": "center",
                                                "display": "flex",
                                                "alignItems": "baseline",
                                            },
                                        ),
                                    ],
                                    type="circle", # cube, default, circle
                                    color="#fccd61",
                                ),
                            ],
                            style={"margin":"16px", "display":"flex"}
                        ),
                        
                    ], 
                    style={
                        "display":'flex',
                        "margin":"1rem 2rem 1rem",
                        "alignSelf": "center",
                    },
                ),

            ],
            style = {
                "display": "none",
            },
        ),
    ],)