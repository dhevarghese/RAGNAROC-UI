# Reference model

`ragnaroc.pyx` is the scientific reference implementation of the RAGNAROC
model. The browser app runs a TypeScript port of it
(`web/src/model/ragnaroc.ts`), and the port is verified against fixtures
produced by this code.

## Build

Python 3.10+ and a C compiler (Xcode command line tools on macOS,
build-essential on Debian/Ubuntu, MSVC build tools on Windows).

```bash
pip install -r ../requirements.txt
python setup.py build_ext --inplace
mv ragnaroc.*.so ..      # the export script imports it from the repo root
```

## Use

```python
import numpy as np
import ragnaroc

EV, LV, IG, AM, II, N2pc, stimMap = ragnaroc.runTrial(
    [{"name": "T", "X": 14, "Y": 7, "duration": 500, "latency": 0, "stimulus": "T"}],
    [{"stimName": "T", "td": 0.4, "bu": 0.15}],
    600,                       # steps (ms)
    np.zeros((27, 27, 1)),     # video input (unused by the app; keep the shape)
    xDim=27, yDim=27, NNMask=3,
)
```

Maps are NumPy arrays indexed `[stimulus, step, x, y]` (`AM` and `IG` are
`[step, x, y]`), `N2pc` is one value per step. `scripts/export_reference.py`
is a complete example.

`python scripts/export_reference.py` (from the repo root) runs a handful of
experiments and writes `web/src/model/__fixtures__/reference.json`, which
`npm test` in `web/` compares the port against.
