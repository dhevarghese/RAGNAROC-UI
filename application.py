"""
    AUTHOR: DHEERAJ V
"""

import logging
import os
import sys
import numpy as np

from dash import dcc, html, callback_context, no_update
from plotly.subplots import make_subplots
from dash_extensions.enrich import Dash, Output, Input, State, Serverside, Trigger

import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc

import ragnaroc
import storage
from pages import experiment, index

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ragnaroc")


def log_exc(context, ex):
    """Log a swallowed exception with enough detail to diagnose it."""
    logger.error(
        "An exception of type %s occurred while %s. Arguments: %r",
        type(ex).__name__, context, ex.args,
    )

external_stylesheets = [dbc.themes.BOOTSTRAP,
                        'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css'
                       ]

app = Dash(__name__, suppress_callback_exceptions=True, external_stylesheets=external_stylesheets, prevent_initial_callbacks=True, update_title=None, assets_folder ="static", assets_url_path="static")
app.title='Ragnaroc'
application = app.server

# Ideally, all callbacks should be in a separate file or in a file with the appropriate element. But, as we require the app variable (Due to the use of Dash-extensions, to 
# save variables), I've defined all over here.

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
        "marginTop": "2.5rem",
    }
    styleHide = {
        "display": "none",
        "marginTop": "2.5rem",
    }
    if tab == 'stim-form':
        return styleDisplay, styleHide
    elif tab == 'vo-form':
        return styleHide, styleDisplay

@app.callback(
    Output('vis-objs-table','data'), Output("vo-alert", "is_open"), Output("vo-dup-alert", "is_open"), Output("results-visual", "style"),
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
    ],
)
def addVisualObject(n_clicks, preset, rows, name, x, y, duration, latency, stimType):
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
    Output('stim-types-table','data'), Output("stim-alert", "is_open"), Output("stim-dup-alert","is_open"),  Output("results-visual", "style"),
    [
        Input('add-stim-type','n_clicks'),
        Input('preset-experiment-choice','value'),
    ],
    [State('stim-types-table','data'), State('stim-type-name','value'), State('top-down','value'), State('bottom-up','value')],
    prevent_initial_call=True,
)
def addStimulusType(n_clicks, preset, rows, name, tdWeight, buWeight):
    """ Add Stimulus Type details to the data table. The details are added by provided input or preset. If invalid data is provided, the user is alerted"""

    ctx = callback_context
    openAlert = False
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

    return rows, openAlert, duplicateStimulus, {"display": "none"}

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

@app.callback(Output('vis-obj-x-tooltip','children'), Output('vis-obj-y-tooltip','children'),
    Output('vis-obj-x','max'), Output('vis-obj-y','max'),
    [Input('canvas-size','value')],
)
def updateTooltip(canvas):
    """ Keep the X/Y input bounds and their tooltips in sync with the canvas size. """
    if not canvas or canvas < 1 or canvas > 50:
        return "Range: (1,27) ", "Range: (1,27) ", 27, 27
    hint = "Range: (1,{}) ".format(canvas)
    return hint, hint, canvas, canvas


@app.callback(
    Output('exp-total-time','value'),
    [
        Input('preset-experiment-choice','value'),
    ],
    prevent_initial_call=True,
)
def setPresetRuntime(preset):
    """ All preset trials run for 600 ms. """
    if (preset and preset!=""):
        return 600
    else:
        raise PreventUpdate 

