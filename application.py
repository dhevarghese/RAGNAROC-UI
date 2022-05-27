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

client = boto3.client(
    'dynamodb',
    aws_access_key_id='AKIAUEW5BFOJBMGPZ4VG',
    aws_secret_access_key='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',
    region_name="us-east-1",
    )
dynamodb = boto3.resource(
    'dynamodb',
    aws_access_key_id='AKIAUEW5BFOJBMGPZ4VG',
    aws_secret_access_key='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',
    region_name="us-east-1",
    )
ddb_exceptions = client.exceptions

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

### Callbacks for the main code

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
    ],
)
def addVisualObject(n_clicks, preset, rows, name, x, y, duration, latency, stimType, isOpen):
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
            if(rows[i]["vis-objs-item"] == name):
                duplicateObj = True
                break
        
        if(n_clicks>0 and validated and not duplicateObj):
            rows.append({'vis-objs-item': name, 'vis-objs-item-X': x, 'vis-objs-item-Y': y, 'vis-objs-item-duration': duration, 'vis-objs-item-latency': latency, 'vis-objs-item-stim-type': stimType})

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
    [State('stim-types-table','data'), State('stim-type-name','value'), State('top-down','value'), State('bottom-up','value'), State("stim-alert", "is_open"), State("stim-count-alert","is_open")],
    prevent_initial_call=True,
)
def addStimulusType(n_clicks, preset, rows, name, tdWeight, buWeight, isOpen, maxStimuliReached):
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
    ServersideOutput("original-store", "data"), ServersideOutput("sim-store", "data"), EnrichedOutput("run-sim-alert", "is_open"), EnrichedOutput("run-sim-alert", "children"), EnrichedOutput('stim-type-dropdown','value'), EnrichedOutput("results-visual", "style"), EnrichedOutput("save-alert", "is_open"), 
    [
        Input('run-sim','n_clicks'),  Input("save-creator-exp","n_clicks"), #Input("save-exp","n_clicks"), 
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
    memoize=True
)
def simulationOperations(clicks, saveClick, sts, vos, runtime, expName, isOpen, data, ogData, creator, openSavedAlert):
    #ragnaroc.Ragnaroc3C(x, y, Type1BottomUp, Type2BottomUp, Type3BottomUp, Type1TopDown, Type2TopDown, Type3TopDown,latency, duration, Stype,steps,videoinput)
    inputId = ""
    ctx = callback_context
    data = data or {}
    ogData = ogData or {}
    openSavedAlert = False

    if ctx.triggered:
        inputId = ctx.triggered[0]['prop_id'].split('.')[0]
        if(expName == "" or expName == None):
            # Experiment name Alert
            return ogData, data, True, "Please set experiment name", None, {"display": "none"}, openSavedAlert

    if(inputId == "run-sim"):
        if(len(sts) == 0):
            # Stimulus types alert
            return ogData, data, True,"Please add stimulus types to the experiment", None, {"display": "none"}, openSavedAlert
        
        if(len(vos) == 0):
            # Visual Objects Alert
            return ogData, data, True,"Please add visual objects to the experiment", None, {"display": "none"}, openSavedAlert

        if(runtime == "" or runtime == None):
            # Set runtime Alert
            return ogData, data, True, "Please set runtime of experiment", None, {"display": "none"}, openSavedAlert

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

        
        data = {}
        # data["EV1"], data["EV2"], data["LV1"], data["LV2"], data["IG"], data["AM"], data["II1"], data["II2"], data["N2pc"],  = ragnaroc.Ragnaroc3C(x, y, t1_bu, t2_bu, t3_bu, t1_td, t2_td, t2_td,latency, duration, Stype,steps,videoinput)
        # data["EV" + str(sts[0]['stim-type-item'])], data["EV" + str(sts[1]['stim-type-item'])], data["LV" + str(sts[0]['stim-type-item'])], data["LV" + str(sts[1]['stim-type-item'])], data["IG"], data["AM"], data["II" + str(sts[0]['stim-type-item'])], data["II" + str(sts[1]['stim-type-item'])], data["N2pc"],  = ragnaroc.Ragnaroc3C(x, y, t1_bu, t2_bu, t3_bu, t1_td, t2_td, t2_td,latency, duration, Stype,steps,videoinput)

        
        # data = {}
        ogData = {}
        ogData["EV" + str(sts[0]['stim-type-item'])], ogData["EV" + str(sts[1]['stim-type-item'])], ogData["EV" + str(sts[2]['stim-type-item'])], ogData["LV" + str(sts[0]['stim-type-item'])], ogData["LV" + str(sts[1]['stim-type-item'])], ogData["LV" + str(sts[2]['stim-type-item'])], ogData["IG"], ogData["AM"], ogData["II" + str(sts[0]['stim-type-item'])], ogData["II" + str(sts[1]['stim-type-item'])], ogData["II" + str(sts[2]['stim-type-item'])], ogData["N2pc"],  = ragnaroc.Ragnaroc3C(x, y, t1_bu, t2_bu, t3_bu, t1_td, t2_td, t3_td,latency, duration, Stype,steps,videoinput)


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

        return ogData, data, False, "", sts[0]['stim-type-item'] , {'display':'flex'}, openSavedAlert
    
    elif (inputId == "save-creator-exp" and creator != "" and (creator is not None)):	
        #Open Modal to enter creator name. Once entered, add to DB. 	
        openSavedAlert = saveExp(creator, expName, runtime, sts, vos)   	
        #Close modal, open saved alert 	
        	
    return {}, {}, isOpen, "", None, {"display": "none"}, openSavedAlert

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

