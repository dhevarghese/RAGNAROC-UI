"""
    AUTHOR: DHEERAJ V
"""

import sys
import numpy as np

from dash import dcc, html, dash_table, callback_context
from plotly.subplots import make_subplots
from dash_extensions.enrich import Dash, Output, Input, State, ServersideOutput, Trigger, EnrichedOutput

import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

import ragnaroc
from pages import experiment, index

import boto3
from boto3.dynamodb.conditions import Key, Attr
import uuid
import json
from decimal import Decimal

external_stylesheets = [dbc.themes.BOOTSTRAP,
                        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css'
                       ]

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=external_stylesheets, prevent_initial_callbacks=True, update_title=None, assets_folder ="static", assets_url_path="static")
app.title='Ragnaroc'
application = app.server

# Ideally, all callbacks should be in a separate file or in a file with the appropriate element. But, as we require the app variable (Due to the use of Dash-extensions, to 
# save variables), I've defined all over here.

client = boto3.client(
    'dynamodb',
    aws_access_key_id='REMOVED-AWS-ACCESS-KEY-ID',
    aws_secret_access_key='REMOVED-AWS-SECRET-KEY',
    region_name="us-east-1",
    )
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id='REMOVED-AWS-ACCESS-KEY-ID',
    aws_secret_access_key='REMOVED-AWS-SECRET-KEY',
    region_name="us-east-1",
    )
ddb_exceptions = client.exceptions


## Workaround for multi-page Dash app 
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/':
        return index.serve_layout(app)
    elif pathname == '/ragnaroc':
        return experiment.serve_layout(app)
    else:
        return '404'

## Callbacks for the entire application

@app.callback(Output('stim-table', 'style'), Output('vo-table', 'style'),
              Input('exp-form-tabs', 'value'))
def render_content(tab):
    """ Update style depending on selected tab."""
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
    EnrichedOutput('vis-objs-table','data'), EnrichedOutput("vo-alert", "is_open"), EnrichedOutput("vo-dup-alert", "is_open"), EnrichedOutput("results-visual", "style"), 
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
    ],
)
def addVisualObject(n_clicks, preset, rows, name, x, y, duration, latency, stimType, isOpen):
    """ Add visual object details to the data table. The details are added by provided input or preset. If invalid data is provided, the user is alerted"""
    ctx = callback_context
    openAlert = False
    duplicateObj = False

    inputId = ""
    if ctx.triggered:
        inputId = ctx.triggered[0]['prop_id'].split('.')[0]

    if(inputId == "vis-obj-add"):
        if n_clicks == 0:
            raise PreventUpdate
        
        validated = True
        if ((x==None) or (y==None) or (duration==None) or (latency==None) or (stimType=="") or (name=="")) :
            validated = False

        openAlert = not validated

        for i in range(len(rows)):
            if(rows[i]["name"] == name):
                duplicateObj = True
                break
        
        if(n_clicks>0 and validated and not duplicateObj):
            rows.append({'name': name, 'X': x, 'Y': y, 'duration': duration, 'latency': latency, 'stimulus': stimType})

    elif (inputId == "preset-experiment-choice" and preset != None):
        presetType = ctx.triggered[0]['value'].split('.')[0]
        rows = getVisualObjectPreset(presetType)

    elif (inputId == "input-alerts"):
        openAlert = isOpen
    
    return rows, openAlert, duplicateObj, {"display": "none"}

def getVisualObjectPreset(presetType):
    """ Helper function to load Visual Objects for preset trials. """
    preset = []
    if(presetType == "Brisson"):
        preset.append({'name': "1", 'X': 7, 'Y': 14, 'duration': 100, 'latency': 0, 'stimulus': "1"})
    elif(presetType == "Single"):
        preset.append({'name': "1", 'X': 7, 'Y': 14, 'duration': 500, 'latency': 0, 'stimulus': "1"})
    elif(presetType == "Same"):
        preset.append({'name': "1", 'X': 7, 'Y': 14, 'duration': 120, 'latency': 0, 'stimulus': "1"})
        preset.append({'name': "2", 'X': 7, 'Y': 14, 'duration': 120, 'latency': 120, 'stimulus': "2"})
    elif(presetType == "Diff"):
        preset.append({'name': "1", 'X': 7, 'Y': 14, 'duration': 120, 'latency': 0, 'stimulus': "1"})
        preset.append({'name': "2", 'X': 21, 'Y': 14, 'duration': 120, 'latency': 120, 'stimulus': "2"})
    elif(presetType == "MidTLateralD"):
        preset.append({'name': "1", 'X': 14, 'Y': 7, 'duration': 500, 'latency': 0, 'stimulus': "1"})
        preset.append({'name': "2", 'X': 7, 'Y': 14, 'duration': 500, 'latency': 0, 'stimulus': "2"})
    elif(presetType == "EimerGrubert"):
        preset.append({'name': "1", 'X': 10, 'Y': 10, 'duration': 40, 'latency': 0, 'stimulus': "1"})
        preset.append({'name': "2", 'X': 10, 'Y': 18, 'duration': 40, 'latency': 10, 'stimulus': "2"})
    return preset

