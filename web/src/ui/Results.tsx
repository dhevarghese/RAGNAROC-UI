import { useEffect, useMemo, useRef, useState } from 'react'

import type { Experiment, SimulationResult } from '../model/types'
import { stimColor } from '../state/experiment'
import { ACT_MAX, ACT_MIN, legendGradient } from '../viz/colormap'
import { Heatmap } from '../viz/Heatmap'
import { TraceChart, type Trace } from '../viz/TraceChart'
import { T1_ONSET } from './Schedule'

interface Props {
  experiment: Experiment
  result: SimulationResult
  step: number
  setStep: (s: number) => void
  probe: { x: number; y: number }
  setProbe: (p: { x: number; y: number }) => void
  selectedObjectId: string | null
}

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
  const [mapSize, setMapSize] = useState(148)
  const gridRef = useRef<HTMLDivElement>(null)

  // Fit the small multiples to the available width.
  useEffect(() => {
    const el = gridRef.current
    if (!el) return
    const ro = new ResizeObserver(() => {
      const width = el.clientWidth
      const perStim = experiment.stimulusTypes.length
      const count = 2 + perStim * 3
      // aim for at most one row of shared maps + one row per stimulus, ~5 tiles per row max
      const cols = Math.min(count, Math.max(3, Math.floor(width / 170)))
      setMapSize(Math.max(96, Math.floor((width - (cols - 1) * 14) / cols)))
    })
    ro.observe(el)
    return () => ro.disconnect()
  }, [experiment.stimulusTypes.length])

  // playback
  useEffect(() => {
    if (!playing) return
    let raf = 0
    let last = performance.now()
    const tick = (now: number) => {
      const dt = now - last
      if (dt > 16) {
        last = now
        setStep((step + Math.max(1, Math.round(dt / 8))) % steps)
      }
      raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [playing, step, steps, setStep])

  const clampedStep = Math.min(step, steps - 1)
  const px = Math.min(probe.x, w), py = Math.min(probe.y, h)
  const probeIndex = (py - 1) * w + (px - 1)

  const seriesAt = (data: Float32Array) => {
    const out = new Float32Array(steps)
    for (let t = 0; t < steps; t++) out[t] = data[t * n + probeIndex]
    return out
  }

  const stimNames = experiment.stimulusTypes.map((s) => s.name)
  const traces = useMemo(() => {
    const shared: Trace[] = [
      { label: 'AM', color: '#f5b53f', values: seriesAt(result.AM.data) },
      { label: 'IG', color: '#5ec4ff', values: seriesAt(result.IG.data) },
    ]
    const perStim: Trace[][] = experiment.stimulusTypes.map((s, i) => [
      { label: `EV · ${s.name}`, color: stimColor(i), values: seriesAt(result.EV[i].data), dashed: true },
      { label: `LV · ${s.name}`, color: stimColor(i), values: seriesAt(result.LV[i].data) },
      { label: `II · ${s.name}`, color: 'rgba(255,255,255,0.5)', values: seriesAt(result.II[i].data), dashed: true },
    ])
    return { shared, perStim }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [result, probeIndex, stimNames.join('|')])

  const n2pcRange = useMemo(() => {
    let m = 1
    for (let t = 0; t < steps; t++) m = Math.max(m, Math.abs(result.n2pc[t]))
    return Math.ceil(m * 1.1)
  }, [result, steps])

  const bands = experiment.objects.map((o) => {
    const i = Math.max(0, experiment.stimulusTypes.findIndex((s) => s.id === o.stimulus))
    return { start: o.latency + T1_ONSET, end: o.latency + T1_ONSET + o.duration, color: stimColor(i) + '22' }
  })

  const markers = experiment.objects.map((o) => {
    const i = Math.max(0, experiment.stimulusTypes.findIndex((s) => s.id === o.stimulus))
    const on = clampedStep >= o.latency + T1_ONSET && clampedStep < o.latency + T1_ONSET + o.duration
    return { x: o.x, y: o.y, color: stimColor(i), active: on || o.id === selectedObjectId }
  })

  const pick = (x: number, y: number) => setProbe({ x, y })
  const probeVal = (data: Float32Array) => data[clampedStep * n + probeIndex]

  return (
    <div className="results">
      <div className="timeline">
        <div className="timeline-head">
          <button className="btn play" onClick={() => setPlaying((p) => !p)} aria-label={playing ? 'pause' : 'play'}>
            {playing ? '❚❚' : '▶'}
          </button>
          <div className="timeline-readout">
            <span className="time-now">{clampedStep}<small> ms</small></span>
            <span className="muted small">drag the trace or the schedule to scrub · objects can appear from {T1_ONSET + 1} ms</span>
          </div>
          <span className="muted small">simulated in {result.elapsedMs.toFixed(0)} ms</span>
        </div>
        <TraceChart
          traces={[{ label: 'N2pc (simulated EEG: left − right hemifield)', color: '#ffffff', values: result.n2pc }]}
          step={clampedStep} steps={steps} yMin={-n2pcRange} yMax={n2pcRange} height={92}
          zeroLine yLabel="N2pc" onScrub={(s) => { setPlaying(false); setStep(s) }} bands={bands}
        />
      </div>

      <div className="maps" ref={gridRef}>
        <div className="maps-row">
          <Heatmap title={MAP_INFO.AM.title} subtitle={`${probeVal(result.AM.data).toFixed(1)} at probe`} data={result.AM.data} w={w} h={h} step={clampedStep} size={mapSize} probe={{ x: px, y: py }} markers={markers} onPick={pick} />
          <Heatmap title={MAP_INFO.IG.title} subtitle={`${probeVal(result.IG.data).toFixed(1)} at probe`} data={result.IG.data} w={w} h={h} step={clampedStep} size={mapSize} probe={{ x: px, y: py }} markers={markers} onPick={pick} />
          <div className="legend">
            <div className="legend-bar" style={{ background: legendGradient() }} />
            <div className="legend-ticks"><span>{ACT_MIN}</span><span>activation</span><span>{ACT_MAX}</span></div>
            <p className="help">Click any map to move the probe (white square). Rings mark object positions; solid when on screen.</p>
          </div>
        </div>
        {experiment.stimulusTypes.map((s, i) => (
          <div className="maps-row" key={s.id}>
            <div className="maps-row-label" style={{ color: stimColor(i) }}>
              <span className="swatch" style={{ background: stimColor(i) }} />{s.name}
            </div>
            <Heatmap title="Early visual" data={result.EV[i].data} w={w} h={h} step={clampedStep} size={mapSize} probe={{ x: px, y: py }} markers={markers} onPick={pick} />
            <Heatmap title="Late visual" data={result.LV[i].data} w={w} h={h} step={clampedStep} size={mapSize} probe={{ x: px, y: py }} markers={markers} onPick={pick} />
            <Heatmap title="Inhib. interneurons" data={result.II[i].data} w={w} h={h} step={clampedStep} size={mapSize} probe={{ x: px, y: py }} markers={markers} onPick={pick} />
          </div>
        ))}
      </div>

      <div className="traces">
        <header className="traces-head">
          <h3>Time course at probe <span className="mono">({px}, {py})</span></h3>
          <span className="muted small">bands = when objects are on screen</span>
        </header>
        <TraceChart traces={traces.shared} step={clampedStep} steps={steps} yMin={ACT_MIN} yMax={ACT_MAX} height={120} zeroLine yLabel="AM · IG" onScrub={(s) => { setPlaying(false); setStep(s) }} bands={bands} />
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
    </div>
  )
}