@app.callback(
    Output('canvas-size','value'),
    Output('mask-size','value'),
    [
        Input('preset-experiment-choice','value'),
    ],
    prevent_initial_call=True,
)
def setPresetSimulationParameters(preset):
    """ All preset trials have a canvas size of 27x27 and mask of 3x3 """
    if (preset and preset!=""):
        return 27,3
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
    Output("original-store", "data"),
    Output("sim-store", "data"),
    Output("run-sim-alert", "is_open"),
    Output("run-sim-alert", "children"),
    Output('stim-type-dropdown','value'),
    Output("results-visual", "style"),
    Output("save-alert", "is_open"),
    Output("rewrite-modal", "is_open"),
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
        State('canvas-size','value'),
        State('mask-size','value'),

    ],
    prevent_initial_call=True,
    # memoize=True #Commenting as memoizing causes errors when cron job executes.
)
def simulationOperations(clicks, saveClick, rewriteClick, rewriteDeny, sts, vos, runtime, expName, isOpen, data, ogData, creator, openSavedAlert, canvas, mask):
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
        return no_update, no_update, False, "", None, {"display": "none"}, openSavedAlert, openRewrite

    if ctx.triggered:
        inputId = ctx.triggered[0]['prop_id'].split('.')[0]
        if(expName == "" or expName == None):
            # Experiment name Alert
            return no_update, no_update, True, "Please set experiment name", None, {"display": "none"}, openSavedAlert, openRewrite

        elif(len(sts) == 0):
            # Stimulus types alert
            return no_update, no_update, True,"Please add stimulus types to the experiment", None, {"display": "none"}, openSavedAlert, openRewrite
        
        elif(len(vos) == 0):
            # Visual Objects Alert
            return no_update, no_update, True,"Please add visual objects to the experiment", None, {"display": "none"}, openSavedAlert, openRewrite

        elif(runtime == "" or runtime == None or int(runtime) < 1):
            # Set runtime Alert
            return no_update, no_update, True, "Please set an appropriate runtime for the experiment", None, {"display": "none"}, openSavedAlert, openRewrite
        
        elif(canvas == "" or canvas == None or int(canvas) < 1 or int(canvas) > 50):
            # Set canvas Alert
            return no_update, no_update, True, "Please set an appropriate canvas size for the experiment", None, {"display": "none"}, openSavedAlert, openRewrite

        elif(mask == "" or mask == None or int(mask) < 1 or int(mask) > 10):
            # Set mask Alert
            return no_update, no_update, True, "Please set an appropriate mask size for the experiment", None, {"display": "none"}, openSavedAlert, openRewrite

        if(mask > canvas):
            # Set mask and canvas size Alert
            return no_update, no_update, True, "Mask cannot be larger than the canvas!", None, {"display": "none"}, openSavedAlert, openRewrite

        # Check if all vos and sts are within range
        try:
            stims = set()
            for item in sts:
                stims.add(item["stimName"])
                name,td,bu = item["stimName"], float(item["td"]), float(item["bu"])
                if(td > 1 or td < 0):
                    return no_update, no_update, True, "Please set an appropriate top-down value for stimulus {}".format(name), None, {"display": "none"}, openSavedAlert, openRewrite
                elif(bu>1 or bu<0):
                    return no_update, no_update, True, "Please set an appropriate bottom-up value for stimulus {}".format(name), None, {"display": "none"}, openSavedAlert, openRewrite
                # item["td"], item["bu"] = td, bu

            for item in vos:
                #name, x,y,duration,latency,stim = item["name"], int(item["X"]), int(item["Y"]), int(item["duration"]), int(item["latency"]), item["stimulus"]
                name, x,y,duration,latency,stim = item["name"], float(item["X"]), float(item["Y"]), float(item["duration"]), float(item["latency"]), item["stimulus"]
                if(stim not in stims):
                    # Invalid stimuli
                    return no_update, no_update, True, "Please ensure that all visual objects have an appropriate stimulus type", None, {"display": "none"}, openSavedAlert, openRewrite
                if(x>canvas or x<1):
                    return no_update, no_update, True, "Please set an appropriate x value for object {}".format(name), None, {"display": "none"}, openSavedAlert, openRewrite
                elif(y>canvas or y<1):
                    return no_update, no_update, True, "Please set an appropriate y value for object {}".format(name), None, {"display": "none"}, openSavedAlert, openRewrite
                elif(duration>1000 or duration< 0):
                    return no_update, no_update, True, "Please set an appropriate duration for object {}".format(name), None, {"display": "none"}, openSavedAlert, openRewrite
                elif(latency>1000 or latency<0):
                    return no_update, no_update, True, "Please set an appropriate latency for object {}".format(name), None, {"display": "none"}, openSavedAlert, openRewrite
                item["X"], item["Y"], item["duration"], item["latency"] = x, y, duration, latency

        
        except Exception as ex:
            log_exc("validating the experiment inputs", ex)
            return no_update, no_update, True, "An error occured...", None, {"display": "none"}, openSavedAlert, openRewrite

        # Validated. 

        if(inputId == "run-sim"):
            steps = int(runtime)
            videoinput = np.zeros((27,27,1)).astype(float) 

            
            data = {}
            ogData = {}

            ogData["EV"], ogData["LV"], ogData["IG"], ogData["AM"], ogData["II"], ogData["N2pc"], ogData["stimMap"]  = ragnaroc.runTrial(vos, sts, steps, videoinput, xDim=canvas, yDim=canvas, NNMask=mask)

            #Normalize the data to the uint8 range (0-255)
            # EE = 30, EI = -10
            payload = 0
            for mapName in ogData.keys():
                if (mapName != "stimMap"):
                    data[mapName] = (ogData[mapName] + 10) * (255/40)
                    data[mapName] = data[mapName].astype(np.uint8)
                    payload += sys.getsizeof(data[mapName])

            logger.info("Total simulation data: %s Bytes", payload)

            ogData["runtime"] = steps
            data["runtime"] = steps
            data['stimMap'] = ogData['stimMap']

            # Log run to storage
            try:
                storage.log_run(str(creator) if creator else "guest", str(expName))
            except Exception as ex:
                log_exc("logging run to storage", ex)

            return Serverside(ogData), Serverside(data), False, "", sts[0]['stimName'] , {'display':'flex'}, openSavedAlert, openRewrite

        elif (inputId == "save-creator-exp" and creator != "" and (creator is not None)):
            # Save the experiment; on a name collision ask before overwriting.
            try:
                if storage.trial_exists(creator, expName):
                    openRewrite = True
                else:
                    storage.save_trial(creator, expName, int(runtime), int(canvas), int(mask), sts, vos)
                    openSavedAlert = True
            except Exception as ex:
                log_exc("saving experiment", ex)
                return no_update, no_update, True, "Failed to save the experiment (storage error).", None, no_update, False, False

        elif (inputId == "rewrite-accept"):
            try:
                storage.save_trial(creator, expName, int(runtime), int(canvas), int(mask), sts, vos, overwrite=True)
                openSavedAlert = True
            except Exception as ex:
                log_exc("saving experiment", ex)
                return no_update, no_update, True, "Failed to save the experiment (storage error).", None, no_update, False, False

        elif (inputId == "rewrite-deny"):
            return no_update, no_update, False, "", None, no_update, openSavedAlert, False

    return no_update, no_update, isOpen, "", None, no_update, openSavedAlert, openRewrite

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
        State('canvas-size','value'),
    ],
    prevent_initial_call=True,
)
def loadingGraph(stim, mapName, store, surfaceFig, canvas):
    """ This callback sets up the data required for the surface plots.

        Input: Stimulus drop down value, map drop down value, simulated store, surface figure
        Output: Updated surface figure.

        Fig consists of data, layout and frames. The frames are required to animate through the neural activations.
    """
    if store is None or not store :
        logger.info("Store: %s", store)
        raise PreventUpdate

    if mapName is None or stim is None:
        raise PreventUpdate

    logger.info("Loading Graph with %s map", mapName)

    # Set the time point of the animation
    currTimePos = 0
    if store["runtime"] > 200 :
        currTimePos = 200

    fig={}

    try:
        if('sliders' in surfaceFig['layout']):
            currTimePos = surfaceFig['layout']['sliders'][0]['active']
        # The previous figure's slider may point past the end of a shorter re-run
        currTimePos = min(currTimePos, store["runtime"] - 1)

        stim = str(stim)
        # Stim only applies to EV, LV and II
        if(mapName == "AM" or mapName == "IG"):
            fig = {
                'data': [go.Surface(z=store[mapName][currTimePos, :,:], colorscale="Hot", showscale=False, name=mapName+stim)],
                'layout': getSurfaceGraphLayout(currTimePos, store["runtime"], canvas),
                'frames': [
                    go.Frame(
                        data=[go.Surface(z=store[mapName][k,:,:], colorscale="Hot", showscale=False, name=mapName+stim)], name=str(k))
                        for k in range(0,store["runtime"])
                ],
            }
        else:
            fig = {
                'data': [go.Surface(z=store[mapName][store["stimMap"][stim],currTimePos, :,:], colorscale="Hot", showscale=False, name=mapName+stim)],
                'layout': getSurfaceGraphLayout(currTimePos, store["runtime"], canvas),
                'frames': [
                    go.Frame(
                        data=[go.Surface(z=store[mapName][store["stimMap"][stim], k,:,:], colorscale="Hot", showscale=False, name=mapName+stim)], name=str(k))
                        for k in range(0,store["runtime"])
                ],
            }

    except Exception as ex:
        log_exc("loading surface plots", ex)
        raise PreventUpdate

    # print("Figure payload: {} Bytes".format(sys.getsizeof(fig)))
    return fig