@app.callback(
    Output("text-td-weight", "value"),
    Output("top-down", "value"),
    Input("text-td-weight", "value"),
    Input("top-down", "value"),
)
def tdUpdate(input_value, slider_value):
    """ Simultaneously update the text/slider for top-down weights. """
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
def buUpdate(input_value, slider_value):
    """ Simultaneously update the text/slider for bottom-up weights. """
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
    [State('stim-types-table','data'), State('stim-type-name','value'), State('top-down','value'), State('bottom-up','value'), State("stim-alert", "is_open"), State("stim-count-alert","is_open")],
    prevent_initial_call=True,
)
def addStimulusType(n_clicks, preset, rows, name, tdWeight, buWeight, isOpen, maxStimuliReached):
    """ Add Stimulus Type details to the data table. The details are added by provided input or preset. If invalid data is provided, the user is alerted"""

    ctx = callback_context
    openAlert = False
    maxStimuliReached = False
    duplicateStimulus = False

    inputId = ""
    if ctx.triggered:
        inputId = ctx.triggered[0]['prop_id'].split('.')[0]

    if(inputId == "add-stim-type"):  
        if n_clicks == 0:
            raise PreventUpdate
        
        openAlert = (name=="") or (tdWeight > 1) or (tdWeight < 0) or (buWeight > 1) or (buWeight < 0) 

        for i in range(len(rows)):
            if(rows[i]["stimName"] == name):
                duplicateStimulus = True
                break

        if(n_clicks>0 and not openAlert and not duplicateStimulus):
            rows.append({'stimName': name, 'td': tdWeight, 'bu': buWeight})

    elif (inputId == "preset-experiment-choice" and preset != None):
        presetType = ctx.triggered[0]['value'].split('.')[0]
        rows = getStimulusTypesPreset(presetType)

    elif (inputId == "input-alerts"):
        openAlert = isOpen

    return rows, openAlert, maxStimuliReached, duplicateStimulus #, style

def getStimulusTypesPreset(presetType):
    """ Helper function to load Stimulus Types for preset trials. """
    preset = []
    if(presetType == "Brisson"):
        preset.append({'stimName': "1", 'td': 0.4, 'bu': 0.6})
        preset.append({'stimName': "2", 'td': 0, 'bu': 0})
    elif(presetType == "Single"):
        preset.append({'stimName': "1", 'td': 0.18, 'bu': 0.15})
        preset.append({'stimName': "2", 'td': 0, 'bu': 0})
    elif(presetType == "Same"):
        preset.append({'stimName': "1", 'td': 0.18, 'bu': 0.15})
        preset.append({'stimName': "2", 'td': 0.18, 'bu': 0.15})
    elif(presetType == "Diff"):
        preset.append({'stimName': "1", 'td': 0.18, 'bu': 0.15})
        preset.append({'stimName': "2", 'td': 0.18, 'bu': 0.15})
    elif(presetType == "MidTLateralD"):
        preset.append({'stimName': "1", 'td': 0.4, 'bu': 0.15})
        preset.append({'stimName': "2", 'td': 0.18, 'bu': 0.17})
    elif(presetType == "EimerGrubert"):
        preset.append({'stimName': "1", 'td': 0.7, 'bu': 0.6})
        preset.append({'stimName': "2", 'td': 0.7, 'bu': 0.6})
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
        removedStim = [row["stimName"] for row in previous if row not in current]
        i=0
        while (i < len(vos)):
            if(vos[i]['name']==removedStim[0]):
                vos.pop(i)
                break
            i+=1
        return vos

@app.callback(
    Output('exp-total-time','value'),
    [
        Input('preset-experiment-choice','value'),
    ],
)
def setPresetRuntime(preset):
    """ All preset trials run for 600 ms. """
    if (preset!=""):
        time = 0
        if(preset):
            time=600
        return time
    else:
        raise PreventUpdate 

