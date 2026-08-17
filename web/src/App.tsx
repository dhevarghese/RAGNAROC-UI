import { useCallback, useEffect, useReducer, useState } from 'react'

import { initialExperiment, reducer } from './state/experiment'
import { useSimulation } from './state/useSimulation'
import { CanvasEditor } from './ui/CanvasEditor'
import { Inspector } from './ui/Inspector'
import { Results } from './ui/Results'
import { Schedule } from './ui/Schedule'
import { TopBar } from './ui/TopBar'

export default function App() {
  const [experiment, dispatch] = useReducer(reducer, undefined, initialExperiment)
  const sim = useSimulation(experiment)
  const [step, setStepRaw] = useState(200)
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [probe, setProbe] = useState({ x: 14, y: 14 })

  const setStep = useCallback((s: number) => setStepRaw(Math.max(0, Math.min(experiment.runtime - 1, s))), [experiment.runtime])

  // keep the probe inside the canvas when it shrinks
  useEffect(() => {
    setProbe((p) => ({ x: Math.min(p.x, experiment.canvas), y: Math.min(p.y, experiment.canvas) }))
  }, [experiment.canvas])

  // when an object is selected, put the probe on it — the traces then explain that object
  useEffect(() => {
    const o = experiment.objects.find((x) => x.id === selectedId)
    if (o) setProbe({ x: o.x, y: o.y })
  }, [selectedId, experiment.objects])

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement)?.tagName === 'INPUT') return
      if (e.key === 'ArrowLeft') setStep(step - (e.shiftKey ? 10 : 1))
      if (e.key === 'ArrowRight') setStep(step + (e.shiftKey ? 10 : 1))
      if ((e.key === 'Delete' || e.key === 'Backspace') && selectedId) {
        dispatch({ type: 'obj/remove', id: selectedId })
        setSelectedId(null)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [step, selectedId, setStep])

  const clampedStep = Math.min(step, experiment.runtime - 1)

  return (
    <div className="app">
      <TopBar experiment={experiment} dispatch={dispatch} status={{ ...sim, elapsedMs: sim.result?.elapsedMs }} />
      <main className="layout">
        <aside className="side">
          <Inspector experiment={experiment} dispatch={dispatch} selectedId={selectedId} onSelect={setSelectedId} />
        </aside>
        <section className="stage">
          <div className="field-and-schedule">
            <CanvasEditor experiment={experiment} dispatch={dispatch} selectedId={selectedId} onSelect={setSelectedId} step={clampedStep} size={300} />
            <div className="schedule-col">
              <h3>Stimulus schedule</h3>
              <Schedule experiment={experiment} step={clampedStep} selectedId={selectedId} onSelect={setSelectedId} onScrub={setStep} />
              <p className="help">
                Objects can't appear before <b>100 ms</b> — the model needs that long to settle. Latency is measured from there.
              </p>
            </div>
          </div>
          {sim.result ? (
            <Results
              experiment={experiment}
              result={sim.result}
              step={clampedStep}
              setStep={setStep}
              probe={probe}
              setProbe={setProbe}
              selectedObjectId={selectedId}
            />
          ) : (
            <div className="results-empty">
              {sim.problems.length > 0 ? (
                <>
                  <h3>Almost there</h3>
                  <ul>{sim.problems.map((p) => <li key={p}>{p}</li>)}</ul>
                </>
              ) : (
                <p><span className="spinner" /> running the first simulation…</p>
              )}
            </div>
          )}
        </section>
      </main>
    </div>
  )
}
