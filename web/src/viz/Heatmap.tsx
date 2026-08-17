import { useEffect, useRef } from 'react'

import { paintFrame } from './colormap'

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
  onPick?: (x: number, y: number) => void
  title: string
  subtitle?: string
}

/**
 * One activation map at one time step, drawn pixel-per-cell into an offscreen
 * ImageData and scaled up with crisp edges. Click to move the probe.
 */
export function Heatmap({ data, w, h, step, size, probe, markers, onPick, title, subtitle }: Props) {
  const ref = useRef<HTMLCanvasElement>(null)
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
    paintFrame(img, data, step * n, n)
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
  }, [data, w, h, step, size, probe, markers])

  return (
    <figure className="heatmap">
      <figcaption>
        <span className="heatmap-title">{title}</span>
        {subtitle && <span className="heatmap-sub">{subtitle}</span>}
      </figcaption>
      <canvas
        ref={ref}
        style={{ width: size, height: size, cursor: onPick ? 'crosshair' : 'default' }}
        onClick={(e) => {
          if (!onPick) return
          const r = e.currentTarget.getBoundingClientRect()
          const x = Math.min(w, Math.max(1, Math.floor(((e.clientX - r.left) / r.width) * w) + 1))
          const y = Math.min(h, Math.max(1, Math.floor(((e.clientY - r.top) / r.height) * h) + 1))
          onPick(x, y)
        }}
        aria-label={`${title} activation map`}
      />
    </figure>
  )
}
