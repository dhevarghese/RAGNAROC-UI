"""Callbacks for the experiment builder: stimulus types, visual objects, presets."""

from dash import callback_context
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State

from callbacks.common import PRESETS, PRESET_CANVAS, PRESET_MASK, PRESET_RUNTIME


def register(app):
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
