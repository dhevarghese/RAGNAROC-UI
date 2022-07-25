from dash import dcc, html, dash_table
import dash_bootstrap_components as dbc

def sideBar():
    return html.Div(
        id="sidebar",
        children=[
            getPresetsDiv(),
            getSimulationParameters(),
            getStimulusTable(),
            getVisualObjectsTable(),
        ]
    )

def getPresetsDiv():
    return html.Div(
        children=[
            html.P("Use preset?",
                style={ "width":"50%", "paddingTop":"0.2rem", }
            ),
            html.Div(
                dcc.Dropdown(options=["Brisson", "Single", "Same", "Diff", "MidTLateralD", "EimerGrubert"], value='', id="preset-experiment-choice",), # "Same", throws errors
                style={"width":"70%",},
            ),

        ],
        style={ "display":"flex", },
    )               

def getSimulationParameters():
    return html.Div(
        children=[
            html.P("Canvas",
                style={ "paddingTop":"0.2rem", }
            ),
            html.Div(
                children = [
                    dcc.Input(
                        id="canvas-size",
                        className="form-name-input hideNumScroll",
                        placeholder='N',
                        type='number', min=1, max=40,
                        value='',
                        style= {"width":"40%", "text-align": "center"}
                    ),
                    dbc.Tooltip(
                        "NxN matrix range: (1,40) ",
                        target="canvas-size",
                        placement="top",
                    ),
                ],

            ),
            html.P("Mask",
                style={"paddingTop":"0.2rem", }
            ),
            html.Div(
                children = [
                    dcc.Input(
                        id="mask-size",
                        className="form-name-input hideNumScroll",
                        placeholder='N',
                        type='number', min=1, max=40,
                        value='',
                        style= {"width":"40%", "text-align": "center"}
                    ),
                    dbc.Tooltip(
                        "NxN matrix range: (1,40) ",
                        target="mask-size",
                        placement="top",
                    ),
                ],

            ),

        ],
        style={ "display":"flex", "justify-content": "space-around", "margin-top":"2.5rem"},
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
                        'id': 'stimName',
                    },
                    {
                        'name': 'Top Down',
                        'id': 'td',
                    },
                    {
                        'name': 'Bottom Up',
                        'id': 'bu',
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
                        "backgroundColor": "#444444",
                    },
                ],
            ),
        ],
        style={
            "marginTop": "2.5rem",
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
                        'id': 'name',
                    },
                    {
                        'name': 'X',
                        'id': 'X',
                    },
                    {
                        'name': 'Y',
                        'id': 'Y',
                    },
                    {
                        'name': 'Duration',
                        'id': 'duration',
                    },
                    {
                        'name': 'Latency',
                        'id': 'latency',
                    },
                    {
                        'name': 'Stimulus',
                        'id': 'stimulus',
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
                        "backgroundColor": "#444444",
                    },
                ],
            ),
        ],
        style={
            "marginTop": "2.5rem",
            "display":"none",
        },
    )