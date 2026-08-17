import { useEffect, useMemo, useRef, useState } from 'react'

import type { Experiment, SimulationResult } from '../model/types'
import { stimColor } from '../state/experiment'
import { ACT_MAX, ACT_MIN, FIXED_RANGE, legendGradient, seriesRange, type Range } from '../viz/colormap'
import { Heatmap } from '../viz/Heatmap'
import { Surface3D } from '../viz/Surface3D'
import { TraceChart, type Trace } from '../viz/TraceChart'
import { T1_ONSET } from './Schedule'

type MapKind = 'AM' | 'IG' | 'EV' | 'LV' | 'II'
interface MapSel { kind: MapKind; stim: number }

interface Props {
  experiment: Experiment
  result: SimulationResult
  step: number
  setStep: (s: number) => void
  probe: { x: number; y: number }
  setProbe: (p: { x: number; y: number }) => void
  selectedObjectId: string | null
}

const SPEEDS = [0.25, 0.5, 1, 2, 4]
/** wall-clock ms per simulated ms at 1x (about 8 s for a 600 ms run) */
const MS_PER_STEP = 8
const PLAY_KEY = 'ragnaroc.playback'

const PIN_COLORS = ['#ffffff', '#7ee787', '#c792ea', '#48dbfb', '#ffa657', '#ff9ff3']
const MAX_PINS = PIN_COLORS.length

const MAP_INFO: Record<string, { title: string; blurb: string }> = {
  AM: { title: 'Attention map', blurb: 'Where attention is deployed. Above threshold (14) it amplifies input to the LV maps.' },
  IG: { title: 'Inhibitory gate', blurb: 'Driven by LV and by AM itself; when it crosses 8 it suppresses the attention map.' },
  EV: { title: 'Early visual', blurb: 'The stimulus signal on the retina-like input layer, per stimulus type.' },
  LV: { title: 'Late visual', blurb: 'EV filtered through the receptive field and boosted by attention.' },
  II: { title: 'Inhibitory interneurons', blurb: 'Local inhibition that pushes back on LV once it fires.' },
}

/**
 * Everything the model produced, laid out so time is shared: small multiples
 * of every map at the current step, an N2pc timeline that doubles as the
 * scrubber, and per-cell traces at the probe.
 */
