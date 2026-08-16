"""Callbacks for the experiment builder: stimulus types, visual objects, presets."""

import plotly.graph_objects as go
from dash import callback_context
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State

from callbacks.common import PRESETS, PRESET_CANVAS, PRESET_MASK, PRESET_RUNTIME


def canvas_preview_figure(rows, canvas):
    """Small scatter of the placed visual objects on the canvas grid."""
    try:
        canvas = int(canvas) if canvas else 27
    except (TypeError, ValueError):
        canvas = 27

    fig = go.Figure()
    by_stim = {}
    for row in rows or []:
        try:
            by_stim.setdefault(str(row.get("stimulus", "?")), []).append(
                (float(row["X"]), float(row["Y"]), str(row.get("name", "")),
                 float(row.get("latency", 0) or 0), float(row.get("duration", 0) or 0))
            )
        except (TypeError, ValueError, KeyError):
            continue

    for stim, pts in sorted(by_stim.items()):
        fig.add_trace(go.Scatter(
            x=[p[0] for p in pts], y=[p[1] for p in pts],
            mode="markers+text",
            text=[p[2] for p in pts], textposition="top center",
            name="stimulus " + stim,
            marker=dict(size=14, line=dict(width=1, color="white")),
            customdata=[[p[3], p[4]] for p in pts],
            hovertemplate="%{text}: (%{x}, %{y})<br>appears at %{customdata[0]} ms, lasts %{customdata[1]} ms<extra></extra>",
        ))

    fig.update_layout(
        template="plotly_dark",
        title=dict(text="Canvas preview ({0}×{0})".format(canvas), font=dict(size=14)),
        height=320,
        margin=dict(l=40, r=20, t=50, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0.2)",
        legend=dict(orientation="h", y=-0.18),
        xaxis=dict(range=[0, canvas + 1], title="X", dtick=max(1, canvas // 9)),
        yaxis=dict(range=[0, canvas + 1], title="Y", dtick=max(1, canvas // 9), scaleanchor="x"),
    )
    if not by_stim:
        fig.add_annotation(
            text="No objects yet — add one on the left,<br>or pick a preset above.",
            showarrow=False, font=dict(color="#aab0bc", size=13),
        )
    return fig


def register(app):
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
        """ Add visual object details to the data table, from the form or a preset. """
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
            rows = [dict(obj) for obj in PRESETS.get(preset, {}).get("vis_objs", [])]

        return rows, openAlert, duplicateObj, {"display": "none"}

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
        """ Add stimulus type details to the data table, from the form or a preset. """
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
            rows = [dict(st) for st in PRESETS.get(preset, {}).get("stim_types", [])]

        return rows, openAlert, duplicateStimulus, {"display": "none"}

    @app.callback(
        Output("text-td-weight", "value"),
        Output("top-down", "value"),
        Input("text-td-weight", "value"),
        Input("top-down", "value"),
    )
    def tdUpdate(input_value, slider_value):
        """ Simultaneously update the text/slider for top-down weights. """
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
        ctx = callback_context
        trigger_id = ctx.triggered[0]["prop_id"].split(".")[0]
        value = input_value if trigger_id == "text-bu-weight" else slider_value
        return value, value

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
        Output('canvas-size','value'),
        Output('mask-size','value'),
        [
            Input('preset-experiment-choice','value'),
        ],
        prevent_initial_call=True,
    )
    def setPresetSimulationParameters(preset):
        """ All preset trials run for 600 ms on a 27x27 canvas with a 3x3 mask. """
        if (preset and preset!=""):
            return PRESET_RUNTIME, PRESET_CANVAS, PRESET_MASK
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
        Output('preset-description', 'children'),
        Input('preset-experiment-choice', 'value'),
        prevent_initial_call=True,
    )
    def describePreset(preset):
        """ Show a one-line description of the chosen preset. """
        if preset and preset in PRESETS:
            return "{} All steps below have been filled in — tweak anything, then run.".format(PRESETS[preset]["description"])
        return "Pick a preset to fill every step with a ready-made experiment — or skip this and build your own below."

    @app.callback(
        Output('canvas-preview', 'figure'),
        [
            Input('vis-objs-table', 'data'),
            Input('canvas-size', 'value'),
        ],
        prevent_initial_call=False,
    )
    def updateCanvasPreview(rows, canvas):
        """ Live preview of where the visual objects sit on the canvas. """
        return canvas_preview_figure(rows, canvas)
