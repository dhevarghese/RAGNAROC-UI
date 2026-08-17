import { useEffect, useRef } from 'react'

export interface Trace {
  label: string
  color: string
  values: ArrayLike<number>
  /** dashed line */
  dashed?: boolean
}

interface Props {
  traces: Trace[]
  /** current time step; a marker line is drawn here */
  step: number
  steps: number
  yMin: number
  yMax: number
  height: number
  /** draw a zero line */
  zeroLine?: boolean
  /** show a y-axis label */
  yLabel?: string
  onScrub?: (step: number) => void
  /** shade the intervals [start, end) as "object visible" bands */
  bands?: { start: number; end: number; color: string; label?: string }[]
}

/**
 * Small, fast line chart on a canvas: several traces sharing an x (time) axis,
 * a movable time cursor, optional zero line and visibility bands.
 */
export function TraceChart({ traces, step, steps, yMin, yMax, height, zeroLine, yLabel, onScrub, bands }: Props) {
  const ref = useRef<HTMLCanvasElement>(null)
  const wrapRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const canvas = ref.current
    const wrap = wrapRef.current
    if (!canvas || !wrap) return
    const draw = () => {
      const width = wrap.clientWidth
      if (width <= 0) return
      const dpr = window.devicePixelRatio || 1
      canvas.width = width * dpr
      canvas.height = height * dpr
      canvas.style.width = width + 'px'
      canvas.style.height = height + 'px'
      const ctx = canvas.getContext('2d')!
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
      ctx.clearRect(0, 0, width, height)

      const padL = 34, padR = 8, padT = 6, padB = 4
      const iw = width - padL - padR
      const ih = height - padT - padB
      const xAt = (t: number) => padL + (t / Math.max(1, steps - 1)) * iw
      const yAt = (v: number) => padT + (1 - (v - yMin) / (yMax - yMin)) * ih

      // bands
      if (bands) {
        for (const b of bands) {
          ctx.fillStyle = b.color
          ctx.fillRect(xAt(b.start), padT, Math.max(1, xAt(b.end) - xAt(b.start)), ih)
          if (b.label) {
            ctx.fillStyle = 'rgba(255,255,255,0.35)'
            ctx.font = '10px ui-monospace, SFMono-Regular, Menlo, monospace'
            ctx.textAlign = 'left'
            ctx.fillText(b.label, xAt(b.start) + 4, padT + 11)
          }
        }
      }
      // frame + zero line
      ctx.strokeStyle = 'rgba(255,255,255,0.08)'
      ctx.lineWidth = 1
      ctx.strokeRect(padL + 0.5, padT + 0.5, iw - 1, ih - 1)
      if (zeroLine && yMin < 0 && yMax > 0) {
        ctx.strokeStyle = 'rgba(255,255,255,0.18)'
        ctx.setLineDash([3, 3])
        ctx.beginPath()
        ctx.moveTo(padL, yAt(0) + 0.5)
        ctx.lineTo(padL + iw, yAt(0) + 0.5)
        ctx.stroke()
        ctx.setLineDash([])
      }
      // y ticks
      ctx.fillStyle = 'rgba(255,255,255,0.45)'
      ctx.font = '10px ui-monospace, SFMono-Regular, Menlo, monospace'
      ctx.textAlign = 'right'
      ctx.textBaseline = 'middle'
      ctx.fillText(fmt(yMax), padL - 4, yAt(yMax) + 4)
      ctx.fillText(fmt(yMin), padL - 4, yAt(yMin) - 4)
      if (yLabel) {
        ctx.save()
        ctx.translate(9, padT + ih / 2)
        ctx.rotate(-Math.PI / 2)
        ctx.textAlign = 'center'
        ctx.fillStyle = 'rgba(255,255,255,0.6)'
        ctx.fillText(yLabel, 0, 0)
        ctx.restore()
      }
      // traces
      for (const tr of traces) {
        ctx.strokeStyle = tr.color
        ctx.lineWidth = 1.6
        ctx.setLineDash(tr.dashed ? [4, 3] : [])
        ctx.beginPath()
        const n = Math.min(tr.values.length, steps)
        for (let t = 0; t < n; t++) {
          const v = tr.values[t]
          const x = xAt(t)
          const y = yAt(v)
          if (t === 0) ctx.moveTo(x, y)
          else ctx.lineTo(x, y)
        }
        ctx.stroke()
        ctx.setLineDash([])
      }
      // cursor
      const cx = xAt(step) + 0.5
      ctx.strokeStyle = 'rgba(255,255,255,0.85)'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(cx, padT)
      ctx.lineTo(cx, padT + ih)
      ctx.stroke()
    }
    draw()
    const ro = new ResizeObserver(draw)
    ro.observe(wrap)
    return () => ro.disconnect()
  }, [traces, step, steps, yMin, yMax, height, zeroLine, yLabel, bands])

  const scrubFromEvent = (e: React.PointerEvent<HTMLCanvasElement>) => {
    if (!onScrub) return
    const r = e.currentTarget.getBoundingClientRect()
    const padL = 34, padR = 8
    const t = ((e.clientX - r.left - padL) / (r.width - padL - padR)) * (steps - 1)
    onScrub(Math.round(Math.min(steps - 1, Math.max(0, t))))
  }

  const at = Math.min(step, steps - 1)
  return (
    <div className="trace-row">
      <div ref={wrapRef} className="trace-wrap">
        <canvas
          ref={ref}
          style={{ cursor: onScrub ? 'ew-resize' : 'default', display: 'block' }}
          onPointerDown={(e) => {
            if (!onScrub) return
            e.currentTarget.setPointerCapture(e.pointerId)
            scrubFromEvent(e)
          }}
          onPointerMove={(e) => {
            if (onScrub && e.buttons & 1) scrubFromEvent(e)
          }}
        />
      </div>
      {/* legend lives outside the canvas so many traces never cover the data; shows the value at the cursor */}
      <ul className="trace-legend" aria-label="legend">
        {traces.map((tr, i) => (
          <li key={i} title={tr.label}>
            <span className={`trace-swatch${tr.dashed ? ' dashed' : ''}`} style={{ borderColor: tr.color }} />
            <span className="trace-label">{tr.label}</span>
            <span className="trace-value">{fmtVal(tr.values[at])}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

function fmtVal(v: number | undefined) {
  if (v === undefined || !Number.isFinite(v)) return ''
  return Math.abs(v) >= 100 ? v.toFixed(0) : v.toFixed(2)
}

function fmt(v: number) {
  return Math.abs(v) >= 100 ? v.toFixed(0) : v.toFixed(1)
}
