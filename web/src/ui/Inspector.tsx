import type { Experiment } from '../model/types'
import { stimColor, type Action } from '../state/experiment'

interface Props {
  experiment: Experiment
  dispatch: (a: Action) => void
  selectedId: string | null
  onSelect: (id: string | null) => void
}

function NumberField({ label, value, min, max, step = 1, onChange, hint }: {
  label: string; value: number; min: number; max: number; step?: number; hint?: string
  onChange: (v: number) => void
}) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      <input
        type="number" value={Number.isFinite(value) ? value : ''} min={min} max={max} step={step}
        onChange={(e) => onChange(e.target.value === '' ? NaN : Number(e.target.value))}
      />
      {hint && <span className="field-hint">{hint}</span>}
    </label>
  )
}

function WeightField({ label, value, onChange, hint }: { label: string; value: number; hint: string; onChange: (v: number) => void }) {
  return (
    <label className="field weight">
      <span className="field-label">{label} <b>{value.toFixed(2)}</b></span>
      <input type="range" min={0} max={1} step={0.01} value={value} onChange={(e) => onChange(Number(e.target.value))} />
      <span className="field-hint">{hint}</span>
    </label>
  )
}

/**
 * Left panel: stimulus types, then the selected object (or the object list),
 * then run settings. Every change re-simulates.
 */
export function Inspector({ experiment, dispatch, selectedId, onSelect }: Props) {
  const { stimulusTypes, objects } = experiment
  const selected = objects.find((o) => o.id === selectedId) ?? null

  return (
    <div className="inspector">
      <section className="panel">
        <header className="panel-head">
          <h2>Stimulus types</h2>
          <button className="btn small" onClick={() => dispatch({ type: 'stim/add' })}>+ add</button>
        </header>
        <p className="help">What can appear. <b>Bottom-up</b> is how physically salient it is; <b>top-down</b> is how relevant it is to the task. Both 0–1.</p>
        {stimulusTypes.length === 0 && <p className="muted">Add at least one stimulus type.</p>}
        {stimulusTypes.map((s, i) => (
          <div className="stim-card" key={s.id} style={{ borderColor: stimColor(i) }}>
            <div className="stim-head">
              <span className="swatch" style={{ background: stimColor(i) }} />
              <input className="name-input" value={s.name} onChange={(e) => dispatch({ type: 'stim/update', id: s.id, patch: { name: e.target.value } })} aria-label="stimulus name" />
              <button className="icon-btn" title="remove stimulus type" onClick={() => dispatch({ type: 'stim/remove', id: s.id })}>×</button>
            </div>
            <WeightField label="bottom-up" value={s.bu} hint="salience" onChange={(v) => dispatch({ type: 'stim/update', id: s.id, patch: { bu: v } })} />
            <WeightField label="top-down" value={s.td} hint="task relevance" onChange={(v) => dispatch({ type: 'stim/update', id: s.id, patch: { td: v } })} />
          </div>
        ))}
      </section>

      <section className="panel">
        <header className="panel-head">
          <h2>Objects</h2>
          <span className="muted small">{objects.length} placed</span>
        </header>
        <p className="help">Each object is one appearance of a stimulus type at (x, y): it shows up after <b>latency</b> ms and stays for <b>duration</b> ms. Click the field to add.</p>
        <ul className="obj-list">
          {objects.map((o) => {
            const i = Math.max(0, stimulusTypes.findIndex((s) => s.id === o.stimulus))
            return (
              <li key={o.id} className={o.id === selectedId ? 'selected' : ''} onClick={() => onSelect(o.id)}>
                <span className="swatch" style={{ background: stimColor(i) }} />
                <span className="obj-name">{o.name}</span>
                <span className="muted small">({o.x}, {o.y}) · {o.latency}→{o.latency + o.duration} ms</span>
              </li>
            )
          })}
        </ul>
        {selected && (
          <div className="obj-editor">
            <div className="stim-head">
              <input className="name-input" value={selected.name} onChange={(e) => dispatch({ type: 'obj/update', id: selected.id, patch: { name: e.target.value } })} aria-label="object name" />
              <button className="icon-btn" title="remove object" onClick={() => { dispatch({ type: 'obj/remove', id: selected.id }); onSelect(null) }}>×</button>
            </div>
            <label className="field">
              <span className="field-label">stimulus type</span>
              <select value={selected.stimulus} onChange={(e) => dispatch({ type: 'obj/update', id: selected.id, patch: { stimulus: e.target.value } })}>
                {stimulusTypes.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
              </select>
            </label>
            <div className="field-grid">
              <NumberField label="x" value={selected.x} min={1} max={experiment.canvas} onChange={(v) => dispatch({ type: 'obj/update', id: selected.id, patch: { x: v } })} />
              <NumberField label="y" value={selected.y} min={1} max={experiment.canvas} onChange={(v) => dispatch({ type: 'obj/update', id: selected.id, patch: { y: v } })} />
              <NumberField label="latency" value={selected.latency} min={0} max={1000} hint="ms" onChange={(v) => dispatch({ type: 'obj/update', id: selected.id, patch: { latency: v } })} />
              <NumberField label="duration" value={selected.duration} min={0} max={1000} hint="ms" onChange={(v) => dispatch({ type: 'obj/update', id: selected.id, patch: { duration: v } })} />
            </div>
          </div>
        )}
      </section>

      <section className="panel">
        <header className="panel-head"><h2>Simulation</h2></header>
        <div className="field-grid">
          <NumberField label="runtime" value={experiment.runtime} min={1} max={3000} hint="ms simulated" onChange={(v) => dispatch({ type: 'set', patch: { runtime: v } })} />
          <NumberField label="canvas" value={experiment.canvas} min={1} max={50} hint="N × N cells" onChange={(v) => dispatch({ type: 'set', patch: { canvas: v } })} />
          <NumberField label="mask" value={experiment.mask} min={1} max={10} hint="neighbourhood radius" onChange={(v) => dispatch({ type: 'set', patch: { mask: v } })} />
        </div>
      </section>
    </div>
  )
}
