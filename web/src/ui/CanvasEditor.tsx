import { useRef, useState } from 'react'

import type { Experiment } from '../model/types'
import { stimColor, type Action } from '../state/experiment'

interface Props {
  experiment: Experiment
  dispatch: (a: Action) => void
  selectedId: string | null
  onSelect: (id: string | null) => void
  /** current time step, to show which objects are on screen right now */
  step: number
  size: number
}

/**
 * The visual field. Click an empty cell to place a new object (using the
 * selected object's stimulus type, or the first one), drag an object to move
 * it, click one to select it. Objects that are on-screen at the current time
 * step are drawn solid; the others hollow.
 */
export function CanvasEditor({ experiment, dispatch, selectedId, onSelect, step, size }: Props) {
  const { canvas, objects, stimulusTypes } = experiment
  const cell = size / canvas
  const svgRef = useRef<SVGSVGElement>(null)
  const [drag, setDrag] = useState<{ id: string; moved: boolean } | null>(null)
  const [hover, setHover] = useState<{ x: number; y: number } | null>(null)

  const cellFromEvent = (e: React.PointerEvent | React.MouseEvent) => {
    const r = svgRef.current!.getBoundingClientRect()
    const x = Math.min(canvas, Math.max(1, Math.floor(((e.clientX - r.left) / r.width) * canvas) + 1))
    const y = Math.min(canvas, Math.max(1, Math.floor(((e.clientY - r.top) / r.height) * canvas) + 1))
    return { x, y }
  }

  const stimIndex = (id: string) => Math.max(0, stimulusTypes.findIndex((s) => s.id === id))
  const isOn = (o: (typeof objects)[number]) => step >= o.latency + 99 && step < o.latency + o.duration + 99

  const gridLines: number[] = []
  const every = canvas > 30 ? 5 : canvas > 15 ? 3 : 1
  for (let i = every; i < canvas; i += every) gridLines.push(i)

  return (
    <div className="canvas-editor">
      <svg
        ref={svgRef}
        width={size}
        height={size}
        viewBox={`0 0 ${size} ${size}`}
        className="field"
        onPointerMove={(e) => {
          const c = cellFromEvent(e)
          setHover(c)
          if (drag) {
            const o = objects.find((x) => x.id === drag.id)
            if (o && (o.x !== c.x || o.y !== c.y)) {
              dispatch({ type: 'obj/update', id: drag.id, patch: { x: c.x, y: c.y } })
              setDrag({ id: drag.id, moved: true })
            }
          }
        }}
        onPointerLeave={() => setHover(null)}
        onPointerUp={(e) => {
          if (drag) {
            e.currentTarget.releasePointerCapture(e.pointerId)
            setDrag(null)
          }
        }}
        onClick={(e) => {
          if (drag) return
          const c = cellFromEvent(e)
          const hit = objects.find((o) => o.x === c.x && o.y === c.y)
          if (hit) {
            onSelect(hit.id)
            return
          }
          if (stimulusTypes.length === 0) return
          const sel = objects.find((o) => o.id === selectedId)
          const stimulus = sel?.stimulus ?? stimulusTypes[0].id
          dispatch({ type: 'obj/add', obj: { x: c.x, y: c.y, stimulus, latency: sel?.latency ?? 0, duration: sel?.duration ?? 100 } })
        }}
        role="application"
        aria-label={`Visual field, ${canvas} by ${canvas} cells. Click to place an object.`}
      >
        <rect width={size} height={size} className="field-bg" rx={6} />
        {gridLines.map((i) => (
          <g key={i} className="field-grid">
            <line x1={i * cell} y1={0} x2={i * cell} y2={size} />
            <line x1={0} y1={i * cell} x2={size} y2={i * cell} />
          </g>
        ))}
        {/* fixation cross at the centre */}
        <g className="field-fixation" transform={`translate(${size / 2} ${size / 2})`}>
          <line x1={-5} y1={0} x2={5} y2={0} />
          <line x1={0} y1={-5} x2={0} y2={5} />
        </g>
        {hover && !drag && !objects.some((o) => o.x === hover.x && o.y === hover.y) && (
          <rect className="field-hover" x={(hover.x - 1) * cell} y={(hover.y - 1) * cell} width={cell} height={cell} />
        )}
        {objects.map((o) => {
          const color = stimColor(stimIndex(o.stimulus))
          const on = isOn(o)
          const cx = (o.x - 0.5) * cell
          const cy = (o.y - 0.5) * cell
          const r = Math.max(6, cell * 0.45)
          const selected = o.id === selectedId
          return (
            <g
              key={o.id}
              className={`field-obj${selected ? ' selected' : ''}${on ? ' on' : ''}`}
              transform={`translate(${cx} ${cy})`}
              onPointerDown={(e) => {
                e.stopPropagation()
                e.currentTarget.ownerSVGElement?.setPointerCapture(e.pointerId)
                onSelect(o.id)
                setDrag({ id: o.id, moved: false })
              }}
              style={{ cursor: 'grab' }}
            >
              {selected && <circle r={r + 4} className="field-obj-ring" />}
              <circle r={r} fill={on ? color : 'transparent'} stroke={color} strokeWidth={on ? 1.5 : 2} strokeDasharray={on ? undefined : '3 2'} />
              <text y={-r - 5} textAnchor="middle" className="field-obj-label" fill={color}>
                {o.name}
              </text>
            </g>
          )
        })}
      </svg>
      <div className="field-caption">
        <span>
          {hover ? `x ${hover.x}, y ${hover.y}` : `${canvas} × ${canvas} cells`}
        </span>
        <span className="muted">{selectedId ? 'arrows nudge the selected object, Esc deselects, Delete removes' : 'click an empty cell to add, drag to move'}</span>
      </div>
    </div>
  )
}
