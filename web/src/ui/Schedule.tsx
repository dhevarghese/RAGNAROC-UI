import type { Experiment } from '../model/types'
import { stimColor } from '../state/experiment'

interface Props {
  experiment: Experiment
  step: number
  selectedId: string | null
  onSelect: (id: string | null) => void
  onScrub: (step: number) => void
}

/** Model time before the first object can appear (t1onset in the reference model). */
export const T1_ONSET = 99

/**
 * When is each object on screen? One row per object, a bar from onset to
 * offset, on the same time axis as every other chart. Click/drag to scrub.
 */
export function Schedule({ experiment, step, selectedId, onSelect, onScrub }: Props) {
  const { objects, stimulusTypes, runtime } = experiment
  const stimIndex = (id: string) => Math.max(0, stimulusTypes.findIndex((s) => s.id === id))
  const pct = (t: number) => `${(Math.min(runtime, Math.max(0, t)) / runtime) * 100}%`

  const scrub = (e: React.PointerEvent<HTMLDivElement>) => {
    const r = e.currentTarget.getBoundingClientRect()
    onScrub(Math.round(Math.min(runtime - 1, Math.max(0, ((e.clientX - r.left) / r.width) * (runtime - 1)))))
  }

  return (
    <div className="schedule">
      <div className="schedule-rows">
        {objects.map((o) => {
          const start = o.latency + T1_ONSET
          const end = start + o.duration
          const color = stimColor(stimIndex(o.stimulus))
          return (
            <div
              key={o.id}
              className={`schedule-row${o.id === selectedId ? ' selected' : ''}`}
              onClick={() => onSelect(o.id)}
            >
              <span className="schedule-label" style={{ color }}>{o.name}</span>
              <div
                className="schedule-track"
                onPointerDown={(e) => { e.currentTarget.setPointerCapture(e.pointerId); scrub(e) }}
                onPointerMove={(e) => { if (e.buttons & 1) scrub(e) }}
              >
                <div className="schedule-bar" style={{ left: pct(start), width: pct(end - start), background: color }} title={`${o.name}: ${start} to ${end} ms`} />
                <div className="schedule-cursor" style={{ left: pct(step) }} />
              </div>
            </div>
          )
        })}
        {objects.length === 0 && <div className="schedule-empty muted">No objects yet. Click the field to place one.</div>}
      </div>
      <div className="schedule-axis">
        <span>0</span>
        <span>{Math.round(runtime / 2)}</span>
        <span>{runtime} ms</span>
      </div>
    </div>
  )
}
