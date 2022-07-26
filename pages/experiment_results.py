from dash import dcc, html
import plotly.graph_objects as go
import dash_bootstrap_components as dbc

def experimentResults():
    return html.Div(
        id="results-visual",
        style = {"display": "none", },
        children=[
            resultsBanner(),
            resultsHelpModal(),
            resultsOptions(),
            resultsGraphs(),
        ],
    )

def resultsBanner():
    return html.Div(
        children=[
            html.H1('Results ', style={"color": "White", "fontFamily": "Norse", "margin":"3rem", "font-size":"3rem"}), #Playfair Display, serif | Norse
            html.H1(' ? ', id="result-info", style={"fontFamily": "Playfair Display, serif", "margin":"3rem", "paddingRight":"2rem"}),
        ],
        style={
            "display":"flex",
            "justifyContent":"space-between"
        },
    )

def resultsHelpModal():
    return dbc.Modal(
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
                    html.P("The surface plot display activations of the chosen map, across time. The values of the surface plot are normalized (0,256)."),
                    html.P("The line plot display activations of the chosen map, at the clicked point on the surface plot"),
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
    )

def resultsOptions():
    return html.Div(
        className="row result-options", 
        children=[
            html.Div(
                className='result-option-map', 
                children=[
                    html.Div(
                        className="result-options-text",
                        children=[
                            html.P("Select map", style={"fontSize": "large", "marginTop": "4px"}),
                        ], 
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
                        style={"width":'40%', },
                    ),
                ],
            ),

            html.Div(
                className='result-option-stim', 
                children=[
                    html.Div(
                        className="result-options-text",
                        children=[
                            html.P("Select stimulus", style={"fontSize": "large", "marginTop": "4px"}),
                        ], 
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
            ),
        ], 
    )

def resultsGraphs():
    return html.Div(
        className="row result-graphs-div", 
        children=[
            html.Div(
                children=[
                    dcc.Loading(
                        [
                            dcc.Graph(id="surface-viz", 
                                figure={
                                    "layout": go.Layout(width=700, height=600, margin=dict(r=35, l=35, b=30, t=30), template= "plotly_dark",),
                                },
                                className="surface-plot-spacing",
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
                                className="line-plot-spacing",
                            ),
                            html.Div(
                                className="result-time-div",
                                children = [
                                    html.P(
                                        "Time Marker", 
                                        className="result-time-text",
                                    ),
                                    dbc.Input(
                                        id="lineplot-time", placeholder="ms", type="number", min=0, max=600, debounce=True, className="hideNumScroll result-time-inp",
                                    ),
                                ],
                            ),
                        ],
                        type="circle", # cube, default, circle
                        color="#fccd61",
                    ),
                ],
                style={"margin":"16px", "display":"flex"}
            ),
            
        ], 
    )