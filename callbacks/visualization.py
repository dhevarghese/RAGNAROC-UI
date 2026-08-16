"""Callbacks that render the simulation results: surface plot and line plots."""

import numpy as np
import plotly.graph_objects as go
from dash.exceptions import PreventUpdate
from dash_extensions.enrich import Input, Output, State, Trigger
from plotly.subplots import make_subplots

from callbacks.common import log_exc, logger


def frame_args(duration):
    # Parameters for the animation
    return {
        "frame": {"duration": duration},
        "mode": "immediate",
        "fromcurrent": True,
        "transition": {"duration": duration, "easing": "linear"},
    }


def getSurfaceGraphLayout(currSliderVal=200, runtime=0, canvasSize=30):
    """ Function to set the layout of the surface plots. """
    return go.Layout(
        template= "plotly_dark",
        title = "Surface Plot",
        scene = dict
        (
            aspectratio=dict(x=1,y=1,z=1),
            xaxis = dict(title= dict(text = 'x', font = {"size" : 16}), range = [0,canvasSize+3], tickfont = dict(size=14),),
            yaxis = dict(title= dict(text = 'y', font = {"size" : 16}), range = [0,canvasSize+3], tickfont = dict(size=14)),
            zaxis = dict(title= dict(text = 'z', font = {"size" : 16}), showticklabels=False, showgrid=False, zeroline=False, range = [0,256],),
            camera = dict(
                eye=dict(x=1.31, y=1.31, z=1.31)
            ),
        ),
        width=700, height=600,
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
                "pad": {"r": 10, "t": 90, "l":10},
                "showactive": True,
                "type": "buttons",
                "x": 0.1,
                "xanchor": "right",
                "y": 0.1,
                "yanchor": "top",
                "active" : 1,
                "bgcolor" : "#fccd61",
                "font" : {"color": "darkslateblue"},
            },
        ],
        sliders = [
            {
                "pad": {"b": 10, "t": 20, "r":10},
                "x": 0.1,
                "y": 0,
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


def register(app):
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

            Fig consists of data, layout and frames. The frames are required to
            animate through the neural activations.
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

        return fig

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
        """ Update the line graphs of all activation maps according to surface plot
            clicks, change in stimuli or time marker. X axis is time, Y axis is the
            activation at the selected canvas location.
        """
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
            figs.update_xaxes(showgrid=False, showticklabels=False, row=figCount, col=1)
            figs.update_yaxes(showgrid=False, showticklabels=False, range=[-10,40], row=figCount, col=1)

            if timePoint:
                figs.add_vline( x=timePoint, line_width=3, line_dash="dash", line_color="#fccd61", row=figCount, col=1)

            figCount+=1

            for k in ["IG","AM"]:
                figs.add_trace(
                    go.Scatter(x=timeline, y=store[k][:, yPos,xPos], mode='lines', name=k), row=figCount, col=1,
                )
                figs.update_xaxes(showgrid=False, showticklabels=False, row=figCount, col=1)
                figs.update_yaxes(showgrid=False, showticklabels=False, range=[-10,40], row=figCount, col=1)
                figs.add_hline(y=0, line_color="lightgray",)
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
                    figs.add_hline(y=0, line_color="lightgray", opacity=0.2)
                    if timePoint:
                        figs.add_vline( x=timePoint, line_width=3, line_dash="dash", line_color="#fccd61", row=figCount, col=1)
                    figCount +=1

            figs.update_yaxes(title="Activation", row=4, col=1)
            figs.update_xaxes(title="Time", showticklabels=True, range=[0,runtime], row=6, col=1)
            figs.update_layout(template= "plotly_dark", title = "Time course at X : {}, Y : {}".format(xPos, yPos))

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

    # Clientside callback to scroll down to the results when the simulation completes.
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