@app.callback(
    Output('vis-obj-stim-type','options'),
    Output('stim-type-dropdown','options'),
    [
        Input('stim-types-table','data')
    ]
)
def updateStimulusTypeDropdown(rows):
    """ Callback to include user defined stimuli in the dropdown. """
    opts = [row['stimName'] for row in rows]
    return opts, opts

@app.callback(
    ServersideOutput("original-store", "data"), 
    ServersideOutput("sim-store", "data"), 
    EnrichedOutput("run-sim-alert", "is_open"), 
    EnrichedOutput("run-sim-alert", "children"), 
    EnrichedOutput('stim-type-dropdown','value'), 
    EnrichedOutput("results-visual", "style"), 
    EnrichedOutput("save-alert", "is_open"),
    EnrichedOutput("rewrite-modal", "is_open"),	
    [
        Input('run-sim','n_clicks'),  Input("save-creator-exp","n_clicks"), Input("rewrite-accept","n_clicks"), Input("rewrite-deny", "n_clicks"),
    ],
    [
        State('stim-types-table','data'),
        State('vis-objs-table','data'),
        State('exp-total-time','value'),
        State('exp-name','value'),
        State("run-sim-alert", "is_open"),
        State("sim-store", "data"),
        State("original-store", "data"),
        State("exp-creator-name", "value"),	
        State("save-alert", "is_open"),
    ],
    prevent_initial_call=True,
    # memoize=True #Commenting as memoizing causes errors when cron job executes.
)
def simulationOperations(clicks, saveClick, rewriteClick, rewriteDeny, sts, vos, runtime, expName, isOpen, data, ogData, creator, openSavedAlert):
    """ This callback performs input validation and calls the ragnaroc model. This is the core of the system. 
        
        Input: Stimulus Types, Visual Objects, runtime, name, run alert, data stores (sim & original), creator name, save alert.
        Output: Original store, sim store, run alert (flag & children), -, results css, save alert

        This callback also handles the save alert.
    
    """
    
    inputId = ""
    ctx = callback_context
    data = data or {}
    ogData = ogData or {}
    openSavedAlert = False
    openRewrite = False

    if(clicks == None and saveClick == None and rewriteClick == None and rewriteDeny == None):
        return ogData, data, False, "", None, {"display": "none"}, openSavedAlert, openRewrite

    if ctx.triggered:
        inputId = ctx.triggered[0]['prop_id'].split('.')[0]
        if(expName == "" or expName == None):
            # Experiment name Alert
            return ogData, data, True, "Please set experiment name", None, {"display": "none"}, openSavedAlert, openRewrite

        elif(len(sts) == 0):
            # Stimulus types alert
            return ogData, data, True,"Please add stimulus types to the experiment", None, {"display": "none"}, openSavedAlert, openRewrite
        
        elif(len(vos) == 0):
            # Visual Objects Alert
            return ogData, data, True,"Please add visual objects to the experiment", None, {"display": "none"}, openSavedAlert, openRewrite

        elif(runtime == "" or runtime == None or int(runtime) < 1):
            # Set runtime Alert
            return ogData, data, True, "Please set an appropriate runtime for the experiment", None, {"display": "none"}, openSavedAlert, openRewrite

        #Validated. 

        if(inputId == "run-sim"):
            steps = int(runtime)
            videoinput = np.zeros((27,27,1)).astype(float) 

            
            data = {}
            ogData = {}

            ogData["EV"], ogData["LV"], ogData["IG"], ogData["AM"], ogData["II"], ogData["N2pc"], ogData["stimMap"]  = ragnaroc.runTrial(vos, sts, steps, videoinput)

            #Normalize the data to the uint8 range (0-255)
            # EE = 30, EI = -10
            payload = 0
            for map in ogData.keys():
                if (map != "stimMap"):
                    data[map] = (ogData[map] + 10) * (255/40)
                    data[map] = data[map].astype(np.uint8)
                    payload += sys.getsizeof(data[map])
            
            print("Total simulation data: {} Bytes".format(payload))

            ogData["runtime"] = steps
            data["runtime"] = steps
            data['stimMap'] = ogData['stimMap']

            return ogData, data, False, "", sts[0]['stimName'] , {'display':'flex'}, openSavedAlert, openRewrite
        
        elif (inputId == "save-creator-exp" and creator != "" and (creator is not None)):	
            # Open Modal to enter creator name. Once entered, add to Database. 
            saved = saveExp(creator, expName, runtime, sts, vos, False)  
            if(saved):
                openSavedAlert = True
            else:
                openRewrite = True
        
        elif (inputId == "rewrite-accept"):	 
            openSavedAlert = saveExp(creator, expName, runtime, sts, vos, True)  	
        
        elif (inputId == "rewrite-deny"):	 
            return ogData, data, False, "", None, {"display": "none"}, openSavedAlert, False
        	
    return {}, {}, isOpen, "", None, {"display": "none"}, openSavedAlert, openRewrite

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
    """ This callback sets up the data required for the surface plots. 
        
        Input: Stimulus drop down value, map drop down value, simulated store, surface figure
        Output: Updated surface figure.

        Fig consists of data, layout and frames. The frames are required to animate through the neural activations.
    """
    if store is None or not store :
        print("Store: {}".format(store))
        raise PreventUpdate 
    
    if map is None or stim is None:
        raise PreventUpdate 
    
    print("Loading Graph with {} map".format(map))
    
    # Set the time point of the animation
    currTimePos = 0
    if store["runtime"] > 200 :
        currTimePos = 200 

    fig={}

    try:
        if('sliders' in surfaceFig['layout']):
            currTimePos = surfaceFig['layout']['sliders'][0]['active']
                
        stim = str(stim)
        # Stim only applies to EV, LV and II
        if(map == "AM" or map == "IG"):
            fig = {
                'data': [go.Surface(z=store[map][currTimePos, :,:], colorscale="Hot", showscale=False, name=map+stim)],
                'layout': getSurfaceGraphLayout(currTimePos, store["runtime"]),
                'frames': [
                    go.Frame(
                        data=[go.Surface(z=store[map][k,:,:], colorscale="Hot", showscale=False, name=map+stim)], name=str(k))
                        for k in range(0,store["runtime"])
                ],
            }
        else:
            fig = {
                'data': [go.Surface(z=store[map][store["stimMap"][stim],currTimePos, :,:], colorscale="Hot", showscale=False, name=map+stim)],
                'layout': getSurfaceGraphLayout(currTimePos, store["runtime"]),
                'frames': [
                    go.Frame(
                        data=[go.Surface(z=store[map][store["stimMap"][stim], k,:,:], colorscale="Hot", showscale=False, name=map+stim)], name=str(k))
                        for k in range(0,store["runtime"])
                ],
            }
        
    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        raise PreventUpdate 

    # print("Figure payload: {} Bytes".format(sys.getsizeof(fig)))
    return fig

