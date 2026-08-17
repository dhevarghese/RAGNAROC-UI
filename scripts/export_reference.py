"""Export reference outputs from the compiled Cython model for the TypeScript port's
differential test (web/src/model/ragnaroc.test.ts).

Run from the repo root with the ragnaroc extension built:
    python scripts/export_reference.py

Writes web/src/model/__fixtures__/reference.json with, per case: the full N2pc
trace, per-step grid sums for every map, and the final frame of every map.
"""

import json
import os
import sys

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import ragnaroc  # noqa: E402  (compiled extension at repo root)

CASES = {
    "diff27": dict(
        canvas=27, mask=3, steps=300,
        stim_types=[{"stimName": "1", "td": 0.18, "bu": 0.15}, {"stimName": "2", "td": 0.18, "bu": 0.15}],
        vis_objs=[
            {"name": "1", "X": 7, "Y": 14, "duration": 120, "latency": 0, "stimulus": "1"},
            {"name": "2", "X": 21, "Y": 14, "duration": 120, "latency": 120, "stimulus": "2"},
        ],
    ),
    "lateral27": dict(
        canvas=27, mask=3, steps=300,
        stim_types=[{"stimName": "1", "td": 0.4, "bu": 0.15}, {"stimName": "2", "td": 0.18, "bu": 0.17}],
        vis_objs=[
            {"name": "1", "X": 14, "Y": 7, "duration": 500, "latency": 0, "stimulus": "1"},
            {"name": "2", "X": 7, "Y": 14, "duration": 500, "latency": 0, "stimulus": "2"},
        ],
    ),
    "eimer27": dict(
        canvas=27, mask=3, steps=250,
        stim_types=[{"stimName": "1", "td": 0.7, "bu": 0.6}, {"stimName": "2", "td": 0.7, "bu": 0.6}],
        vis_objs=[
            {"name": "1", "X": 10, "Y": 10, "duration": 40, "latency": 0, "stimulus": "1"},
            {"name": "2", "X": 10, "Y": 18, "duration": 40, "latency": 10, "stimulus": "2"},
        ],
    ),
    "small10": dict(
        canvas=10, mask=2, steps=150,
        stim_types=[{"stimName": "T", "td": 0.5, "bu": 0.5}],
        vis_objs=[{"name": "t1", "X": 3, "Y": 4, "duration": 60, "latency": 20, "stimulus": "T"}],
    ),
}


def summarize(name, arr):
    """Per-step sums plus the final frame, for 3-D (t,y,x) or 4-D (s,t,y,x) maps."""
    if arr.ndim == 3:
        return {"stepSums": arr.sum(axis=(1, 2)).tolist(), "finalFrame": arr[-1].ravel().tolist()}
    return {
        "stepSums": arr.sum(axis=(2, 3)).tolist(),           # [stim][step]
        "finalFrame": [arr[s, -1].ravel().tolist() for s in range(arr.shape[0])],
    }


def main():
    out = {}
    for name, case in CASES.items():
        video = np.zeros((27, 27, 1))
        EV, LV, IG, AM, II, N2pc, stimMap = ragnaroc.runTrial(
            case["vis_objs"], case["stim_types"], case["steps"], video,
            xDim=case["canvas"], yDim=case["canvas"], NNMask=case["mask"],
        )
        out[name] = {
            "input": case,
            "stimMap": stimMap,
            "n2pc": N2pc.tolist(),
            "EV": summarize("EV", EV),
            "LV": summarize("LV", LV),
            "II": summarize("II", II),
            "AM": summarize("AM", AM),
            "IG": summarize("IG", IG),
        }
        print(f"{name}: steps={case['steps']} canvas={case['canvas']} AM.max={AM.max():.4f} n2pc.absmax={np.abs(N2pc).max():.4f}")

    dest = os.path.join(ROOT, "web", "src", "model", "__fixtures__")
    os.makedirs(dest, exist_ok=True)
    path = os.path.join(dest, "reference.json")
    with open(path, "w") as f:
        json.dump(out, f)
    print("wrote", path, f"({os.path.getsize(path) / 1e6:.1f} MB)")


if __name__ == "__main__":
    main()
