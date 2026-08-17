import { useCallback, useEffect, useReducer, useState } from 'react'

import type { Experiment } from './model/types'
import { experimentFromLocation, initialExperiment, reducer } from './state/experiment'
import { useSimulation } from './state/useSimulation'
import { CanvasEditor } from './ui/CanvasEditor'
import { Guide } from './ui/Guide'
import { Inspector } from './ui/Inspector'
import { Landing } from './ui/Landing'
import { Results } from './ui/Results'
import { Schedule } from './ui/Schedule'
import { TopBar } from './ui/TopBar'

type Route = 'landing' | 'app'

function routeFromHash(): Route {
  const h = window.location.hash
  return h.startsWith('#/app') || h.startsWith('#e=') ? 'app' : 'landing'
}

const GUIDE_SEEN_KEY = 'ragnaroc.guide.seen'

export default function App() {
  const [route, setRoute] = useState<Route>(routeFromHash)
  const [experiment, dispatch] = useReducer(reducer, undefined, initialExperiment)
  const [guideOpen, setGuideOpen] = useState(false)

  useEffect(() => {
    const onHash = () => {
      setRoute(routeFromHash())
      const fromUrl = experimentFromLocation()
      if (fromUrl) dispatch({ type: 'replace', experiment: fromUrl })
    }
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [])

  const openApp = useCallback((exp?: Experiment) => {
    if (exp) dispatch({ type: 'replace', experiment: exp })
    window.location.hash = '#/app'
    window.scrollTo(0, 0)
    if (!localStorage.getItem(GUIDE_SEEN_KEY)) {
      setGuideOpen(true)
      localStorage.setItem(GUIDE_SEEN_KEY, '1')
    }
  }, [])

  const goLanding = useCallback(() => {
    setGuideOpen(false)
    window.location.hash = ''
    window.scrollTo(0, 0)
  }, [])

  if (route === 'landing') return <Landing onOpen={openApp} />
  return (
    <>
      <Simulator experiment={experiment} dispatch={dispatch} onGuide={() => setGuideOpen(true)} onHome={goLanding} />
      <Guide open={guideOpen} onClose={() => setGuideOpen(false)} onLanding={goLanding} />
    </>
  )
}

function Simulator({ experiment, dispatch, onGuide, onHome }: {
  experiment: Experiment
  dispatch: React.Dispatch<Parameters<typeof reducer>[1]>
  onGuide: () => void
  onHome: () => void
}) {
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
      const tag = (e.target as HTMLElement)?.tagName
      if (tag === 'INPUT' || tag === 'SELECT' || tag === 'TEXTAREA') return
      if (e.key === 'ArrowLeft') setStep(step - (e.shiftKey ? 10 : 1))
      if (e.key === 'ArrowRight') setStep(step + (e.shiftKey ? 10 : 1))
      if ((e.key === 'Delete' || e.key === 'Backspace') && selectedId) {
        dispatch({ type: 'obj/remove', id: selectedId })
        setSelectedId(null)
      }
      if (e.key === '?') onGuide()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [step, selectedId, setStep, dispatch, onGuide])

  const clampedStep = Math.min(step, experiment.runtime - 1)

  return (
    <div className="app">
      <TopBar experiment={experiment} dispatch={dispatch} status={{ ...sim, elapsedMs: sim.result?.elapsedMs }} onGuide={onGuide} onHome={onHome} />
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
