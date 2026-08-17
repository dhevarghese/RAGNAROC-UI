import { useEffect, useRef, useState } from 'react'

import { FIXED_RANGE, paintFrame, type Range } from './colormap'

interface Props {
  /** full series, row-major frames */
  data: Float32Array
  w: number
  h: number
  step: number
  /** CSS pixel size of the square canvas */
  size: number
  /** highlighted cell (1-based x, y) */
  probe?: { x: number; y: number } | null
  markers?: { x: number; y: number; color: string; active: boolean }[]
  /** pinned probes: small numbered squares */
  pins?: { x: number; y: number; color: string; label: string }[]
  onPick?: (x: number, y: number) => void
  title: string
  subtitle?: string
  /** colour range; defaults to the model's fixed activation bounds */
  range?: Range
}

/**
 * One activation map at one time step, drawn pixel-per-cell into an offscreen
 * ImageData and scaled up with crisp edges. Click to move the probe.
 */
export function Heatmap({ data, w, h, step, size, probe, markers, pins, onPick, title, subtitle, range = FIXED_RANGE }: Props) {
  const ref = useRef<HTMLCanvasElement>(null)
  const [hover, setHover] = useState<{ x: number; y: number } | null>(null)
  const imgRef = useRef<ImageData | null>(null)
  const offRef = useRef<HTMLCanvasElement | null>(null)

  useEffect(() => {
    const canvas = ref.current
    if (!canvas) return
    const dpr = window.devicePixelRatio || 1
    canvas.width = size * dpr
    canvas.height = size * dpr
    const ctx = canvas.getContext('2d')!
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)

    if (!offRef.current) offRef.current = document.createElement('canvas')
    const off = offRef.current
    off.width = w
    off.height = h
    if (!imgRef.current || imgRef.current.width !== w || imgRef.current.height !== h) {
      imgRef.current = new ImageData(w, h)
    }
    const img = imgRef.current
    const n = w * h
    paintFrame(img, data, step * n, n, range.min, range.max)
    off.getContext('2d')!.putImageData(img, 0, 0)

    ctx.imageSmoothingEnabled = false
    ctx.clearRect(0, 0, size, size)
    ctx.drawImage(off, 0, 0, size, size)

    const cell = size / w
    // object markers
    if (markers) {
      for (const m of markers) {
        const cx = (m.x - 0.5) * cell
        const cy = (m.y - 0.5) * cell
        ctx.beginPath()
        ctx.arc(cx, cy, Math.max(3, cell * 0.42), 0, Math.PI * 2)
        ctx.lineWidth = m.active ? 2 : 1
        ctx.strokeStyle = m.active ? m.color : 'rgba(255,255,255,0.35)'
        ctx.setLineDash(m.active ? [] : [2, 2])
        ctx.stroke()
        ctx.setLineDash([])
      }
    }
    // pinned probes
    if (pins) {
      for (const p of pins) {
        if (p.x < 1 || p.y < 1 || p.x > w || p.y > h) continue
        const x0 = (p.x - 1) * cell, y0 = (p.y - 1) * cell
        ctx.strokeStyle = p.color
        ctx.lineWidth = 1.5
        ctx.strokeRect(x0 + 0.75, y0 + 0.75, cell - 1.5, cell - 1.5)
        if (cell >= 9) {
          ctx.fillStyle = p.color
          ctx.font = `600 ${Math.max(8, Math.min(11, cell * 0.8))}px system-ui, sans-serif`
          ctx.textAlign = 'center'
          ctx.textBaseline = 'middle'
          ctx.fillText(p.label, x0 + cell / 2, y0 + cell / 2 + 0.5)
          ctx.textBaseline = 'alphabetic'
        }
      }
    }
    // probe crosshair
    if (probe) {
      const px = (probe.x - 1) * cell
      const py = (probe.y - 1) * cell
      ctx.strokeStyle = '#ffffff'
      ctx.lineWidth = 1.5
      ctx.strokeRect(px + 0.75, py + 0.75, cell - 1.5, cell - 1.5)
      ctx.strokeStyle = 'rgba(0,0,0,0.6)'
      ctx.lineWidth = 0.5
      ctx.strokeRect(px + 2, py + 2, cell - 4, cell - 4)
    }
  }, [data, w, h, step, size, probe, markers, pins, range])

  const cell = size / w
  const cellAt = (e: React.PointerEvent | React.MouseEvent) => {
    const r = e.currentTarget.getBoundingClientRect()
    return {
      x: Math.min(w, Math.max(1, Math.floor(((e.clientX - r.left) / r.width) * w) + 1)),
      y: Math.min(h, Math.max(1, Math.floor(((e.clientY - r.top) / r.height) * h) + 1)),
    }
  }

  return (
    <figure className="heatmap">
      <figcaption>
        <span className="heatmap-title">{title}</span>
        {subtitle && <span className="heatmap-sub">{subtitle}</span>}
      </figcaption>
      <div className="heatmap-body" style={{ width: size, height: size }}>
        <canvas
          ref={ref}
          style={{ width: size, height: size, cursor: onPick ? 'crosshair' : 'default' }}
          onClick={(e) => { if (onPick) { const c = cellAt(e); onPick(c.x, c.y) } }}
          onPointerMove={(e) => setHover(e.pointerType === 'touch' ? null : cellAt(e))}
          onPointerLeave={() => setHover(null)}
          aria-label={`${title} activation map`}
        />
        {hover && (
          <>
            <div className="cell-hover" style={{ left: (hover.x - 1) * cell, top: (hover.y - 1) * cell, width: cell, height: cell }} />
            <div className={`cell-tip${hover.y <= h / 2 ? ' below' : ''}${hover.x > w / 2 ? ' left' : ''}`}
              style={{ left: (hover.x - 0.5) * cell, top: hover.y <= h / 2 ? hover.y * cell : (hover.y - 1) * cell }}>
              ({hover.x}, {hover.y}) <b>{data[step * w * h + (hover.y - 1) * w + (hover.x - 1)].toFixed(2)}</b>
            </div>
          </>
        )}
      </div>
    </figure>
  )
}
