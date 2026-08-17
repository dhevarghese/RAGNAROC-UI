import { ACT_MAX, ACT_MIN } from '../viz/colormap'

interface Props {
  open: boolean
  onClose: () => void
  onLanding: () => void
}

/** Slide-in guide: the short version of the landing page, available any time. */
export function Guide({ open, onClose, onLanding }: Props) {
  if (!open) return null
  return (
    <div className="guide-backdrop" onClick={onClose}>
      <aside className="guide" onClick={(e) => e.stopPropagation()} role="dialog" aria-label="guide">
        <header className="guide-head">
          <h2>Quick guide</h2>
          <button className="icon-btn" onClick={onClose} aria-label="close">×</button>
        </header>
        <div className="guide-body">
          <section>
            <h3>Build</h3>
            <ul>
              <li><b>Stimulus types</b> (left panel) are kinds of things, such as a target or a distractor. <b>Bottom-up</b> = salience, <b>top-down</b> = task relevance.</li>
              <li><b>Click the field</b> to place an object; <b>drag</b> to move; <b>Delete</b> removes the selected one. Each object appears after its <b>latency</b> and stays for its <b>duration</b>.</li>
              <li>The <b>schedule</b> shows when each object is on screen. Nothing can appear before 100 ms, which the model needs to settle.</li>
              <li><b>Simulation</b> settings: runtime (ms), canvas size, mask (neighbourhood radius).</li>
            </ul>
          </section>
          <section>
            <h3>Read</h3>
            <ul>
              <li>It re-simulates on every change. The pill in the top bar says <b>live</b> when it's done.</li>
              <li><b>Scrub</b> by dragging the N2pc trace or the schedule; <b>▶</b> plays; <b>← →</b> step 1 ms (shift: 10 ms).</li>
              <li>The <b>3D surface</b> shows one map at the current instant. Pick which with the chips and drag to orbit. The small maps show everything at once; click one to feature it.</li>
              <li>Hover any map to read a cell's value. The <b>fixed / auto</b> toggle under the surface sets the colour scale: fixed is the same {ACT_MIN} to {ACT_MAX} on every map so they compare directly; auto stretches each map to its own range so faint ones become readable.</li>
              <li>The <b>probe</b> (white marker) is a location; the trace charts show its full time course. Click any map to move it. Selecting an object moves the probe onto it.</li>
            </ul>
          </section>
          <section>
            <h3>Keep</h3>
            <ul>
              <li><b>Share link</b> encodes the whole experiment in the URL, so you can send it to anyone.</li>
              <li><b>Save</b> keeps it in this browser; <b>Saved ▾</b> lists them. <b>Presets ▾</b> has the classics.</li>
            </ul>
          </section>
          <section>
            <h3>The maps</h3>
            <ul>
              <li><b>EV</b> early visual: the stimulus signal. <b>LV</b> late visual: EV through receptive fields, boosted by attention.</li>
              <li><b>AM</b> attention map: where attention is. <b>IG</b> inhibitory gate: the brake on AM. <b>II</b> inhibitory interneurons: local push-back on LV.</li>
              <li><b>N2pc</b>: simulated EEG, attentional excitation minus inhibition, left minus right hemifield.</li>
            </ul>
          </section>
          <button className="btn" onClick={onLanding}>Read the full introduction</button>
        </div>
      </aside>
    </div>
  )
}
