"""Shared helpers and data for the callback modules."""

import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ragnaroc")


def log_exc(context, ex):
    """Log a swallowed exception with enough detail to diagnose it."""
    logger.error(
        "An exception of type %s occurred while %s. Arguments: %r",
        type(ex).__name__, context, ex.args,
    )


# Preset experiments. Each entry fully describes a runnable trial: the stimulus
# types (with top-down/bottom-up weights) and the visual objects placed on the
# canvas. All presets run for 600 ms on a 27x27 canvas with a 3x3 mask.
PRESET_RUNTIME = 600
PRESET_CANVAS = 27
PRESET_MASK = 3

PRESETS = {
    "Brisson": {
        "description": "A single salient, task-relevant target (Brisson & Jolicœur).",
        "stim_types": [
            {"stimName": "1", "td": 0.4, "bu": 0.6},
            {"stimName": "2", "td": 0, "bu": 0},
        ],
        "vis_objs": [
            {"name": "1", "X": 7, "Y": 14, "duration": 100, "latency": 0, "stimulus": "1"},
        ],
    },
    "Single": {
        "description": "One long-lasting object of moderate salience and relevance.",
        "stim_types": [
            {"stimName": "1", "td": 0.18, "bu": 0.15},
            {"stimName": "2", "td": 0, "bu": 0},
        ],
        "vis_objs": [
            {"name": "1", "X": 7, "Y": 14, "duration": 500, "latency": 0, "stimulus": "1"},
        ],
    },
    "Same": {
        "description": "Two sequential objects at the same location.",
        "stim_types": [
            {"stimName": "1", "td": 0.18, "bu": 0.15},
            {"stimName": "2", "td": 0.18, "bu": 0.15},
        ],
        "vis_objs": [
            {"name": "1", "X": 7, "Y": 14, "duration": 120, "latency": 0, "stimulus": "1"},
            {"name": "2", "X": 7, "Y": 14, "duration": 120, "latency": 120, "stimulus": "2"},
        ],
    },
    "Diff": {
        "description": "Two sequential objects at different locations.",
        "stim_types": [
            {"stimName": "1", "td": 0.18, "bu": 0.15},
            {"stimName": "2", "td": 0.18, "bu": 0.15},
        ],
        "vis_objs": [
            {"name": "1", "X": 7, "Y": 14, "duration": 120, "latency": 0, "stimulus": "1"},
            {"name": "2", "X": 21, "Y": 14, "duration": 120, "latency": 120, "stimulus": "2"},
        ],
    },
    "MidTLateralD": {
        "description": "A central target with a lateral distractor shown together.",
        "stim_types": [
            {"stimName": "1", "td": 0.4, "bu": 0.15},
            {"stimName": "2", "td": 0.18, "bu": 0.17},
        ],
        "vis_objs": [
            {"name": "1", "X": 14, "Y": 7, "duration": 500, "latency": 0, "stimulus": "1"},
            {"name": "2", "X": 7, "Y": 14, "duration": 500, "latency": 0, "stimulus": "2"},
        ],
    },
    "EimerGrubert": {
        "description": "Two brief, highly salient targets in quick succession (Eimer & Grubert).",
        "stim_types": [
            {"stimName": "1", "td": 0.7, "bu": 0.6},
            {"stimName": "2", "td": 0.7, "bu": 0.6},
        ],
        "vis_objs": [
            {"name": "1", "X": 10, "Y": 10, "duration": 40, "latency": 0, "stimulus": "1"},
            {"name": "2", "X": 10, "Y": 18, "duration": 40, "latency": 10, "stimulus": "2"},
        ],
    },
}