def getSurfaceGraphLayout(currSliderVal=200, runtime=0):
    """ Function to set the layout of the surface plots. """
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
                        "args": [None, frame_args(1)], 
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

def frame_args(duration):
    # Parameters for the animation
    return {
            "frame": {"duration": duration},
            "mode": "immediate",
            "fromcurrent": True,
            "transition": {"duration": duration, "easing": "linear"},
        }

@app.callback( 
    Output('line-viz','figure'),
    [
        Input('surface-viz', 'clickData'),
        Input('stim-type-dropdown', 'value'),
        Input('lineplot-time', 'value'),
    ],
    [
        State("original-store", "data"),
    ],
    prevent_initial_call=True,
)
def updateLineGraphs(clickData, stim, timePoint, store):
    """ Callback to update the line graphs of all activation maps according to surface plot clicks, change in stimuli or time marker. 
        The line chart should show activations at x, y over 600 time steps. In plot, X axis is time, Y axis is the activations ([13][13]). 
        We make subplots to show all the activation maps in a single plot.
    """
    
    # The line charts are dependant on click and stimulus type
    # Store size is 600* 27 * 27 
    if store is None or not store:
        print("Original Store: {}".format(store))
        raise PreventUpdate 
    
    if stim is None:
        raise PreventUpdate 

    print("Loading line graphs")

    try:
        runtime = store["runtime"]
        timeline = np.arange(0, runtime+1, 1)
        
        xPos = 13
        yPos = 13
        if clickData:
            xPos = clickData['points'][0]['x']
            yPos = clickData['points'][0]['y']

        figs = make_subplots(rows=6, cols=1,
                    shared_xaxes=True,
                    vertical_spacing=0.02)
        figCount = 1

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
                go.Scatter(x=timeline, y=store[k][:, yPos,xPos], mode='lines', name=k), row=figCount, col=1,
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
                    go.Scatter(x=timeline, y=store[k][store["stimMap"][stim], :,yPos,xPos], mode='lines', name=k+" "+stim), row=figCount, col=1,
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
        raise PreventUpdate 

    return figs

