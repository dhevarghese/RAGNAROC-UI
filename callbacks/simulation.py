"""Callbacks that validate the experiment, run the model, and save trials."""

import sys

import numpy as np
from dash import callback_context, no_update
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, Serverside, State

import ragnaroc
import storage
from callbacks.common import log_exc, logger


def validate_experiment(sts, vos, runtime, expName, canvas, mask):
    """Validate the full experiment definition.

    Returns None when everything is fine, otherwise a user-facing message
    describing the first problem found. Coerces the numeric columns of the
    (user-editable) tables in place, like the original inline validation did.
    """
    if expName == "" or expName is None:
        return "Please set experiment name"
    if len(sts) == 0:
        return "Please add stimulus types to the experiment"
    if len(vos) == 0:
        return "Please add visual objects to the experiment"
    if runtime == "" or runtime is None or int(runtime) < 1:
        return "Please set an appropriate runtime for the experiment"
    if canvas == "" or canvas is None or int(canvas) < 1 or int(canvas) > 50:
        return "Please set an appropriate canvas size for the experiment"
    if mask == "" or mask is None or int(mask) < 1 or int(mask) > 10:
        return "Please set an appropriate mask size for the experiment"
    if mask > canvas:
        return "Mask cannot be larger than the canvas!"

    try:
        stims = set()
        for item in sts:
            stims.add(item["stimName"])
            name, td, bu = item["stimName"], float(item["td"]), float(item["bu"])
            if td > 1 or td < 0:
                return "Please set an appropriate top-down value for stimulus {}".format(name)
            if bu > 1 or bu < 0:
                return "Please set an appropriate bottom-up value for stimulus {}".format(name)

        for item in vos:
            name, x, y, duration, latency, stim = (
                item["name"], float(item["X"]), float(item["Y"]),
                float(item["duration"]), float(item["latency"]), item["stimulus"],
            )
            if stim not in stims:
                return "Please ensure that all visual objects have an appropriate stimulus type"
            if x > canvas or x < 1:
                return "Please set an appropriate x value for object {}".format(name)
            if y > canvas or y < 1:
                return "Please set an appropriate y value for object {}".format(name)
            if duration > 1000 or duration < 0:
                return "Please set an appropriate duration for object {}".format(name)
            if latency > 1000 or latency < 0:
                return "Please set an appropriate latency for object {}".format(name)
            item["X"], item["Y"], item["duration"], item["latency"] = x, y, duration, latency

    except Exception as ex:
        log_exc("validating the experiment inputs", ex)
        return "An error occured..."

    return None


def register(app):
    @app.callback(
        Output("original-store", "data"),
        Output("sim-store", "data"),
        Output("run-sim-alert", "is_open"),
        Output("run-sim-alert", "children"),
        Output('stim-type-dropdown','value'),
        Output("results-visual", "style"),
        [Input('run-sim','n_clicks')],
        [
            State('stim-types-table','data'),
            State('vis-objs-table','data'),
            State('exp-total-time','value'),
            State('exp-name','value'),
            State("exp-creator-name", "value"),
            State('canvas-size','value'),
            State('mask-size','value'),
        ],
        prevent_initial_call=True,
        running=[(Output("run-sim", "disabled"), True, False)],
    )
    def runSimulation(clicks, sts, vos, runtime, expName, creator, canvas, mask):
        """ Validate the experiment and run the RAGNAROC model. The core of the system. """
        if clicks is None:
            raise PreventUpdate

        error = validate_experiment(sts, vos, runtime, expName, canvas, mask)
        if error:
            return no_update, no_update, True, error, None, {"display": "none"}

        steps = int(runtime)
        videoinput = np.zeros((27,27,1)).astype(float)

        data = {}
        ogData = {}

        ogData["EV"], ogData["LV"], ogData["IG"], ogData["AM"], ogData["II"], ogData["N2pc"], ogData["stimMap"] = \
            ragnaroc.runTrial(vos, sts, steps, videoinput, xDim=canvas, yDim=canvas, NNMask=mask)

        # Normalize the data to the uint8 range (0-255). EE = 30, EI = -10
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

        try:
            storage.log_run(str(creator) if creator else "guest", str(expName))
        except Exception as ex:
            log_exc("logging run to storage", ex)

        return Serverside(ogData), Serverside(data), False, "", sts[0]['stimName'], {'display':'flex'}

    @app.callback(
        Output("save-alert", "is_open"),
        Output("rewrite-modal", "is_open"),
        Output("run-sim-alert", "is_open"),
        Output("run-sim-alert", "children"),
        [
            Input("save-creator-exp","n_clicks"), Input("rewrite-accept","n_clicks"), Input("rewrite-deny", "n_clicks"),
        ],
        [
            State('stim-types-table','data'),
            State('vis-objs-table','data'),
            State('exp-total-time','value'),
            State('exp-name','value'),
            State("exp-creator-name", "value"),
            State('canvas-size','value'),
            State('mask-size','value'),
        ],
        prevent_initial_call=True,
    )
    def saveExperiment(saveClick, rewriteClick, rewriteDeny, sts, vos, runtime, expName, creator, canvas, mask):
        """ Save the experiment definition; on a name collision ask before overwriting. """
        ctx = callback_context
        if not ctx.triggered:
            raise PreventUpdate
        inputId = ctx.triggered[0]['prop_id'].split('.')[0]

        if inputId == "rewrite-deny":
            return False, False, False, ""

        error = validate_experiment(sts, vos, runtime, expName, canvas, mask)
        if error:
            return False, False, True, error

        if inputId == "save-creator-exp" and creator:
            try:
                if storage.trial_exists(creator, expName):
                    return False, True, False, ""
                storage.save_trial(creator, expName, int(runtime), int(canvas), int(mask), sts, vos)
                return True, False, False, ""
            except Exception as ex:
                log_exc("saving experiment", ex)
                return False, False, True, "Failed to save the experiment (storage error)."

        if inputId == "rewrite-accept":
            try:
                storage.save_trial(creator, expName, int(runtime), int(canvas), int(mask), sts, vos, overwrite=True)
                return True, False, False, ""
            except Exception as ex:
                log_exc("saving experiment", ex)
                return False, False, True, "Failed to save the experiment (storage error)."

        raise PreventUpdate
