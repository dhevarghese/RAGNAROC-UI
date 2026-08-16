"""Callbacks for the save/load modals and trial retrieval from storage."""

from dash import no_update
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State

import storage
from callbacks.common import log_exc, logger


def register(app):
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
        """Callback to query storage for all the trial names saved by the creator. """
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
        """Callback to fetch the selected trial from storage and restore it in the UI. """
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
