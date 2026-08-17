import { PRESETS } from '../model/presets'
import type { Experiment } from '../model/types'
import { stimColor } from '../state/experiment'

interface Props {
  onOpen: (experiment?: Experiment) => void
}

const MAPS = [
  ['Early visual (EV)', 'The stimulus signal on the input layer — what is physically on screen, per stimulus type.'],
  ['Late visual (LV)', 'EV filtered through receptive fields and amplified wherever attention is deployed.'],
  ['Attention map (AM)', 'Where attention is. Driven by LV weighted by task relevance; above threshold it boosts LV in return.'],
  ['Inhibitory gate (IG)', 'The brake: excited by LV and by AM itself, it suppresses the attention map once it crosses threshold.'],
  ['Inhibitory interneurons (II)', 'Local inhibition that pushes back on LV once it fires — keeps the system from running away.'],
  ['N2pc', 'A simulated EEG component: attentional excitation minus inhibition, left hemifield minus right. The lab\'s bridge to real data.'],
]

/** What this is, how to use it, and a way in. */
export function Landing({ onOpen }: Props) {
  return (
    <div className="landing">
      <header className="landing-hero">
        <img src="./logo.png" alt="" className="landing-logo" />
        <h1>Ragnaroc</h1>
        <p className="landing-tag">A simulator for reflexive visual attention — in your browser.</p>
        <p className="landing-lede">
          Describe a small visual experiment: what can appear, where, and when. The RAGNAROC model
          (Wyble et al.) predicts how attention deploys across the visual field millisecond by
          millisecond — down to the simulated N2pc EEG component. Everything runs locally; nothing
          is uploaded.
        </p>
        <div className="landing-cta">
          <button className="btn primary big" onClick={() => onOpen()}>Open the simulator</button>
          <a className="btn big" href="#how">How does it work?</a>
        </div>
      </header>

      <section className="landing-section" id="how">
        <h2>How to use it</h2>
        <ol className="how-steps">
          <li>
            <span className="step-num">1</span>
            <div>
              <h3>Define stimulus types</h3>
              <p>A stimulus type is a kind of thing that can appear — a target, a distractor. Give each a
                <b> bottom-up</b> weight (how physically salient it is) and a <b>top-down</b> weight (how
                relevant it is to the task), both from 0 to 1.</p>
            </div>
          </li>
          <li>
            <span className="step-num">2</span>
            <div>
              <h3>Place objects on the field</h3>
              <p>Click the visual field to place an object; drag to move it. Each object is one appearance of
                a stimulus type: it shows up after a <b>latency</b> and stays for a <b>duration</b>. The
                schedule beside the field shows exactly when everything is on screen.</p>
            </div>
          </li>
          <li>
            <span className="step-num">3</span>
            <div>
              <h3>Watch it simulate — live</h3>
              <p>There is no run button. Every change re-runs the model in a background thread in a few
                hundred milliseconds. Drag a weight and watch attention move.</p>
            </div>
          </li>
          <li>
            <span className="step-num">4</span>
            <div>
              <h3>Read the results</h3>
              <p>Scrub time on the N2pc trace or press play. The 3-D surface shows one brain map at that
                instant; the small maps show all of them. Click anywhere to move the <b>probe</b> and see that
                location's full time course. <b>Share link</b> puts the whole experiment in the URL.</p>
            </div>
          </li>
        </ol>
      </section>

      <section className="landing-section">
        <h2>Start from a classic experiment</h2>
        <div className="preset-grid">
          {PRESETS.map((p) => (
            <button key={p.key} className="preset-card" onClick={() => onOpen(p.experiment)}>
              <PresetThumb exp={p.experiment} />
              <b>{p.title}</b>
              <span>{p.description}</span>
            </button>
          ))}
        </div>
      </section>

      <section className="landing-section">
        <h2>What you'll be looking at</h2>
        <p className="landing-lede">The model is a stack of interacting topographic maps. Each one is a grid the size of the visual field.</p>
        <dl className="map-cards">
          {MAPS.map(([t, d]) => (
            <div key={t} className="map-card"><dt>{t}</dt><dd>{d}</dd></div>
          ))}
        </dl>
      </section>

      <section className="landing-section about">
        <h2>About the model</h2>
        <p>
          RAGNAROC models reflexive covert attention as brief neural attractor states formed across the
          visual hierarchy. An attentional gradient over topographically organised neurons focuses processing
          at one or more locations while inhibiting lower-priority information, linking behaviour to neural
          correlates such as the N2pc and P<sub>D</sub> components of the EEG.
        </p>
        <p className="landing-links">
          <a href="https://www.biorxiv.org/content/10.1101/406124v4" target="_blank" rel="noreferrer">Preprint (bioRxiv)</a>
          <a href="https://psycnet.apa.org/record/2020-58898-001" target="_blank" rel="noreferrer">Psychological Review</a>
          <a href="https://github.com/dhevarghese/RAGNAROC-UI" target="_blank" rel="noreferrer">Source on GitHub</a>
        </p>
        <p className="muted small">The simulator is a TypeScript port of the reference Cython model, verified against it to floating-point precision on every build.</p>
      </section>
    </div>
  )
}

/** Tiny SVG of a preset's field: dots where objects are, coloured by stimulus. */
function PresetThumb({ exp }: { exp: Experiment }) {
  const s = 96
  return (
    <svg width={s} height={s} viewBox={`0 0 ${s} ${s}`} className="preset-thumb" aria-hidden>
      <rect width={s} height={s} rx={8} fill="#0a0c11" />
      <line x1={s / 2 - 4} y1={s / 2} x2={s / 2 + 4} y2={s / 2} stroke="rgba(255,255,255,0.3)" />
      <line x1={s / 2} y1={s / 2 - 4} x2={s / 2} y2={s / 2 + 4} stroke="rgba(255,255,255,0.3)" />
      {exp.objects.map((o) => {
        const i = Math.max(0, exp.stimulusTypes.findIndex((t) => t.id === o.stimulus))
        return <circle key={o.id} cx={((o.x - 0.5) / exp.canvas) * s} cy={((o.y - 0.5) / exp.canvas) * s} r={5} fill={stimColor(i)} />
      })}
    </svg>
  )
}