@app.callback(
    Output("result-modal", "is_open"),
    [Input("result-info", "n_clicks")],
    [State("result-modal", "is_open")],
)
def toggle_modal(n1, is_open):
    if n1:
        return not is_open
    return is_open

@app.callback(	
    Output("creator-modal", "is_open"),	
    [Input("save-exp","n_clicks"), Input("save-creator-exp","n_clicks")],	
    [State("creator-modal", "is_open")],	
)	
def toggle_creator_modal(n1, n2, is_open):	
    if n1 or n2:	
        return not is_open	
    return is_open	

@app.callback(	
    Output("load-exp-modal", "is_open"),	
    [Input("load-sim","n_clicks"),],	
    [State("load-exp-modal", "is_open")],	
)	
def toggle_load_modal(n1, is_open):	
    if n1:	
        return not is_open	
    return is_open	

@app.callback(	
    Output("loaded-exps-dropdown", "options"),	
    [Input("load-exps-creator","value"),],	
    prevent_initial_call=True,
)	
def load_get_creator(creator):	
    print("Loading creators")	
    # response = dynamodb.Table('ragnaroc-experiments').query(	
    #         KeyConditionExpression=Key('creator').eq(creator)	
    #     )	
    response = dynamodb.Table('ragnaroc-exp-names').scan(	
            FilterExpression= Attr("creator").eq(creator)	
        )	
    # {'label': 'Inhibitory Gate (IG)', 'value': 'IG'},	
    # [{"label" : i["name"] , "value" : i["exp-id"]} for i in response["Items"]]	
    # [i["name"] for i in response["Items"]]	
    return [{"label" : i["name"] , "value" : i["exp-id"]} for i in response["Items"]]	

@app.callback(	
    [	
        Output('stim-types-table','data'),	
        Output('vis-objs-table','data'),	
        Output('exp-total-time','value'),	
        Output('exp-name','value'),     	
        Output("load-exp-modal", "is_open"), 	
    ],	
    [Input("load-creator-exp","n_clicks"),],	
    [State("loaded-exps-dropdown","value"),],	
)	
def load_exps(n1, expID):	
    if n1 is None:
        raise PreventUpdate

    print("Loading experiments")
    response = dynamodb.Table('ragnaroc-experiments').query(	
            KeyConditionExpression=Key('exp-id').eq(expID)	
        )	
    return response["Items"][0]["stimulus-types"], response["Items"][0]["visual-objects"], response["Items"][0]["runtime"], response["Items"][0]["name"], False

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

def saveExp(creator, expName, runtime, stimTypes, visObjs):	
    try:	
        # JSON formatting	
        uid = uuid.uuid5(uuid.NAMESPACE_X500, creator+ "|" + expName+"|"+str(runtime))	
        exp = {	
            "exp-id" : str(uid),	
            "creator" : str(creator),	
            "name": str(expName),	
            "runtime": str(runtime),	
            "stimulus-types": json.loads(json.dumps(stimTypes), parse_float=Decimal),	
            "visual-objects" : json.loads(json.dumps(visObjs), parse_float=Decimal),	
        }	
        expName = {	
            "exp-id" : str(uid),	
            "creator" : str(creator),	
            "name": str(expName),	
        }	
        print("adding")	
        # Add to DynamoDB	
        dynamodb.Table('ragnaroc-experiments').put_item(Item=exp)	
        dynamodb.Table('ragnaroc-exp-names').put_item(Item=expName)	
        print("added")	
        return True	
        	
    except Exception as ex:	
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"	
        message = template.format(type(ex).__name__, ex.args)	
        print(message)	
        return False

if __name__ == '__main__':
    # app.run_server()
    # app.run_server(debug=True)
    # app.run_server(debug=True,port=8080)
    application.run_server(debug=True,port=8080)