from dash import dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
from dash_extensions import Lottie

def serve_layout(app):
    return html.Div(
        id="root",
        children=[
            # Main body
            html.Div(
                id="home-container",
                children=[
                    # Banner display
                    html.Div(
                        id="banner",
                        children=[
                            html.Img(
                                id="logo", src=app.get_asset_url("logo.png")
                            ),
                            html.H2("Ragnaroc", id="title", style={"font-family":"Norse", "marginTop":"1rem",}),
                        ],
                    ),
                    getRagnarocDetailsDiv()[0],
                    # Link to the trial section of the portal
                    dcc.Link(
                        children=[
                            html.Div(
                                [
                                    html.Div(
                                        [
                                            dbc.Button(
                                                "Let's run an experiment",
                                                id="goto-exp",
                                                color="warning",
                                            ),
                                        ],
                                        className="d-grid gap-2 col-6 mx-auto",
                                    ),
                                ],
                            ),
                        ],
                        href="/ragnaroc",
                        style = {"textDecoration":"none"},
                    ),
                ],
            ),
        ]
    )

def getRagnarocDetailsDiv():
    # Detailed information about the project, aka, the actual body of the index page.
    return html.Div(
        id="ragnaroc-details",
        children=[
            html.Div(
                [
                    html.P(
                        "A quintessential challenge for any perceptual system is the need to focus on task-relevant \
                        information without being blindsided by unexpected, yet important information. ",
                        id="para-spacing",
                        style={"textAlign":"center",},
                    ), 

                    html.P("The human visual system incorporates several solutions to this challenge, one of which is a reflexive covert \
                        attention system that is rapidly responsive to both the physical salience and the task-relevance of \
                        new information.",
                        id="para-spacing",
                        style={"textAlign":"center",},  
                    ),

                    html.P("RAGNAROC presents a model that simulates behavioral and neural correlates of \
                        reflexive attention as the product of brief neural attractor states that are formed across the visual \
                        hierarchy when attention is engaged. Such attractors emerge from an attentional gradient \
                        distributed over a population of topographically organized neurons and serve to focus processing \
                        at one or more locations in the visual field, while inhibiting the processing of lower priority \
                        information.",
                        id="para-spacing",
                        style={"textAlign":"justify",}, 
                    ),

                    html.P("The model moves towards a resolution of key debates about the nature of reflexive \
                        attention, such as whether it is parallel or serial, and whether suppression effects are distributed \
                        in a spatial surround, or selectively at the location of distractors. Most importantly, the model \
                        develops a framework for understanding the neural mechanisms of visual attention as a \
                        spatiotopic decision process within a hierarchy and links them to observable correlates such as \
                        accuracy, reaction time, and the N2pc and PD components of the EEG. This last contribution is \
                        the most crucial for repairing the disconnect that exists between our understanding of behavioral \
                        and neural correlates of attention. ",
                        id="para-spacing",
                    ),
                    # Links to the paper and preprint.
                    html.Div(
                        children=[
                            html.A("Check the preprint here! ",
                                href="https://www.biorxiv.org/content/10.1101/406124v4",
                                target="_blank",
                                id="para-spacing",
                                style={"color":"yellow",},
                            ),  

                            html.A("Check the official psych review here! ",
                                href="https://psycnet.apa.org/record/2020-58898-001",
                                target="_blank",
                                id="para-spacing",
                                style={"color":"yellow",},
                            ),  
                        ], 
                        id="center-links", 
                    ),
                ],
                style={"color":"White",},
            ),
        ],
    ),