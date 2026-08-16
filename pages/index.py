"""Landing page: what RAGNAROC is, how the tool works, and a way in."""

from dash import dcc, html
import dash_bootstrap_components as dbc


def serve_layout(app):
    return html.Div(
        id="home-page",
        children=[
            html.Div(
                className="hero",
                children=[
                    html.Img(className="hero-logo", src=app.get_asset_url("logo.png")),
                    html.H1("Ragnaroc", className="hero-title"),
                    html.P(
                        "An interactive simulator of reflexive visual attention. Describe a simple visual "
                        "experiment — what appears, where, and when — and watch the RAGNAROC model predict how "
                        "attention deploys across the visual field, down to the simulated EEG.",
                        className="hero-lede",
                    ),
                    dcc.Link(
                        dbc.Button("Open the experiment builder", id="goto-exp", color="warning", size="lg"),
                        href="/ragnaroc",
                        className="hero-cta",
                    ),
                ],
            ),
            html.Div(
                className="how-it-works",
                children=[
                    howCard("1", "Describe", "Define stimulus types (how salient and task-relevant they are) and place visual objects on a canvas — or start from a preset experiment."),
                    howCard("2", "Simulate", "The model runs the trial millisecond by millisecond across interacting neural maps of the visual hierarchy."),
                    howCard("3", "Explore", "Scrub through 3-D activation maps over time, click any location to inspect its time course, and compare against the simulated N2pc EEG component."),
                ],
            ),
            html.Div(
                className="about",
                children=[
                    html.H2("About the model", className="about-title"),
                    html.P(
                        "RAGNAROC (Wyble et al.) models reflexive covert attention as brief neural attractor states "
                        "formed across the visual hierarchy. An attentional gradient over topographically organized "
                        "neurons focuses processing at one or more locations while inhibiting lower-priority "
                        "information — linking behavior to neural correlates such as the N2pc and PD components of "
                        "the EEG.",
                        className="about-text",
                    ),
                    html.Div(
                        className="about-links",
                        children=[
                            html.A("Read the preprint", href="https://www.biorxiv.org/content/10.1101/406124v4", target="_blank"),
                            html.A("Psychological Review paper", href="https://psycnet.apa.org/record/2020-58898-001", target="_blank"),
                        ],
                    ),
                ],
            ),
        ],
    )


def howCard(number, title, text):
    return html.Div(
        className="how-card",
        children=[
            html.Span(number, className="step-number"),
            html.H3(title, className="how-title"),
            html.P(text, className="how-text"),
        ],
    )