def getSurfaceGraphLayout(currSliderVal=200, runtime=0, canvasSize=30):
    """ Function to set the layout of the surface plots. """
    return go.Layout(
        template= "plotly_dark",
        title = "Surface Plot",
        scene = dict
        (
            aspectratio=dict(x=1,y=1,z=1),
            xaxis = dict(title= dict(text = 'x', font = {"size" : 16}), range = [0,canvasSize+3], tickfont = dict(size=14),), #Modify the axes
            yaxis = dict(title= dict(text = 'y', font = {"size" : 16}), range = [0,canvasSize+3], tickfont = dict(size=14)),
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
                    for k in range(0,runtime)
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
        logger.info("Original Store: %s", store)
        raise PreventUpdate

    if stim is None:
        raise PreventUpdate

    logger.info("Loading line graphs")

    try:
        runtime = store["runtime"]
        timeline = np.arange(runtime)

        # Default to the canvas center; the canvas can be smaller than the old
        # hardcoded (13,13) default, which indexed out of bounds.
        yDim, xDim = store["AM"].shape[1], store["AM"].shape[2]
        xPos = xDim // 2
        yPos = yDim // 2
        if clickData:
            xPos = min(int(clickData['points'][0]['x']), xDim - 1)
            yPos = min(int(clickData['points'][0]['y']), yDim - 1)

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
        log_exc("loading line graphs", ex)
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
    """Callback to query storage for all the trial names saved by the creator and update the dropdown options. """
    logger.info("Loading trial names")
    if(creator and creator != ""):
        try:
            names = storage.list_trial_names(creator)
        except Exception as ex:
            log_exc("listing saved experiments", ex)
            return []
        return [{"label": name, "value": name} for name in names]
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
        Output('canvas-size','value'),
        Output('mask-size','value'),
    ],
    [Input("load-creator-exp","n_clicks"),],
    [State("loaded-exps-dropdown","value"), State("load-exps-creator","value"),],
)
def load_trials(n1, name, creator):
    """Callback to query storage for the trial selected by the user and update the data tables and other relevant information for the trial. """
    if n1 is None:
        raise PreventUpdate

    try:
        logger.info("Loading experiment %r by %r", name, creator)
        trial = storage.get_trial(creator, name)
        if trial is not None and trial["stim_types"] and trial["vis_objs"]:
            return (trial["stim_types"], trial["vis_objs"], trial["runtime"], trial["name"],
                    False, False, None, None, {"display": "none"},
                    trial["canvas"] or 27, trial["mask"] or 3)
        else:
            return [], [], None, None, False, True, None, None, {"display": "none"}, no_update, no_update

    except Exception as ex:
        log_exc("loading experiment from storage", ex)
        return [], [], None, None, False, True, None, None, {"display": "none"}, no_update, no_update

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

if __name__ == '__main__':
    """The start point of the application. """
    debug = os.getenv("RAGNAROC_DEBUG", "").lower() in ("1", "true", "yes")
    app.run(debug=debug, port=int(os.getenv("PORT", "8050")))