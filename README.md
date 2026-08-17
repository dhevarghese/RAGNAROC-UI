# Ragnaroc

An interactive simulator for the RAGNAROC model of reflexive visual attention
([Wyble et al., 2020](https://psycnet.apa.org/record/2020-58898-001)).
Describe a small visual experiment, what appears, where, and when, and watch
the model predict how attention deploys across the visual field millisecond by
millisecond, down to the simulated N2pc EEG component.

The app runs entirely in the browser: the model is a TypeScript port of the
reference implementation, executed in a Web Worker, so every change
re-simulates in a few hundred milliseconds and nothing is uploaded anywhere.

Live site: https://dhevarghese.github.io/RAGNAROC-UI/

## Repository layout

| Path | What |
|---|---|
| [`web/`](web/) | The app: Vite + React + TypeScript, no other runtime dependencies. `web/src/model/ragnaroc.ts` is the model port. |
| [`cython/`](cython/) | The scientific reference implementation of the model in Cython (`ragnaroc.pyx`). The port is verified against it. |
| [`scripts/export_reference.py`](scripts/export_reference.py) | Runs the compiled reference model on a few experiments and writes the fixtures the port is tested against. |
| [`.github/workflows/web.yml`](.github/workflows/web.yml) | CI: typecheck, tests, build, deploy to GitHub Pages. |

## Run it locally

Requires Node 20+.

```bash
cd web && npm install && npm run dev
```

Open http://localhost:5173. Other commands, all from `web/`:

- `npm test` runs the unit tests, including the differential test that pins
  the TypeScript model to fixtures exported from the reference model.
- `npm run typecheck` runs the TypeScript compiler.
- `npm run build` produces the static site in `web/dist/`.

## Deploy

Every push to `main` that touches `web/` builds, tests and publishes the site
to GitHub Pages through GitHub Actions. One-time setup: repository Settings,
Pages, Source: "GitHub Actions". The build is served from `/<repo>/`, which
the workflow passes in as `VITE_BASE`.

## Changing the model

The reference model lives in [`cython/ragnaroc.pyx`](cython/ragnaroc.pyx).
To change it and keep the app in sync:

1. Edit `cython/ragnaroc.pyx`.
2. Build it (Python 3.10+, a C compiler):
   ```bash
   pip install -r requirements.txt
   cd cython && python setup.py build_ext --inplace && mv ragnaroc.*.so .. && cd ..
   ```
3. Re-export the fixtures: `python scripts/export_reference.py`.
4. Port the change to `web/src/model/ragnaroc.ts`. `npm test` in `web/` tells
   you when the two agree again (single-precision constants matter: every
   `cdef float` in the reference is a `Math.fround(...)` in the port).

## Contributing

Fork, branch, change, pull request. UI copy avoids em dashes and bold inside
prose; the app has no runtime dependencies beyond React, and we would like to
keep it that way.

## Citing

If you use the simulator in your work, please cite the model paper:
Wyble, B., Callahan-Flintoft, C., Chen, H., Marinov, T., Sarkar, A., & Bowman, H. (2020).
Understanding visual attention with RAGNAROC: A reflexive attention gradient through neural
AttRactOr competition. *Psychological Review, 127*(6), 1163–1198.
https://doi.org/10.1037/rev0000245

GitHub's "Cite this repository" button (from [`CITATION.cff`](CITATION.cff)) also gives a
citation for the tool itself.

## Licence

[MIT](LICENSE). The model is the published work of Wyble et al.; this repository covers the
simulator code and the TypeScript port.
