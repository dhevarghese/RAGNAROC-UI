# RAGNAROC-UI

An interactive simulator for the RAGNAROC model of reflexive visual attention
(Wyble et al.). Describe a small visual experiment — what appears, where, and
when — and watch the model predict how attention deploys across the visual
field, down to the simulated N2pc EEG component.

There are two apps in this repository:

| | Where | Status |
|---|---|---|
| **v2 — browser-native** (recommended) | [`web/`](web/) | The model runs *in your browser* (TypeScript port, verified against the reference). Live re-simulation on every change, interactive canvas, shareable links. Deploys as a static site. |
| v1 — Dash | [`application.py`](application.py), [`callbacks/`](callbacks/), [`pages/`](pages/) | Python/Dash app driving the compiled Cython model. Kept for reference; see [docs/ROADMAP.md](docs/ROADMAP.md) for the plan to retire it. |

The scientific reference implementation of the model stays in Python:
[`cython/ragnaroc.pyx`](cython/ragnaroc.pyx) (compiled) and
[`ragnaroc_vanilla.py`](ragnaroc_vanilla.py) (pure Python, for reading).

## v2 — run it locally

Requires Node 20+.

```bash
cd web && npm install && npm run dev
```

Then open http://localhost:5173. `npm test` runs the differential test that
pins the TypeScript model to fixtures exported from the compiled Cython model
(`scripts/export_reference.py`); `npm run build` produces the static site in
`web/dist/`. Pushes to `main` build, test, and publish it to GitHub Pages via
[`.github/workflows/web.yml`](.github/workflows/web.yml) (enable Pages with
source "GitHub Actions" in the repository settings once).

## v1 — run the Dash app locally

Requires Python 3.12 and a C compiler.

```bash
pip install -r requirements.txt -r requirements-build.txt
cd cython && python setup.py build_ext --inplace && mv ragnaroc.*.so .. && cd ..
python application.py
```

Serves at http://localhost:8050. Saved experiments go to a local SQLite database
at `data/ragnaroc.db`. Environment: `RAGNAROC_DEBUG=1` enables Dash debug mode,
`PORT` overrides the port, `RAGNAROC_STORAGE=dynamo` (with standard AWS
credentials in the environment) switches persistence to DynamoDB.

## Contributing

Fork, branch, change, pull-request. For model changes, edit
`cython/ragnaroc.pyx`, rebuild, re-export the fixtures with
`python scripts/export_reference.py`, and port the change to
`web/src/model/ragnaroc.ts` — `npm test` will tell you when the two agree.