@app.callback(
    Output("result-modal", "is_open"),
    [Input("result-info", "n_clicks")],
    [State("result-modal", "is_open")],
)
def toggle_modal(n1, is_open):
    """Simple callback to open the modal for info/help on the results screen. """
    if n1:
        return not is_open
    return is_open

@app.callback(	
    Output("creator-modal", "is_open"),	
    [Input("save-exp","n_clicks"), Input("save-creator-exp","n_clicks")],	
    [State("creator-modal", "is_open")],	
)	
def toggle_creator_modal(n1, n2, is_open):	
    """Callback to open the modal for saving the trial. """
    if n1 or n2:	
        return not is_open	
    return is_open	

@app.callback(	
    Output("load-exp-modal", "is_open"),	
    [Input("load-sim","n_clicks"),],	
    [State("load-exp-modal", "is_open")],	
)	
def toggle_load_modal(n1, is_open):	
    """Callback to open the modal for loading a trial. """
    if n1:	
        return not is_open	
    return is_open	

@app.callback(	
    Output("loaded-exps-dropdown", "options"),	
    [Input("load-exps-creator","value"),],	
    prevent_initial_call=True,
)	
def load_trial_names(creator):	
    """Callback to query dynamoDB for all the trial names saved by the creator and update the dropdown options. """
    print("Loading creators")
    if(creator and creator != ""):		
        response = dynamodb.Table('ragnaroc-trial-names').query(	
                KeyConditionExpression=Key('creator').eq(creator)	
            )
        return [{"label" : i["name"] , "value" : i["name"]} for i in response["Items"]]	
    else:
        raise PreventUpdate

@app.callback(	
    [	
        Output('stim-types-table','data'),	
        Output('vis-objs-table','data'),	
        Output('exp-total-time','value'),	
        Output('exp-name','value'),     	
        Output("load-exp-modal", "is_open"), 	
        Output("load-alert", "is_open"),
        Output("loaded-exps-dropdown", "value"),
        Output("load-exps-creator","value"),
        Output("results-visual", "style"), 
    ],	
    [Input("load-creator-exp","n_clicks"),],	
    [State("loaded-exps-dropdown","value"), State("load-exps-creator","value"),],	
)	
def load_trials(n1, name, creator):	
    """Callback to query dynamoDB for the trial selected by the user and update the data tables and other relevant information for the trial. """
    if n1 is None:
        raise PreventUpdate
    
    try:
        print("Loading experiments") 
        response = dynamodb.Table('ragnaroc-trials').query(	
                KeyConditionExpression=Key('name').eq(name) & Key('creator').eq(creator)
            )	
        if("stimName" in response["Items"][0]["stimulus-types"][0] and "name" in response["Items"][0]["visual-objects"][0]):
            return response["Items"][0]["stimulus-types"], response["Items"][0]["visual-objects"], response["Items"][0]["runtime"], response["Items"][0]["name"], False, False, None, None, {"display": "none"}
        else:
            return [], [], None, None, False, True, None, None, {"display": "none"}

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        print(message)
        return [], [], None, None, False, True, None, None, {"display": "none"}

"""Clientside callback to scroll down to the results when the simulation completes. """
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
    [Input("results-visual", "style")],
    [State('surface-viz', 'id')]
)

def saveExp(creator, expName, runtime, stimTypes, visObjs, rewrite):	
    """Function to call dynamoDB and insert new trials. """
    try:	
        # Check if experiment with same name exists
        response = dynamodb.Table('ragnaroc-trial-names').get_item(Key={'name':expName, 'creator':creator})	
        if("Item" in response and not rewrite):
            return False

        exp = {		
            "creator" : str(creator),	
            "name": str(expName),	
            "runtime": str(runtime),	
            "stimulus-types": json.loads(json.dumps(stimTypes), parse_float=Decimal),	
            "visual-objects" : json.loads(json.dumps(visObjs), parse_float=Decimal),	
        }	
        expName = {		
            "creator" : str(creator),	
            "name": str(expName),	
        }	
        # Add to DynamoDB	
        dynamodb.Table('ragnaroc-trials').put_item(Item=exp)	
        dynamodb.Table('ragnaroc-trial-names').put_item(Item=expName)	        
        print("Trial by {} added to dynamoDB".format(str(creator)))	
        return True	
        	
    except Exception as ex:	
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"	
        message = template.format(type(ex).__name__, ex.args)	
        print(message)	
        return False

if __name__ == '__main__':
    """The start point of the application. """
    # app.run_server()
    app.run_server(debug=True)
    # app.run_server(debug=True,port=8080)
    # application.run_server(debug=True,port=8080)