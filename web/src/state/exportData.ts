/**
 * Export helpers: experiment JSON (and import), CSV of time courses and map
 * frames, PNG sheets of the maps. Everything happens in the browser; files are
 * handed to the user through a temporary object URL.
 */
import type { Experiment, SimulationResult } from '../model/types'
import { T1_ONSET } from '../ui/Schedule'
import { paintFrame, type Range } from '../viz/colormap'

export function download(filename: string, blob: Blob) {
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  setTimeout(() => URL.revokeObjectURL(url), 1000)
}

/** A filesystem-friendly version of the experiment name. */
export function slug(name: string): string {
  const s = name.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '')
  return s || 'experiment'
}

// ---- JSON --------------------------------------------------------------------

export interface ExperimentFile { format: 'ragnaroc-experiment'; version: 1; experiment: Experiment }

export function experimentJson(exp: Experiment): string {
  const file: ExperimentFile = { format: 'ragnaroc-experiment', version: 1, experiment: exp }
  return JSON.stringify(file, null, 2)
}

/** Accepts our wrapper format or a bare Experiment object. Returns null if unusable. */
export function parseExperimentJson(text: string): Experiment | null {
  try {
    const raw = JSON.parse(text) as unknown
    const exp = (raw && typeof raw === 'object' && 'experiment' in raw ? (raw as ExperimentFile).experiment : raw) as Partial<Experiment>
    if (!exp || !Array.isArray(exp.stimulusTypes) || !Array.isArray(exp.objects)) return null
    return {
      name: String(exp.name ?? 'Imported experiment'),
      runtime: Number(exp.runtime ?? 600), canvas: Number(exp.canvas ?? 27), mask: Number(exp.mask ?? 3),
      stimulusTypes: exp.stimulusTypes.map((s, i) => ({
        id: String(s.id ?? `s${i}`), name: String(s.name ?? `stimulus ${i + 1}`), td: Number(s.td), bu: Number(s.bu),
      })),
      objects: exp.objects.map((o, i) => ({
        id: String(o.id ?? `o${i}`), name: String(o.name ?? `obj ${i + 1}`), x: Number(o.x), y: Number(o.y),
        latency: Number(o.latency ?? 0), duration: Number(o.duration ?? 100), stimulus: String(o.stimulus ?? ''),
      })),
    }
  } catch {
    return null
  }
}

// ---- CSV ---------------------------------------------------------------------