export function Results({ experiment, result, step, setStep, probe, setProbe, selectedObjectId }: Props) {
  const { w, h, steps } = result
  const n = w * h
  const [playing, setPlaying] = useState(false)
  const [playback, setPlayback] = useState<{ speed: number; loop: boolean }>(() => {
    try { return { speed: 1, loop: true, ...JSON.parse(localStorage.getItem(PLAY_KEY) ?? '{}') } } catch { return { speed: 1, loop: true } }
  })
  const [autoRange, setAutoRange] = useState(false)
  // pinned probes: extra locations whose AM/IG traces are compared side by side
  const [pins, setPins] = useState<{ x: number; y: number }[]>([])
  const [mapSize, setMapSize] = useState(148)
  const [sel, setSel] = useState<MapSel>({ kind: 'AM', stim: 0 })
  const [surfaceW, setSurfaceW] = useState(560)
  const gridRef = useRef<HTMLDivElement>(null)
  const surfRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = surfRef.current
    if (!el) return
    const ro = new ResizeObserver(() => setSurfaceW(Math.max(320, el.clientWidth)))
    ro.observe(el)
    return () => ro.disconnect()
  }, [])

  // Fit the small multiples to the available width.
  useEffect(() => {
    const el = gridRef.current
    if (!el) return
    const ro = new ResizeObserver(() => {
      // three thumbnails + a row label per row
      const width = el.clientWidth - 22
      setMapSize(Math.max(84, Math.min(150, Math.floor((width - 2 * 12) / 3))))
    })
    ro.observe(el)
    return () => ro.disconnect()
  }, [experiment.stimulusTypes.length])

  useEffect(() => { localStorage.setItem(PLAY_KEY, JSON.stringify(playback)) }, [playback])

  // playback: advance by wall clock so speed is independent of frame rate
  const stepRef = useRef(step)
  stepRef.current = step
  useEffect(() => {
    if (!playing) return
    let raf = 0
    let last = performance.now()
    let acc = 0
    const tick = (now: number) => {
      acc += ((now - last) / MS_PER_STEP) * playback.speed
      last = now
      const advance = Math.floor(acc)
      if (advance >= 1) {
        acc -= advance
        const next = stepRef.current + advance
        if (next >= steps && !playback.loop) {
          setStep(steps - 1)
          setPlaying(false)
          return
        }
        setStep(next % steps)
      }
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [playing, steps, setStep, playback])

  const togglePlay = () => {
    // pressing play at the very end restarts from 0
    if (!playing && stepRef.current >= steps - 1) setStep(0)
    setPlaying((p) => !p)
  }

  // space toggles playback anywhere outside a text field
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      const tag = (e.target as HTMLElement)?.tagName
      if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA' || tag === 'BUTTON') return
      if (e.key === ' ') { e.preventDefault(); togglePlay() }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [playing, steps])

  // per-map colour ranges (whole run), used when "auto" is on
  const ranges = useMemo(() => ({
    AM: seriesRange(result.AM.data), IG: seriesRange(result.IG.data),
    EV: result.EV.map((m) => seriesRange(m.data)), LV: result.LV.map((m) => seriesRange(m.data)), II: result.II.map((m) => seriesRange(m.data)),
  }), [result])
  const rangeOf = (kind: MapKind, stim = 0): Range =>
    !autoRange ? FIXED_RANGE : kind === 'AM' ? ranges.AM : kind === 'IG' ? ranges.IG : ranges[kind][stim] ?? FIXED_RANGE

  const clampedStep = Math.min(step, steps - 1)
  const px = Math.min(probe.x, w), py = Math.min(probe.y, h)
  const probeIndex = (py - 1) * w + (px - 1)

  const seriesAt = (data: Float32Array) => {
    const out = new Float32Array(steps)
    for (let t = 0; t < steps; t++) out[t] = data[t * n + probeIndex]
    return out
  }

  const visiblePins = pins.filter((p) => p.x >= 1 && p.y >= 1 && p.x <= w && p.y <= h)
  const pinMarks = visiblePins.map((p, i) => ({ ...p, color: PIN_COLORS[i % PIN_COLORS.length], label: String(i + 1) }))
  const isPinned = pins.some((p) => p.x === px && p.y === py)
  const pinCurrent = () => { if (!isPinned && pins.length < MAX_PINS) setPins([...pins, { x: px, y: py }]) }
  const unpin = (i: number) => setPins(pins.filter((_, k) => k !== i))

  const pinKey = visiblePins.map((p) => `${p.x},${p.y}`).join(';')
  const pinTraces = useMemo(() => {
    const at = (data: Float32Array, x: number, y: number) => {
      const idx = (y - 1) * w + (x - 1)
      const out = new Float32Array(steps)
      for (let t = 0; t < steps; t++) out[t] = data[t * n + idx]
      return out
    }
    const am: Trace[] = visiblePins.map((p, i) => ({ label: `${i + 1} AM (${p.x}, ${p.y})`, color: PIN_COLORS[i % PIN_COLORS.length], values: at(result.AM.data, p.x, p.y) }))
    const ig: Trace[] = visiblePins.map((p, i) => ({ label: `${i + 1} IG (${p.x}, ${p.y})`, color: PIN_COLORS[i % PIN_COLORS.length], values: at(result.IG.data, p.x, p.y), dashed: true }))
    return { am, ig }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [result, pinKey])

  const stimNames = experiment.stimulusTypes.map((s) => s.name)
  const traces = useMemo(() => {
    const shared: Trace[] = [
      { label: 'AM', color: '#f5b53f', values: seriesAt(result.AM.data) },
      { label: 'IG', color: '#5ec4ff', values: seriesAt(result.IG.data) },
    ]
    const perStim: Trace[][] = experiment.stimulusTypes.map((s, i) => [
      { label: `EV ${s.name}`, color: stimColor(i), values: seriesAt(result.EV[i].data), dashed: true },
      { label: `LV ${s.name}`, color: stimColor(i), values: seriesAt(result.LV[i].data) },
      { label: `II ${s.name}`, color: 'rgba(255,255,255,0.5)', values: seriesAt(result.II[i].data), dashed: true },
    ])
    return { shared, perStim }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [result, probeIndex, stimNames.join('|')])

  const n2pcRange = useMemo(() => {
    let m = 1
    for (let t = 0; t < steps; t++) m = Math.max(m, Math.abs(result.n2pc[t]))
    return Math.ceil(m * 1.1)
  }, [result, steps])

  const bands = [
    { start: 0, end: Math.min(steps, T1_ONSET + 1), color: 'rgba(255,255,255,0.045)', label: 'settling' },
    ...experiment.objects.map((o) => {
      const i = Math.max(0, experiment.stimulusTypes.findIndex((s) => s.id === o.stimulus))
      return { start: o.latency + T1_ONSET, end: o.latency + T1_ONSET + o.duration, color: stimColor(i) + '22' }
    }),
  ]

  const markers = experiment.objects.map((o) => {
    const i = Math.max(0, experiment.stimulusTypes.findIndex((s) => s.id === o.stimulus))
    const on = clampedStep >= o.latency + T1_ONSET && clampedStep < o.latency + T1_ONSET + o.duration
    return { x: o.x, y: o.y, color: stimColor(i), active: on || o.id === selectedObjectId }
  })

  const pick = (x: number, y: number) => setProbe({ x, y })
  const probeVal = (data: Float32Array) => data[clampedStep * n + probeIndex]

  const stimCount = experiment.stimulusTypes.length
  const selStim = Math.min(sel.stim, Math.max(0, stimCount - 1))
  const selData = sel.kind === 'AM' ? result.AM.data
    : sel.kind === 'IG' ? result.IG.data
    : (sel.kind === 'EV' ? result.EV : sel.kind === 'LV' ? result.LV : result.II)[selStim].data
  const selTitle = MAP_INFO[sel.kind].title + (sel.kind === 'AM' || sel.kind === 'IG' ? '' : `: ${stimNames[selStim] ?? ''}`)
  const isSel = (kind: MapKind, stim = 0) => sel.kind === kind && (kind === 'AM' || kind === 'IG' || selStim === stim)
  const pickAndSelect = (kind: MapKind, stim = 0) => (x: number, y: number) => {
    setSel({ kind, stim })
    pick(x, y)
  }
  const surfaceMarkers = experiment.objects.map((o, i) => ({ ...markers[i], label: o.name }))
  const selRange = rangeOf(sel.kind, selStim)

  return (
    <div className="results">
      <div className="timeline">
        <div className="timeline-head">
          <div className="transport">
            <button className="btn icon" onClick={() => { setPlaying(false); setStep(0) }} title="Start" aria-label="go to start">⏮</button>
            <button className="btn icon" onClick={() => { setPlaying(false); setStep(clampedStep - 1) }} title="Back 1 ms (←)" aria-label="step back">‹</button>
            <button className="btn play" onClick={togglePlay} title="Play / pause (space)" aria-label={playing ? 'pause' : 'play'}>
              {playing ? '❚❚' : '▶'}
            </button>
            <button className="btn icon" onClick={() => { setPlaying(false); setStep(clampedStep + 1) }} title="Forward 1 ms (→)" aria-label="step forward">›</button>
            <select className="chip-select" value={playback.speed} onChange={(e) => setPlayback((p) => ({ ...p, speed: Number(e.target.value) }))} aria-label="playback speed" title="Playback speed">
              {SPEEDS.map((sp) => <option key={sp} value={sp}>{sp}x</option>)}
            </select>
            <button className={`chip${playback.loop ? ' active' : ''}`} onClick={() => setPlayback((p) => ({ ...p, loop: !p.loop }))} title="Loop at the end" aria-pressed={playback.loop}>loop</button>
          </div>
          <div className="timeline-readout">
            <span className="time-now">{clampedStep}<small> ms</small></span>
            <span className="muted small">drag the trace or the schedule to scrub, space to play, arrow keys to step. Objects can appear from {T1_ONSET + 1} ms</span>
          </div>
          <span className="muted small">simulated in {result.elapsedMs.toFixed(0)} ms</span>
        </div>
        <TraceChart
          traces={[{ label: 'N2pc (simulated EEG: left − right hemifield)', color: '#ffffff', values: result.n2pc }]}
          step={clampedStep} steps={steps} yMin={-n2pcRange} yMax={n2pcRange} height={92}
          zeroLine yLabel="N2pc" onScrub={(s) => { setPlaying(false); setStep(s) }} bands={bands}
        />
      </div>

      <div className="featured">
        <div className="featured-surface" ref={surfRef}>
          <div className="featured-head">
            <div className="map-picker" role="tablist" aria-label="map shown in 3D">
              {(['AM', 'IG'] as MapKind[]).map((k) => (
                <button key={k} role="tab" aria-selected={isSel(k)} className={`chip${isSel(k) ? ' active' : ''}`} onClick={() => setSel({ kind: k, stim: 0 })}>{k}</button>
              ))}
              {stimCount > 0 && <span className="chip-sep" />}
              {(['EV', 'LV', 'II'] as MapKind[]).map((k) => (
                <button key={k} role="tab" aria-selected={sel.kind === k} className={`chip${sel.kind === k ? ' active' : ''}`} onClick={() => setSel({ kind: k, stim: selStim })}>{k}</button>
              ))}
              {(sel.kind === 'EV' || sel.kind === 'LV' || sel.kind === 'II') && stimCount > 1 && (
                <select className="chip-select" value={selStim} onChange={(e) => setSel({ kind: sel.kind, stim: Number(e.target.value) })} aria-label="stimulus type">
                  {experiment.stimulusTypes.map((s, i) => <option key={s.id} value={i}>{s.name}</option>)}
                </select>
              )}
            </div>
            <p className="help">{MAP_INFO[sel.kind].blurb}</p>
          </div>
          <Surface3D
            title={selTitle}
            subtitle={`${probeVal(selData).toFixed(1)} at probe`}
            data={selData} w={w} h={h} step={clampedStep}
            width={surfaceW} height={Math.round(surfaceW * 0.62)}
            probe={{ x: px, y: py }} markers={surfaceMarkers} pins={pinMarks} onPick={pick}
            range={selRange}
          />
          <div className="legend legend-inline">
            <div className="legend-bar" style={{ background: legendGradient() }} />
            <div className="legend-ticks">
              <span>{fmtRange(selRange.min)}</span>
              <span className="legend-mid">
                <span title="Fixed: same scale on every map (comparable). Auto: each map stretched to its own min and max over the run (readable).">activation (height and colour), scale:</span>
                <span className="range-toggle" role="group" aria-label="colour range">
                  <button className={`chip${!autoRange ? ' active' : ''}`} onClick={() => setAutoRange(false)} title={`Same scale for every map: ${ACT_MIN} to ${ACT_MAX}`}>fixed</button>
                  <button className={`chip${autoRange ? ' active' : ''}`} onClick={() => setAutoRange(true)} title="Each map stretched to its own min and max over the whole run">auto</button>
                </span>
              </span>
              <span>{fmtRange(selRange.max)}</span>
            </div>
          </div>
        </div>

        <div className="maps" ref={gridRef}>
          <div className="maps-head">
            <h3>All maps at {clampedStep} ms</h3>
            <span className="help">click a map to feature it in 3D and move the probe</span>
          </div>
          <div className="maps-row">
            <div className={`thumb${isSel('AM') ? ' active' : ''}`}><Heatmap title={MAP_INFO.AM.title} subtitle={`${probeVal(result.AM.data).toFixed(1)} at probe`} data={result.AM.data} range={rangeOf('AM')} w={w} h={h} step={clampedStep} size={mapSize} probe={{ x: px, y: py }} markers={markers} pins={pinMarks} onPick={pickAndSelect('AM')} /></div>
            <div className={`thumb${isSel('IG') ? ' active' : ''}`}><Heatmap title={MAP_INFO.IG.title} subtitle={`${probeVal(result.IG.data).toFixed(1)} at probe`} data={result.IG.data} range={rangeOf('IG')} w={w} h={h} step={clampedStep} size={mapSize} probe={{ x: px, y: py }} markers={markers} pins={pinMarks} onPick={pickAndSelect('IG')} /></div>
          </div>
          {experiment.stimulusTypes.map((s, i) => (
            <div className="maps-row" key={s.id}>
              <div className="maps-row-label" style={{ color: stimColor(i) }}>
                <span className="swatch" style={{ background: stimColor(i) }} />{s.name}
              </div>
              <div className={`thumb${isSel('EV', i) ? ' active' : ''}`}><Heatmap title="Early visual" data={result.EV[i].data} range={rangeOf('EV', i)} w={w} h={h} step={clampedStep} size={mapSize} probe={{ x: px, y: py }} markers={markers} pins={pinMarks} onPick={pickAndSelect('EV', i)} /></div>
              <div className={`thumb${isSel('LV', i) ? ' active' : ''}`}><Heatmap title="Late visual" data={result.LV[i].data} range={rangeOf('LV', i)} w={w} h={h} step={clampedStep} size={mapSize} probe={{ x: px, y: py }} markers={markers} pins={pinMarks} onPick={pickAndSelect('LV', i)} /></div>
              <div className={`thumb${isSel('II', i) ? ' active' : ''}`}><Heatmap title="Inhib. interneurons" data={result.II[i].data} range={rangeOf('II', i)} w={w} h={h} step={clampedStep} size={mapSize} probe={{ x: px, y: py }} markers={markers} pins={pinMarks} onPick={pickAndSelect('II', i)} /></div>
            </div>
          ))}
        </div>
      </div>

      <div className="traces">
        <header className="traces-head">
          <h3>Time course at probe <span className="mono">({px}, {py})</span></h3>
          <div className="pin-bar">
            <button className="btn small" onClick={pinCurrent} disabled={isPinned || pins.length >= MAX_PINS}
              title={isPinned ? 'This cell is already pinned' : pins.length >= MAX_PINS ? `Up to ${MAX_PINS} pins` : 'Keep this location to compare it with others'}>
              📌 pin this probe
            </button>
            {pinMarks.map((p, i) => (
              <span key={i} className="pin-chip" style={{ borderColor: p.color }}>
                <button className="pin-jump" style={{ color: p.color }} onClick={() => pick(p.x, p.y)} title="Move the probe here">{p.label} ({p.x}, {p.y})</button>
                <button className="icon-btn" onClick={() => unpin(pins.indexOf(visiblePins[i]))} title="unpin" aria-label={`unpin ${p.label}`}>×</button>
              </span>
            ))}
            {pins.length > 0 && <button className="btn small" onClick={() => setPins([])}>clear</button>}
          </div>
          <span className="muted small">bands = when objects are on screen</span>
        </header>
        {pinMarks.length > 0 && (
          <div className="pin-compare">
            <h4>Pinned probes compared <span className="muted small">(AM solid, IG dashed)</span></h4>
            <TraceChart traces={[...pinTraces.am, ...pinTraces.ig]} step={clampedStep} steps={steps} yMin={ACT_MIN} yMax={ACT_MAX} height={130} zeroLine yLabel="pins" onScrub={(s) => { setPlaying(false); setStep(s) }} bands={bands} />
          </div>
        )}
        <TraceChart traces={traces.shared} step={clampedStep} steps={steps} yMin={ACT_MIN} yMax={ACT_MAX} height={120} zeroLine yLabel="AM, IG" onScrub={(s) => { setPlaying(false); setStep(s) }} bands={bands} />
        {traces.perStim.map((tr, i) => (
          <TraceChart key={i} traces={tr} step={clampedStep} steps={steps} yMin={ACT_MIN} yMax={ACT_MAX} height={110} zeroLine yLabel={stimNames[i]} onScrub={(s) => { setPlaying(false); setStep(s) }} bands={bands} />
        ))}
      </div>

      <details className="map-glossary">
        <summary>What are these maps?</summary>
        <dl>
          {Object.entries(MAP_INFO).map(([k, v]) => (
            <div key={k}><dt>{v.title} <span className="mono muted">{k}</span></dt><dd>{v.blurb}</dd></div>
          ))}
          <div><dt>N2pc</dt><dd>The simulated EEG component: summed attentional excitation minus inhibition over the left half of the field, minus the same over the right half. A lateralised target produces the characteristic deflection.</dd></div>
        </dl>
      </details>

      <details className="map-glossary">
        <summary>What are the colour ranges, fixed and auto?</summary>
        <p>Every map is drawn with the same colour ramp, from dark (low activation) to bright yellow (high). The toggle under the 3D surface decides what the ends of that ramp mean.</p>
        <dl>
          <div><dt>Fixed</dt><dd>The ramp always spans the model's activation bounds, {ACT_MIN} to {ACT_MAX}, on every map. A given colour means the same value everywhere, so you can compare maps with each other and across time. This is the default. Maps with small activations, such as early visual input or the inhibitory interneurons, look dim.</dd></div>
          <div><dt>Auto</dt><dd>Each map is stretched to its own lowest and highest value across the whole run. Faint maps become fully readable and the 3D surface uses its full height. The trade-off is that colours no longer mean the same thing from one map to the next, so read the legend numbers before comparing.</dd></div>
        </dl>
        <p>The choice affects only how results are drawn, never the simulation itself. Hovering any map shows the actual value of a cell either way.</p>
      </details>
    </div>
  )
}

const fmtRange = (v: number) => (Number.isInteger(v) ? String(v) : v.toFixed(1))
