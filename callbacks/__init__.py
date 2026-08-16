"""Callback registration for the RAGNAROC-UI app.

Each module owns one functional area and exposes register(app). The app object
is required because dash-extensions transforms (Serverside stores, output
multiplexing) hang off the app instance.
"""

from callbacks import builder, persistence, routing, simulation, visualization


def register_all(app):
    routing.register(app)
    builder.register(app)
    simulation.register(app)
    visualization.register(app)
    persistence.register(app)