const csvCell = (s: string) => (/[",\n]/.test(s) ? `"${s.replace(/"/g, '""')}"` : s)

/**
 * One row per simulated ms: N2pc, AM/IG at the probe, EV/LV/II per stimulus at
 * the probe, and AM/IG at every pinned probe.
 */
export function tracesCsv(exp: Experiment, r: SimulationResult, probe: { x: number; y: number }, pins: { x: number; y: number }[]): string {
  const n = r.w * r.h
  const idx = (p: { x: number; y: number }) => (p.y - 1) * r.w + (p.x - 1)
  const at = (p: { x: number; y: number }) => `x${p.x}y${p.y}`
  const cols: { name: string; data: Float32Array | Float64Array; at: number }[] = [
    { name: 'n2pc', data: r.n2pc, at: -1 },
    { name: `AM@${at(probe)}`, data: r.AM.data, at: idx(probe) },
    { name: `IG@${at(probe)}`, data: r.IG.data, at: idx(probe) },
  ]
  exp.stimulusTypes.forEach((s, i) => {
    cols.push({ name: `EV[${s.name}]@${at(probe)}`, data: r.EV[i].data, at: idx(probe) })
    cols.push({ name: `LV[${s.name}]@${at(probe)}`, data: r.LV[i].data, at: idx(probe) })
    cols.push({ name: `II[${s.name}]@${at(probe)}`, data: r.II[i].data, at: idx(probe) })
  })
  pins.forEach((p) => {
    cols.push({ name: `AM@${at(p)}`, data: r.AM.data, at: idx(p) })
    cols.push({ name: `IG@${at(p)}`, data: r.IG.data, at: idx(p) })
  })
  const lines = ['t_ms,' + cols.map((c) => csvCell(c.name)).join(',')]
  for (let t = 0; t < r.steps; t++) {
    const row = [String(t)]
    for (const c of cols) row.push(fmt(c.at < 0 ? c.data[t] : c.data[t * n + c.at]))
    lines.push(row.join(','))
  }
  return lines.join('\n') + '\n'
}

/** One map at one step as a w×h grid (row y, column x), 1-based coordinates in the header. */
export function frameCsv(data: Float32Array, w: number, h: number, step: number): string {
  const n = w * h
  const lines = ['y\\x,' + Array.from({ length: w }, (_, x) => String(x + 1)).join(',')]
  for (let y = 0; y < h; y++) {
    const row = [String(y + 1)]
    for (let x = 0; x < w; x++) row.push(fmt(data[step * n + y * w + x]))
    lines.push(row.join(','))
  }
  return lines.join('\n') + '\n'
}

const fmt = (v: number) => (Number.isFinite(v) ? String(+v.toPrecision(7)) : '')

// ---- PNG ---------------------------------------------------------------------

export interface SheetMap { title: string; data: Float32Array; range: Range }

/**
 * Every map at one step on a single labelled sheet: a row of AM and IG, then a
 * row per stimulus type (EV, LV, II). Rendered crisp at `cellPx` per cell.
 */
export function mapsSheetPng(
  exp: Experiment, r: SimulationResult, step: number,
  rows: { label: string; maps: SheetMap[] }[],
  cellPx = 12,
): Promise<Blob> {
  const { w, h } = r
  const n = w * h
  const mapW = w * cellPx, mapH = h * cellPx
  const pad = 16, labelH = 22, rowLabelW = 110, titleH = 44
  const cols = Math.max(...rows.map((row) => row.maps.length))
  const W = rowLabelW + cols * (mapW + pad) + pad
  const H = titleH + rows.length * (labelH + mapH + pad) + pad
  const canvas = document.createElement('canvas')
  canvas.width = W; canvas.height = H
  const ctx = canvas.getContext('2d')!
  ctx.fillStyle = '#0f1116'; ctx.fillRect(0, 0, W, H)
  const title = `${exp.name}: all maps at ${step} ms`
  ctx.fillStyle = '#e8eaf0'; ctx.font = '600 16px system-ui, sans-serif'; ctx.textBaseline = 'top'
  ctx.fillText(title, pad, 12)
  const titleW = ctx.measureText(title).width
  ctx.font = '12px system-ui, sans-serif'; ctx.fillStyle = 'rgba(255,255,255,0.55)'
  ctx.fillText(`canvas ${w} x ${h}, runtime ${r.steps} ms, mask ${exp.mask}. Ragnaroc simulator.`, pad + titleW + 16, 15)

  const off = document.createElement('canvas'); off.width = w; off.height = h
  const octx = off.getContext('2d')!
  const img = new ImageData(w, h)
  ctx.imageSmoothingEnabled = false
  rows.forEach((row, ri) => {
    const y0 = titleH + ri * (labelH + mapH + pad)
    ctx.fillStyle = '#e8eaf0'; ctx.font = '600 13px system-ui, sans-serif'
    ctx.fillText(row.label, pad, y0 + labelH + 4)
    row.maps.forEach((m, ci) => {
      const x0 = rowLabelW + ci * (mapW + pad)
      ctx.fillStyle = 'rgba(255,255,255,0.75)'; ctx.font = '12px system-ui, sans-serif'
      ctx.fillText(`${m.title}  [${fmtR(m.range.min)} to ${fmtR(m.range.max)}]`, x0, y0 + 4)
      paintFrame(img, m.data, step * n, n, m.range.min, m.range.max)
      octx.putImageData(img, 0, 0)
      ctx.drawImage(off, x0, y0 + labelH, mapW, mapH)
      // object markers
      ctx.lineWidth = 1.5
      for (const o of exp.objects) {
        const on = step >= o.latency + T1_ONSET && step < o.latency + T1_ONSET + o.duration
        ctx.strokeStyle = on ? '#ffffff' : 'rgba(255,255,255,0.35)'
        ctx.beginPath()
        ctx.arc(x0 + (o.x - 0.5) * cellPx, y0 + labelH + (o.y - 0.5) * cellPx, Math.max(3, cellPx * 0.45), 0, Math.PI * 2)
        ctx.stroke()
      }
    })
  })
  return new Promise((resolve, reject) => canvas.toBlob((b) => (b ? resolve(b) : reject(new Error('PNG encoding failed'))), 'image/png'))
}

const fmtR = (v: number) => (Number.isInteger(v) ? String(v) : v.toFixed(1))

/** Snapshot of an on-screen canvas (the 3D surface) as PNG. */
export function canvasPng(canvas: HTMLCanvasElement): Promise<Blob> {
  return new Promise((resolve, reject) => canvas.toBlob((b) => (b ? resolve(b) : reject(new Error('PNG encoding failed'))), 'image/png'))
}
