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

external_stylesheets = [dbc.themes.BOOTSTRAP,
                        #'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css',
                        #'https://use.fontawesome.com/releases/v5.8.1/css/all.css',
                        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css'
                       ]

app = Dash(__name__, external_stylesheets=external_stylesheets, prevent_initial_callbacks=True, update_title=None, assets_folder ="static", assets_url_path="static")

app.title='Ragnaroc'
# application = app.server


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

def frame_args(duration):
    return {
            "frame": {"duration": duration},
            "mode": "immediate",
            "fromcurrent": True,
            "transition": {"duration": duration, "easing": "linear"},
        }

def getSurfaceGraphLayout(currSliderVal=200, runtime=0):
    return go.Layout(
        template= "plotly_dark",
        title = "Surface Plot",
        scene = dict
        (
            aspectratio=dict(x=1,y=1,z=1),
            xaxis = dict(title= dict(text = 'x', font = {"size" : 16}), range = [0,30], tickfont = dict(size=14),), #Modify the axes
            yaxis = dict(title= dict(text = 'y', font = {"size" : 16}), range = [0,30], tickfont = dict(size=14)),
            zaxis = dict(title= dict(text = 'z', font = {"size" : 16}), showticklabels=False, showgrid=False, zeroline=False, range = [0,256],),
            camera = dict(
                eye=dict(x=1.31, y=1.31, z=1.31)
            ),
        ),
        width=700, height=600, 
        #margin=dict(r=5, l=5, b=5, t=5), #paper_bgcolor='#fccd61',
        updatemenus=[
            {
                "buttons": [
                    {
                        "args": [None, frame_args(1)], #1, 100 ?
                        "label": "&#9654;", # play symbol
                        "method": "animate",
                    },
                    {
                        "args": [[None], frame_args(0)],
                        "label": "&#9724;", # pause symbol
                        "method": "animate",
                    },
                ],
                "direction": "left",
                #"pad": {"r": 10, "t": 87},
                "pad": {"r": 10, "t": 90, "l":10},
                "showactive": True,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0.1,
                "yanchor": "top",
                # "visible": False,
                "active" : 1,
                "bgcolor" : "#fccd61",
                "font" : {"color": "darkslateblue"},
            },
        ],
        sliders = [
            {
                "pad": {"b": 10, "t": 20, "r":10},
                # "len": 0.9,
                "x": 0.1,
                "y": 0,
                # "visible": False,
                "steps": [
                    {
                        "args": [[k], frame_args(0)],
                        "label": str(k),
                        "method": "animate",
                    }
                    for k in range(0,runtime+1)
                ],
                "name" : "res-slider",
                "active": currSliderVal,
                "currentvalue" : {
                    "suffix" : " ms",
                }
            }
        ], 
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
                        'id': 'stim-type-item',
                    },
                    {
                        'name': 'Top Down',
                        'id': 'td-weights',
                    },
                    {
                        'name': 'Bottom Up',
                        'id': 'bu-weights',
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
                        'id': 'vis-objs-item',
                    },
                    {
                        'name': 'X',
                        'id': 'vis-objs-item-X',
                    },
                    {
                        'name': 'Y',
                        'id': 'vis-objs-item-Y',
                    },
                    {
                        'name': 'Duration',
                        'id': 'vis-objs-item-duration',
                    },
                    {
                        'name': 'Latency',
                        'id': 'vis-objs-item-latency',
                    },
                    {
                        'name': 'Stimulus',
                        'id': 'vis-objs-item-stim-type',
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

def serve_layout():
    return html.Div(children=[html.Div(
        id="root",
        children=[
            # Main body
            html.Div(
                id="app-container",
                children=[
                    # Banner display
                    # html.Div(
                    #     id="banner",
                    #     children=[
                    #         html.Img(
                    #             id="logo", src=app.get_asset_url("logo.png")
                    #         ),
                    #         html.H2("Ragnaroc", id="title", style={"font-family":"Norse", "marginTop":"1rem",}),
                    #         html.Div(
                    #             [

                    #                 html.P("Run time", style={"display":"contents", "color":"white"}),
                    #                 dcc.Input(
                    #                     id="exp-total-time",
                    #                     placeholder='ms',
                    #                     type='number',
                    #                     value='',
                    #                     style=
                    #                     {
                    #                         "color":"white",
                    #                         "marginLeft":"16px",
                    #                         "background": "transparent",
                    #                         "borderBottomColor": "white",
                    #                         "borderInlineStyle": "none",
                    #                         "padding":"4px",
                    #                         "borderRadius":"4px",
                    #                         "borderTop": "transparent",
                    #                     }
                    #                 ),
                    #             ],
                    #             style={"marginLeft":"auto"}
                    #         ),
                    #     ],
                    # ),
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
                                                value='sample',
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
                                    html.Div(
                                        children=[
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
                                                className="d-grid gap-2 col-4 mx-auto",
                                            ),

                                            html.Div(
                                                [
                                                    dbc.Button(#"Save experiment", 
                                                        #html.I(className="fas fa-solid fa-file-pen"),
                                                        children = [ html.I(className="fas fa-solid fa-file-pen", style={"margin-right":"1rem"}), "Save"],
                                                        id="save-exp",
                                                        color="warning",
                                                        disabled="True",
                                                        style={
                                                            "color": "darkslateblue", 
                                                            "fontWeight": "bold",
                                                        }
                                                    ),
                                                ],
                                                className="d-grid gap-2 col-4 mx-auto",
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
                        html.H1('Results ', style={"color": "White", "fontFamily": "Norse", "margin":"3rem"}), #Playfair Display, serif | Norse
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
                                        # dbc.Input(
                                        #     id="lineplot-time", placeholder="Enter timepoint", type="number", min=0, max=600, debounce=True,
                                        #     style={
                                        #         "width":"50%",
                                        #         "margin": "1rem 15rem 1rem",
                                        #     },
                                        # ),
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

                # html.Div(
                #     children = [
                #         dcc.Slider(0,600,value=200, id="sim-time", tooltip={"placement": "bottom",}), 
                #         # html.Button("speed up", id="speed", n_clicks=0),
                #     ],
                #     style={
                #         'width': '50%', 
                #         # 'padding': '0px 20px 20px 20px', 
                #         # "margin":"24px",
                #         "margin":"1rem",
                #         "marginLeft" : "15rem",
                #     }
                # ), 

            ],
            style = {
                # "backgroundColor": "#131417", # Colors - #131417, #2f394f
                # "display": "flex",
                "display": "none",
                # "flex-direction": "column",
                # #"padding": "4rem 2rem 10rem",
                # "padding": "1rem 2rem 2rem",
            },
        ),
    ],)

@app.callback(Output('stim-table', 'style'), Output('vo-table', 'style'),
              Input('exp-form-tabs', 'value'))
def render_content(tab):
    styleDisplay = {
        "display": "block",
        "marginTop": "6rem",
    }
    styleHide = {
        "display": "none",
        "marginTop": "6rem",
    }
    if tab == 'stim-form':
        return styleDisplay, styleHide
    elif tab == 'vo-form':
        return styleHide, styleDisplay

@app.callback(
    Output('vis-objs-table','data'), Output("vo-alert", "is_open"), Output("vo-dup-alert", "is_open"),
    [
        Input('vis-obj-add','n_clicks'), 
        Input('preset-experiment-choice','value'),
    ],
    [
        State('vis-objs-table','data'),
        State('vis-obj-name','value'),
        State('vis-obj-x','value'), 
        State('vis-obj-y','value'),
        State('vis-obj-duration','value'),
        State('vis-obj-latency','value'),
        State('vis-obj-stim-type','value'),
        State("vo-alert", "is_open"),
    ]
)
def addVisualObject(n_clicks, preset, rows, name, x, y, duration, latency, stimType, isOpen):
    ctx = callback_context
    openAlert = False
    duplicateObj = False

    inputId = ""
    if ctx.triggered:
        inputId = ctx.triggered[0]['prop_id'].split('.')[0]

    if(inputId == "vis-obj-add"):
        validated = True
        if ((x==None) or (y==None) or (duration==None) or (latency==None) or (stimType=="") or (name=="")) :
            validated = False

        openAlert = not validated

        for i in range(len(rows)):
            if(rows[i]["vis-objs-item"] == name):
                duplicateObj = True
                break
        
        if(n_clicks>0 and validated and not duplicateObj):
            #print(n_clicks)
            #visObjs.append(VisualObject(x,y, stimType,latency, duration))
            #visObjs[name]= VisualObject(x,y, stimType,latency, duration)
            rows.append({'vis-objs-item': name, 'vis-objs-item-X': x, 'vis-objs-item-Y': y, 'vis-objs-item-duration': duration, 'vis-objs-item-latency': latency, 'vis-objs-item-stim-type': stimType})
            #rows.append({'vis-objs-item': name, 'vis-objs-item-X': x, 'vis-objs-item-Y': y, 'vis-objs-item-duration': duration, 'vis-objs-item-latency': latency, 'vis-objs-item-stim-type': stimType})
            #return ["{} |".format(str(i)) for i in visObjs]
    elif (inputId == "preset-experiment-choice"):
        presetType = ctx.triggered[0]['value'].split('.')[0]
        rows = getExperimentVisualObjectPresets(presetType)
    elif (inputId == "input-alerts"):
        openAlert = isOpen
    
    return rows, openAlert, duplicateObj

def getExperimentVisualObjectPresets(presetType):
    preset = []
    if(presetType == "Brisson"):
        preset.append({'vis-objs-item': "1", 'vis-objs-item-X': 7, 'vis-objs-item-Y': 14, 'vis-objs-item-duration': 100, 'vis-objs-item-latency': 0, 'vis-objs-item-stim-type': "1"})
    elif(presetType == "Single"):
        preset.append({'vis-objs-item': "1", 'vis-objs-item-X': 7, 'vis-objs-item-Y': 14, 'vis-objs-item-duration': 500, 'vis-objs-item-latency': 0, 'vis-objs-item-stim-type': "1"})
    elif(presetType == "Same"):
        preset.append({'vis-objs-item': "1", 'vis-objs-item-X': 7, 'vis-objs-item-Y': 14, 'vis-objs-item-duration': 120, 'vis-objs-item-latency': 0, 'vis-objs-item-stim-type': "1"})
        preset.append({'vis-objs-item': "2", 'vis-objs-item-X': 7, 'vis-objs-item-Y': 14, 'vis-objs-item-duration': 120, 'vis-objs-item-latency': 120, 'vis-objs-item-stim-type': "2"})
    elif(presetType == "Diff"):
        preset.append({'vis-objs-item': "1", 'vis-objs-item-X': 7, 'vis-objs-item-Y': 14, 'vis-objs-item-duration': 120, 'vis-objs-item-latency': 0, 'vis-objs-item-stim-type': "1"})
        preset.append({'vis-objs-item': "2", 'vis-objs-item-X': 21, 'vis-objs-item-Y': 14, 'vis-objs-item-duration': 120, 'vis-objs-item-latency': 120, 'vis-objs-item-stim-type': "2"})
    elif(presetType == "MidTLateralD"):
        preset.append({'vis-objs-item': "1", 'vis-objs-item-X': 14, 'vis-objs-item-Y': 7, 'vis-objs-item-duration': 500, 'vis-objs-item-latency': 0, 'vis-objs-item-stim-type': "1"})
        preset.append({'vis-objs-item': "2", 'vis-objs-item-X': 7, 'vis-objs-item-Y': 14, 'vis-objs-item-duration': 500, 'vis-objs-item-latency': 0, 'vis-objs-item-stim-type': "2"})
    elif(presetType == "EimerGrubert"):
        preset.append({'vis-objs-item': "1", 'vis-objs-item-X': 10, 'vis-objs-item-Y': 10, 'vis-objs-item-duration': 40, 'vis-objs-item-latency': 0, 'vis-objs-item-stim-type': "1"})
        preset.append({'vis-objs-item': "2", 'vis-objs-item-X': 10, 'vis-objs-item-Y': 18, 'vis-objs-item-duration': 40, 'vis-objs-item-latency': 10, 'vis-objs-item-stim-type': "2"})
    return preset

@app.callback(
    Output("text-td-weight", "value"),
    Output("top-down", "value"),
    Input("text-td-weight", "value"),
    Input("top-down", "value"),
)
def callback(input_value, slider_value):
    ## https://dash.plotly.com/advanced-callbacks
    ctx = callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    value = input_value if trigger_id == "text-td-weight" else slider_value
    return value, value

@app.callback(
    Output("text-bu-weight", "value"),
    Output("bottom-up", "value"),
    Input("text-bu-weight", "value"),
    Input("bottom-up", "value"),
)
def callback(input_value, slider_value):
    ## https://dash.plotly.com/advanced-callbacks
    ctx = callback_context
    trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
    value = input_value if trigger_id == "text-bu-weight" else slider_value
    return value, value

@app.callback(
    Output('stim-types-table','data'), Output("stim-alert", "is_open"), Output("stim-count-alert","is_open"), Output("stim-dup-alert","is_open"),  #Output("stim-type-name", "style"),
    [
        Input('add-stim-type','n_clicks'),
        Input('preset-experiment-choice','value'),
    ],
    [State('stim-types-table','data'), State('stim-type-name','value'), State('top-down','value'), State('bottom-up','value'), State("stim-alert", "is_open"), State("stim-count-alert","is_open")]
)
def addStimulusType(n_clicks, preset, rows, name, tdWeight, buWeight, isOpen, maxStimuliReached):
    ctx = callback_context
    openAlert = False
    maxStimuliReached = False
    duplicateStimulus = False
    # style = {
    #     "color":"white",
    #     "marginLeft":"16px",
    #     "background": "transparent",
    #     "borderBottomColor": "white",
    #     "borderInlineStyle": "none",
    #     "padding":"4px",
    #     "borderRadius":"4px",
    #     "border-top": "transparent",
    # }

    inputId = ""
    if ctx.triggered:
        inputId = ctx.triggered[0]['prop_id'].split('.')[0]

    if(inputId == "add-stim-type"):  

        openAlert = (name=="") or (tdWeight > 1) or (tdWeight < 0) or (buWeight > 1) or (buWeight < 0) 
        maxStimuliReached = (len(rows) > 2)

        for i in range(len(rows)):
            if(rows[i]["stim-type-item"] == name):
                duplicateStimulus = True
                break

        # if openAlert:
        #     style["borderBottomColor"] = "red"
        #if(n_clicks>0 and (name!="") and (tdWeight <= 1) and (tdWeight >= 0) and (buWeight <= 1) and (buWeight >= 0) ):
        if(n_clicks>0 and not openAlert and not maxStimuliReached and not duplicateStimulus):
            #stimTypes.append(StimulusTypes(buWeight,tdWeight))
            #rows.append({'stim-type-item': (1 if rows==None else len(rows)+1), 'td-weights': tdWeight, 'bu-weights': buWeight})
            rows.append({'stim-type-item': name, 'td-weights': tdWeight, 'bu-weights': buWeight})
    elif (inputId == "preset-experiment-choice"):
        presetType = ctx.triggered[0]['value'].split('.')[0]
        rows = getExperimentStimulusTypesPresets(presetType)
    elif (inputId == "input-alerts"):
        openAlert = isOpen

    return rows, openAlert, maxStimuliReached, duplicateStimulus #, style

def getExperimentStimulusTypesPresets(presetType):
    preset = []
    if(presetType == "Brisson"):
        preset.append({'stim-type-item': "1", 'td-weights': 0.4, 'bu-weights': 0.6})
        preset.append({'stim-type-item': "2", 'td-weights': 0, 'bu-weights': 0})
    elif(presetType == "Single"):
        preset.append({'stim-type-item': "1", 'td-weights': 0.18, 'bu-weights': 0.15})
        preset.append({'stim-type-item': "2", 'td-weights': 0, 'bu-weights': 0})
    elif(presetType == "Same"):
        preset.append({'stim-type-item': "1", 'td-weights': 0.18, 'bu-weights': 0.15})
        preset.append({'stim-type-item': "2", 'td-weights': 0.18, 'bu-weights': 0.15})
    elif(presetType == "Diff"):
        preset.append({'stim-type-item': "1", 'td-weights': 0.18, 'bu-weights': 0.15})
        preset.append({'stim-type-item': "2", 'td-weights': 0.18, 'bu-weights': 0.15})
    elif(presetType == "MidTLateralD"):
        preset.append({'stim-type-item': "1", 'td-weights': 0.4, 'bu-weights': 0.15})
        preset.append({'stim-type-item': "2", 'td-weights': 0.18, 'bu-weights': 0.17})
    elif(presetType == "EimerGrubert"):
        preset.append({'stim-type-item': "1", 'td-weights': 0.7, 'bu-weights': 0.6})
        preset.append({'stim-type-item': "2", 'td-weights': 0.7, 'bu-weights': 0.6})
    return preset

@app.callback(Output('vis-objs-table','data'),
    [Input('stim-types-table', 'data_previous')],
    [
        State('stim-types-table', 'data'),
        State('vis-objs-table','data')
    ]
)
def deleteStimulus(previous, current, vos):
    if previous is None:
        raise PreventUpdate 
    else:
        removedStim = [row["stim-type-item"] for row in previous if row not in current]
        i=0
        while (i < len(vos)):
            if(vos[i]['vis-objs-item']==removedStim[0]):
                vos.pop(i)
                break
            i+=1
        # for i in range(len(vos)):
        #     if(vos[i]['vis-objs-item']==removedStim[0]):
        #         vos.pop(i)
        #         break
        return vos

@app.callback(
    Output('exp-total-time','value'),
    [
        Input('preset-experiment-choice','value'),
    ],
)
def setPresetRuntime(preset):
    if (preset!=""):
        time = 0
        if(preset):
            time=600
        return time

@app.callback(
    Output('vis-obj-stim-type','options'),
    Output('stim-type-dropdown','options'),
    [
        Input('stim-types-table','data')
    ]
)
def updateStimulusTypeDropDown(rows):
    opts = [row['stim-type-item'] for row in rows]
    return opts, opts
    #To remove visual objects on removing a stimulus type -> Callback output VO table data. Loop through the rows, remove the row with an unknown name.
    #At the moment this is a rather... slow implementation

@app.callback(
    ServersideOutput("original-store", "data"), ServersideOutput("sim-store", "data"), EnrichedOutput("run-sim-alert", "is_open"), EnrichedOutput("run-sim-alert", "children"), EnrichedOutput('stim-type-dropdown','value'), EnrichedOutput("results-visual", "style"),
    [
        Input('run-sim','n_clicks'), Input("save-exp","n_clicks"),
    ],
    [
        State('stim-types-table','data'),
        State('vis-objs-table','data'),
        State('exp-total-time','value'),
        State('exp-name','value'),
        State("run-sim-alert", "is_open"),
        State("sim-store", "data"),
        State("original-store", "data"),
    ],
    memoize=True
)
def simulationOperations(clicks, saveClick, sts, vos, runtime, expName, isOpen, data, ogData):
    #ragnaroc.Ragnaroc3C(x, y, Type1BottomUp, Type2BottomUp, Type3BottomUp, Type1TopDown, Type2TopDown, Type3TopDown,latency, duration, Stype,steps,videoinput)
    inputId = ""
    ctx = callback_context
    data = data or {}
    ogData = ogData or {}

    if ctx.triggered:
        inputId = ctx.triggered[0]['prop_id'].split('.')[0]
        if(expName == ""):
            # Experiment name Alert
            return ogData, data, True, "Please set experiment name", None, {"display": "none"}

    if(inputId == "run-sim"):
        if(len(sts) == 0):
            # Stimulus types alert
            return ogData, data, True,"Please add stimulus types to the experiment", None, {"display": "none"}
        
        if(len(vos) == 0):
            # Visual Objects Alert
            return ogData, data, True,"Please add visual objects to the experiment", None, {"display": "none"}

        if(runtime == "" or runtime == None):
            # Set runtime Alert
            return ogData, data, True, "Please set runtime of experiment", None, {"display": "none"}

        #Validated. 
        nameStore = {}

        #Setup variables to pass to the model
        x = np.zeros(len(vos)).astype(int)
        y = np.zeros(len(vos)).astype(int)
        Stype = np.zeros(len(vos)).astype(int)
        latency = np.zeros(len(vos)).astype(int)
        duration = np.zeros(len(vos)).astype(int)
        sts_len = len(sts) 
        while (sts_len < 3):
            sts.append({'stim-type-item': str(sts_len+1), 'td-weights': 0, 'bu-weights': 0})
            sts_len += 1
        t1_bu = sts[0]['bu-weights']
        t2_bu = sts[1]['bu-weights']
        t3_bu = sts[2]['bu-weights']

        t1_td = sts[0]['td-weights']
        t2_td = sts[1]['td-weights']
        t3_td = sts[2]['td-weights']
        
        for i in range(len(sts)):
            nameStore[sts[i]['stim-type-item']] = (i+1) 

        for i in range(len(vos)):
            x[i] = vos[i]['vis-objs-item-X']
            y[i] = vos[i]['vis-objs-item-Y']
            duration[i] = vos[i]['vis-objs-item-duration']
            latency[i] = vos[i]['vis-objs-item-latency']
            #Stype[i] = vos[i]['vis-objs-item-stim-type']
            Stype[i] = nameStore[vos[i]['vis-objs-item-stim-type']]

        steps=int(runtime)
        videoinput=np.zeros((27,27,1)).astype(float) 

        # x=np.zeros(1).astype(int)
        # y=np.zeros(1).astype(int)
        # Stype=np.zeros(1).astype(int)
        # latency=np.zeros(1).astype(int)
        # duration=np.zeros(1).astype(int)
        # x[0] = 7
        # y[0]  = 14
        # latency[0] = 0
        # Stype[0] = 1
        # duration[0]=100 
        # t1_bu = 0.6
        # t2_bu = 0
        # t1_td = 0.4
        # t2_td = 0
        # t3_bu = 0
        # t3_td = 0

        
        data = {}
        # data["EV1"], data["EV2"], data["LV1"], data["LV2"], data["IG"], data["AM"], data["II1"], data["II2"], data["N2pc"],  = ragnaroc.Ragnaroc3C(x, y, t1_bu, t2_bu, t3_bu, t1_td, t2_td, t2_td,latency, duration, Stype,steps,videoinput)
        # data["EV" + str(sts[0]['stim-type-item'])], data["EV" + str(sts[1]['stim-type-item'])], data["LV" + str(sts[0]['stim-type-item'])], data["LV" + str(sts[1]['stim-type-item'])], data["IG"], data["AM"], data["II" + str(sts[0]['stim-type-item'])], data["II" + str(sts[1]['stim-type-item'])], data["N2pc"],  = ragnaroc.Ragnaroc3C(x, y, t1_bu, t2_bu, t3_bu, t1_td, t2_td, t2_td,latency, duration, Stype,steps,videoinput)

        
        # data = {}
        ogData = {}
        ogData["EV" + str(sts[0]['stim-type-item'])], ogData["EV" + str(sts[1]['stim-type-item'])], ogData["LV" + str(sts[0]['stim-type-item'])], ogData["LV" + str(sts[1]['stim-type-item'])], ogData["IG"], ogData["AM"], ogData["II" + str(sts[0]['stim-type-item'])], ogData["II" + str(sts[1]['stim-type-item'])], ogData["N2pc"],  = ragnaroc.Ragnaroc3C(x, y, t1_bu, t2_bu, t3_bu, t1_td, t2_td, t3_td,latency, duration, Stype,steps,videoinput)


        # print(ogData["IG"])
        print(ogData["IG"].max())
        print(len(np.unique(ogData["IG"])))
        #Normalize the data to the uint8 range (0-255)
        # EE = 30, EI = -10
        payload = 0
        
        #for map in data.keys():
        for map in ogData.keys():
            data[map] = (ogData[map] + 10) * (255/40)
            data[map] = data[map].astype(np.uint8)
            payload += sys.getsizeof(data[map])
        
        print("Total simulation data: {} Bytes".format(payload))

        ogData["runtime"]=steps
        data["runtime"]=steps
        #saveResults(EV1,EV2,LV1,LV2,IG,AM,II1,II2,N2pc)

        return ogData, data, False, "", sts[0]['stim-type-item'] , {'display':'flex'}
    
    elif (inputId == "save-exp"):
        saveExp(expName, runtime, sts, vos)    

    return {}, {}, isOpen, "", None, {"display": "none"}

@app.callback( 
    Output('surface-viz','figure'), 
    Trigger("sim-store", "modified_timestamp"),
    [
        Input('stim-type-dropdown', 'value'),
        Input('map-dropdown', 'value'),
    ],
    [
        State("sim-store", "data"),
        State('surface-viz','figure'), 
    ],
    prevent_initial_call=True,
)
def loadingGraph(stim, map, store, surfaceFig):
    if store is None or not store :
        print("Store: {}".format(store))
        raise PreventUpdate 
    
    print("Loading Graph")
    currTimePos = 0
    if store["runtime"] > 200 :
        currTimePos = 200 

    if('sliders' in surfaceFig['layout']):
        currTimePos = surfaceFig['layout']['sliders'][0]['active']
    
    # Stim only applies to EV, LV and II
    if map == "AM" or map == "IG":
        stim = ""

    try:
        stim = str(stim)
        # print(map+stim)
        fig = {
            'data': [go.Surface(z=store[map+stim][:,:,currTimePos], colorscale="Hot", showscale=False, name=map+stim)],
            'layout': getSurfaceGraphLayout(currTimePos, store["runtime"]),
            'frames': [
                go.Frame(
                    data=[go.Surface(z=store[map+stim][:,:,k], colorscale="Hot", showscale=False, name=map+stim)], name=str(k))
                    for k in range(0,store["runtime"])
            ],
        }

        
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)

    # print("Figure payload: {} Bytes".format(sys.getsizeof(fig)))
    # print("Figure data payload: {} Bytes".format(sys.getsizeof(fig["data"])))
    # print("Figure frames payload: {} Bytes".format(sys.getsizeof(fig["frames"])))
    return fig

@app.callback( 
    Output('line-viz','figure'),
    [
        Input('surface-viz', 'clickData'),
        Input('stim-type-dropdown', 'value'),
        Input('lineplot-time', 'value'),
    ],
    [
        #State("sim-store", "data"),
        State("original-store", "data"),
    ],
    prevent_initial_call=True,
)
def updateLineGraphs(clickData, stim, timePoint, store):

    # The line charts are dependant on click and stimulus type

    # Store is 27 * 27 * 600
    # The line chart should show activations at x,y over 600 time steps
    # In plot, X axis is time, Y axis is the activations ([13][13])
    if store is None or not store :
        print("Original Store: {}".format(store))
        raise PreventUpdate 

    print("Loading line graphs")

    try:
        runtime = store["runtime"]
        timeline = np.arange(0,runtime+1,1)
        # print("Checking timeline {}".format(timeline[-1]))
        xPos = 13
        yPos = 13
        if clickData:
            xPos = clickData['points'][0]['x']
            yPos = clickData['points'][0]['y']

        #figs = {'data':[]}
        # figs = go.Figure(data=[])

        figs = make_subplots(rows=6, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.02)
        figCount=1

        figs.add_trace(
                go.Scatter(x=timeline, y=store["N2pc"], mode='lines', name="EEG"), row=figCount, col=1,
            )
        figs.update_xaxes(showgrid=False, showticklabels=False, row=figCount, col=1) #fixedrange=True
        figs.update_yaxes(showgrid=False, showticklabels=False, range=[-10,40], row=figCount, col=1)

        if timePoint:
            figs.add_vline( x=timePoint, line_width=3, line_dash="dash", line_color="#fccd61", row=figCount, col=1)
        
        figCount+=1

        for k in ["IG","AM"]:
            figs.add_trace(
                go.Scatter(x=timeline, y=store[k][yPos,xPos,:], mode='lines', name=k), row=figCount, col=1,
            )
            figs.update_xaxes(showgrid=False, showticklabels=False, row=figCount, col=1) #fixedrange=True
            figs.update_yaxes(showgrid=False, showticklabels=False, range=[-10,40], row=figCount, col=1)
            figs.add_hline(y=0, line_color="lightgray",) # , opacity=0.2,  line_dash="dash", line_color="lightgray",
            if timePoint:
                figs.add_vline( x=timePoint, line_width=3, line_dash="dash", line_color="#fccd61", row=figCount, col=1)

            figCount +=1
        
        if stim != "":
            for k in ["II","LV","EV"]:
                stim = str(stim)
                figs.add_trace(
                    go.Scatter(x=timeline, y=store[k+stim][yPos,xPos,:], mode='lines', name=k+" "+stim), row=figCount, col=1,
                )
                figs.update_xaxes(showgrid=False, showticklabels=False, row=figCount, col=1)
                figs.update_yaxes(showgrid=False, showticklabels=False, range=[-10,40], row=figCount, col=1)
                figs.add_hline(y=0, line_color="lightgray", opacity=0.2) # line_color="lightgray", line_dash="dash",
                if timePoint:
                    figs.add_vline( x=timePoint, line_width=3, line_dash="dash", line_color="#fccd61", row=figCount, col=1)
                figCount +=1

        figs.update_yaxes(title="Activation", row=4, col=1)
        figs.update_xaxes(title="Time", showticklabels=True, range=[0,runtime], row=6, col=1)
        figs.update_layout(template= "plotly_dark", title = "Time course at X : {}, Y : {}".format(xPos, yPos)) # "plotly", "plotly_white", "plotly_dark", "ggplot2", "seaborn", "simple_white", "none", "plotly_dark"
            
        
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)

    return figs

@app.callback(
    Output("result-modal", "is_open"),
    [Input("result-info", "n_clicks")],
    [State("result-modal", "is_open")],
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open


"""
@app.callback( 
    Output('surface-viz','figure'), 
    [
        Input("sim-store", "modified_timestamp"),
    ],
    [
        State("sim-store", "data")
    ],
    prevent_initial_call=True,
)
def loadingGraph(ts, store):
    print("Loading Graph")
    if store is None or not store :
        print("Store: {}".format(store))
        raise PreventUpdate 
    
    print("Laid out")
    print(type(store["IG"]))
    
    try:
        fig = {
                'data': [go.Surface(z=store["IG"][:,:,200], colorscale="Hot", showscale=False, name='IG')],
                'layout': getSurfaceGraphLayout(),
                'frames': [
                    go.Frame(
                        data=[go.Surface(z=store["IG"][:,:,k], colorscale="Hot", showscale=False, name='IG')], name=str(k))
                        for k in range(0,600)
                ],
            }
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)

    print("Figure payload: {} Bytes".format(sys.getsizeof(fig)))
    print("Figure data payload: {} Bytes".format(sys.getsizeof(fig["data"])))
    print("Figure frames payload: {} Bytes".format(sys.getsizeof(fig["frames"])))
    return fig
"""

app.clientside_callback(
    """
    function(style, elemid) {
        const isEmpty = Object.keys(style).length === 0;
        if(! isEmpty){
            document.getElementById(elemid).scrollIntoView({
                behavior: 'smooth'
            });
        }
    }
    """,
    Output('garbage-output-0', 'children'),
    #[Input("sim-store", "modified_timestamp")],
    [Input("results-visual", "style")],
    [State('surface-viz', 'id')]
)

# [Input('surface-viz', 'figure')], - Great, but delayed
# [Input("sim-store", "modified_timestamp")], - would work? # could work, or take input as loading state 
# Show loading, once store is set, scroll down, the graph is loading anyways


"""
    Output('garbage-output-0', 'children'),
    [Input('surface-viz', 'figure')],
    [State('surface-viz', 'id')]
-
    Output('garbage-output-0', 'children'),
    [Input("sim-store", "modified_timestamp")],
    [State('surface-viz', 'id')]

^Maybe delay by a second

    Output('garbage-output-0', 'children'),
    [Input("sim-store", "modified_timestamp")],
    [State('results-visual', 'id')]

- Garbage div approach
    Output('garbage-output-0', 'children'),
    [Input("sim-store", "modified_timestamp")],
    [State('garbage-output-1', 'id')]



"""

def saveResults(EV1,EV2,LV1,LV2,IG,AM,II1,II2,N2pc):
    #np.save('EV1',EV1)
    np.save(os.path.join(os.getcwd(), 'data', 'EV1.npy'),EV1)
    np.save('./data/EV2',EV2)
    np.save('./data/LV1',LV1)
    np.save('./data/LV2',LV2)
    np.save('./data/IG',IG)
    np.save('./data/AM',AM)
    np.save('./data/II1',II1)
    np.save('./data/II2',II2)
    np.save('./data/N2pc',N2pc)

def saveExp(expName, runtime, stimTypes, visObjs):
    #Use pickle library
    path = os.path.join(os.getcwd(), 'data', expName)
    os.mkdir(path)
    
    with open(os.path.join(path, 'stimulusTypes.pkl'), 'wb') as f:
        pickle.dump(stimTypes, f)
        
    with open(os.path.join(path, 'visualObjects.pkl'), 'wb') as f:
        pickle.dump(visObjs, f)
        
    with open(os.path.join(path, 'runtime.pkl'), 'wb') as f:
        pickle.dump(runtime, f)


app.layout = serve_layout
application = app.server

if __name__ == '__main__':
    # app.run_server()
    app.run_server(debug=True)
    # app.run_server(debug=True,port=8080)
    # application.run_server(debug=True,port=8080)