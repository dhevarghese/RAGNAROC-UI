import { useEffect, useRef, useState } from 'react'

import { ACT_MAX, ACT_MIN, rgbAt } from './colormap'

interface Props {
  /** full series, row-major frames */
  data: Float32Array
  w: number
  h: number
  step: number
  width: number
  height: number
  probe?: { x: number; y: number } | null
  markers?: { x: number; y: number; color: string; active: boolean; label: string }[]
  onPick?: (x: number, y: number) => void
  title: string
  subtitle?: string
}

/**
 * A 3-D surface of one activation map at one time step, rendered on a plain
 * 2-D canvas: orthographic camera, painter's-algorithm depth sort, Lambert
 * shading, colour from the shared activation colormap. Drag to orbit, click
 * to move the probe. No WebGL, no dependencies, ~2 ms per frame at 27×27.
 */
export function Surface3D({ data, w, h, step, width, height, probe, markers, onPick, title, subtitle }: Props) {
  const ref = useRef<HTMLCanvasElement>(null)
  const [azimuth, setAzimuth] = useState(-0.65)
  const [elevation, setElevation] = useState(0.55)
  const dragRef = useRef<{ x: number; y: number; moved: boolean } | null>(null)
  // projected cell centres for picking, filled during draw
  const centersRef = useRef<Float32Array>(new Float32Array(0))

  useEffect(() => {
    const canvas = ref.current
    if (!canvas) return
    const dpr = window.devicePixelRatio || 1
    canvas.width = width * dpr
    canvas.height = height * dpr
    const ctx = canvas.getContext('2d')!
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    ctx.clearRect(0, 0, width, height)

    const n = w * h
    const base = step * n
    const zRange = ACT_MAX - ACT_MIN
    const zScale = Math.max(w, h) * 0.55 // world height of the full activation range

    const ca = Math.cos(azimuth), sa = Math.sin(azimuth)
    const ce = Math.cos(elevation), se = Math.sin(elevation)
    // fit: the rotated footprint's half-extent is at most (w+h)/2 * ~0.71 → use diagonal
    const diag = Math.hypot(w, h)
    const scale = Math.min(width / (diag * 1.15), height / (diag * 0.75 * se + zScale * ce + diag * 0.25))
    const cx = width / 2
    const cy = height * 0.56

    // project world (X right, Y away, Z up) → screen; also return depth (larger = farther)
    const project = (X: number, Y: number, Z: number): [number, number, number] => {
      const x1 = X * ca - Y * sa
      const y1 = X * sa + Y * ca
      const sx = cx + x1 * scale
      const sy = cy + (y1 * se - Z * ce) * scale
      const depth = y1 * ce + Z * se
      return [sx, sy, -depth]
    }
    const worldX = (x: number) => x - w / 2 // x in [0..w] cell edges
    const worldY = (y: number) => y - h / 2
    const worldZ = (v: number) => ((v - ACT_MIN) / zRange) * zScale
    const val = (x: number, y: number) => data[base + y * w + x]

    // ---- base plane grid -------------------------------------------------
    ctx.lineWidth = 1
    ctx.strokeStyle = 'rgba(255,255,255,0.07)'
    const every = w > 30 ? 5 : w > 15 ? 3 : 1
    ctx.beginPath()
    for (let x = 0; x <= w; x += every) {
      const [ax, ay] = project(worldX(x), worldY(0), 0)
      const [bx, by] = project(worldX(x), worldY(h), 0)
      ctx.moveTo(ax, ay); ctx.lineTo(bx, by)
    }
    for (let y = 0; y <= h; y += every) {
      const [ax, ay] = project(worldX(0), worldY(y), 0)
      const [bx, by] = project(worldX(w), worldY(y), 0)
      ctx.moveTo(ax, ay); ctx.lineTo(bx, by)
    }
    ctx.stroke()
    // resting-level plane (AM rests at 5) helps read height
    ctx.strokeStyle = 'rgba(255,255,255,0.14)'
    ctx.beginPath()
    const z0 = worldZ(0)
    const corners = [[0, 0], [w, 0], [w, h], [0, h], [0, 0]]
    corners.forEach(([x, y], i) => {
      const [px, py] = project(worldX(x), worldY(y), z0)
      if (i === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py)
    })
    ctx.stroke()

    // ---- quads, painter sorted ---------------------------------------------
    type Quad = { d: number; pts: number[]; r: number; g: number; b: number; shade: number; x: number; y: number }
    const quads: Quad[] = []
    // light from upper-left-front
    const L = normalize([-0.4, -0.6, 0.7])
    for (let y = 0; y < h - 1; y++) {
      for (let x = 0; x < w - 1; x++) {
        const v00 = val(x, y), v10 = val(x + 1, y), v11 = val(x + 1, y + 1), v01 = val(x, y + 1)
        const z00 = worldZ(v00), z10 = worldZ(v10), z11 = worldZ(v11), z01 = worldZ(v01)
        // cell centres sit at x+0.5; corners of the quad are the four cell centres
        const X0 = worldX(x + 0.5), X1 = worldX(x + 1.5)
        const Y0 = worldY(y + 0.5), Y1 = worldY(y + 1.5)
        const p00 = project(X0, Y0, z00), p10 = project(X1, Y0, z10), p11 = project(X1, Y1, z11), p01 = project(X0, Y1, z01)
        const d = (p00[2] + p10[2] + p11[2] + p01[2]) / 4
        // surface normal from the height gradient across the quad
        const gx = ((v10 + v11) - (v00 + v01)) / 2 / zRange * zScale
        const gy = ((v01 + v11) - (v00 + v10)) / 2 / zRange * zScale
        const nrm = normalize([-gx, -gy, 1])
        const lambert = Math.max(0, nrm[0] * L[0] + nrm[1] * L[1] + nrm[2] * L[2])
        const [r, g, b] = rgbAt((v00 + v10 + v11 + v01) / 4)
        quads.push({ d, pts: [p00[0], p00[1], p10[0], p10[1], p11[0], p11[1], p01[0], p01[1]], r, g, b, shade: 0.55 + 0.45 * lambert, x, y })
      }
    }
    quads.sort((a, b) => b.d - a.d)
    for (const q of quads) {
      ctx.fillStyle = `rgb(${(q.r * q.shade) | 0},${(q.g * q.shade) | 0},${(q.b * q.shade) | 0})`
      ctx.beginPath()
      ctx.moveTo(q.pts[0], q.pts[1]); ctx.lineTo(q.pts[2], q.pts[3]); ctx.lineTo(q.pts[4], q.pts[5]); ctx.lineTo(q.pts[6], q.pts[7])
      ctx.closePath()
      ctx.fill()
      // hairline edges give the mesh definition without a heavy wireframe
      ctx.strokeStyle = 'rgba(0,0,0,0.18)'
      ctx.lineWidth = 0.5
      ctx.stroke()
    }

    // ---- cell centres for picking + probe + markers -----------------------
    const centers = new Float32Array(n * 2)
    for (let y = 0; y < h; y++) {
      for (let x = 0; x < w; x++) {
        const [sx, sy] = project(worldX(x + 0.5), worldY(y + 0.5), worldZ(val(x, y)))
        centers[(y * w + x) * 2] = sx
        centers[(y * w + x) * 2 + 1] = sy
      }
    }
    centersRef.current = centers

    if (markers) {
      for (const m of markers) {
        const x = m.x - 1, y = m.y - 1
        if (x < 0 || y < 0 || x >= w || y >= h) continue
        const [bx, by] = project(worldX(x + 0.5), worldY(y + 0.5), 0)
        const [tx, ty] = project(worldX(x + 0.5), worldY(y + 0.5), worldZ(val(x, y)))
        ctx.strokeStyle = m.active ? m.color : 'rgba(255,255,255,0.35)'
        ctx.setLineDash(m.active ? [] : [3, 3])
        ctx.lineWidth = 1.2
        ctx.beginPath(); ctx.moveTo(bx, by); ctx.lineTo(tx, ty); ctx.stroke()
        ctx.setLineDash([])
        ctx.fillStyle = m.active ? m.color : 'rgba(255,255,255,0.5)'
        ctx.beginPath(); ctx.arc(tx, ty, 3.5, 0, Math.PI * 2); ctx.fill()
        ctx.fillStyle = m.color
        ctx.font = '600 11px system-ui, sans-serif'
        ctx.textAlign = 'center'
        ctx.fillText(m.label, tx, ty - 8)
      }
    }
    if (probe) {
      const x = Math.min(w, probe.x) - 1, y = Math.min(h, probe.y) - 1
      const [sx, sy] = project(worldX(x + 0.5), worldY(y + 0.5), worldZ(val(x, y)))
      ctx.strokeStyle = '#fff'
      ctx.lineWidth = 1.5
      ctx.beginPath(); ctx.arc(sx, sy, 5, 0, Math.PI * 2); ctx.stroke()
      ctx.beginPath(); ctx.moveTo(sx - 9, sy); ctx.lineTo(sx + 9, sy); ctx.moveTo(sx, sy - 9); ctx.lineTo(sx, sy + 9); ctx.stroke()
    }

    // ---- axis labels -------------------------------------------------------
    ctx.fillStyle = 'rgba(255,255,255,0.55)'
    ctx.font = '11px ui-monospace, monospace'
    ctx.textAlign = 'center'
    const [lx, ly] = project(worldX(w / 2), worldY(-1.5), 0); ctx.fillText('x →', lx, ly)
    const [mx, my] = project(worldX(w + 1.8), worldY(h / 2), 0); ctx.fillText('y ↓', mx, my)
    const [zx, zy] = project(worldX(-1.5), worldY(-1), worldZ(ACT_MAX)); ctx.fillText(`${ACT_MAX}`, zx, zy)
    const [z0x, z0y] = project(worldX(-1.5), worldY(-1), 0); ctx.fillText(`${ACT_MIN}`, z0x, z0y)
  }, [data, w, h, step, width, height, azimuth, elevation, probe, markers])

  return (
    <figure className="surface3d">
      <figcaption>
        <div>
          <span className="heatmap-title">{title}</span>
          {subtitle && <span className="heatmap-sub">, {subtitle}</span>}
        </div>
        <span className="muted small">drag to orbit, click to move the probe</span>
      </figcaption>
      <canvas
        ref={ref}
        style={{ width, height, display: 'block', cursor: 'grab', touchAction: 'none' }}
        onPointerDown={(e) => {
          e.currentTarget.setPointerCapture(e.pointerId)
          dragRef.current = { x: e.clientX, y: e.clientY, moved: false }
        }}
        onPointerMove={(e) => {
          const d = dragRef.current
          if (!d) return
          const dx = e.clientX - d.x, dy = e.clientY - d.y
          if (Math.abs(dx) + Math.abs(dy) > 2) d.moved = true
          d.x = e.clientX; d.y = e.clientY
          setAzimuth((a) => a + dx * 0.008)
          setElevation((el) => Math.min(1.45, Math.max(0.12, el + dy * 0.008)))
        }}
        onPointerUp={(e) => {
          const d = dragRef.current
          dragRef.current = null
          if (!d || d.moved || !onPick) return
          const r = e.currentTarget.getBoundingClientRect()
          const px = e.clientX - r.left, py = e.clientY - r.top
          const c = centersRef.current
          let best = -1, bd = Infinity
          for (let i = 0; i < c.length / 2; i++) {
            const dd = (c[i * 2] - px) ** 2 + (c[i * 2 + 1] - py) ** 2
            if (dd < bd) { bd = dd; best = i }
          }
          if (best >= 0 && bd < 20 * 20) onPick((best % w) + 1, Math.floor(best / w) + 1)
        }}
        aria-label={`${title} 3-D surface`}
      />
    </figure>
  )
}

function normalize(v: number[]): number[] {
  const l = Math.hypot(v[0], v[1], v[2]) || 1
  return [v[0] / l, v[1] / l, v[2] / l]
}
