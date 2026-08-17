import { useCallback, useEffect, useReducer, useState } from 'react'

import type { Experiment } from './model/types'
import {
  experimentFromLocation, historyReducer, initialExperiment, initialHistory, loadDraft, outOfBounds, saveDraft,
  type Action, type HistoryAction,
} from './state/experiment'
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
const DRAFT_SAVE_MS = 400

export interface UndoState { canUndo: boolean; canRedo: boolean; undo: () => void; redo: () => void }

export default function App() {
  const [route, setRoute] = useState<Route>(routeFromHash)
  const [history, rawDispatch] = useReducer(historyReducer, undefined, () => initialHistory(initialExperiment()))
  const [guideOpen, setGuideOpen] = useState(false)
  const [hasDraft] = useState(() => loadDraft() !== null)
  const experiment = history.present

  // Timestamp edits here so the reducer stays pure but can still coalesce a drag or a typing run.
  const dispatch = useCallback((a: HistoryAction) => rawDispatch({ ...a, now: performance.now() }), [])
  const undo = useCallback(() => rawDispatch({ type: 'undo' }), [])
  const redo = useCallback(() => rawDispatch({ type: 'redo' }), [])
  const undoState: UndoState = { canUndo: history.past.length > 0, canRedo: history.future.length > 0, undo, redo }

  // Autosave the working experiment so a reload never loses it.
  useEffect(() => {
    const t = setTimeout(() => saveDraft(experiment), DRAFT_SAVE_MS)
    return () => clearTimeout(t)
  }, [experiment])

  useEffect(() => {
    const onHash = () => {
      setRoute(routeFromHash())
      const fromUrl = experimentFromLocation()
      if (fromUrl) dispatch({ type: 'replace', experiment: fromUrl })
    }
    window.addEventListener('hashchange', onHash)
    return () => window.removeEventListener('hashchange', onHash)
  }, [dispatch])

  const openApp = useCallback((exp?: Experiment) => {
    if (exp) dispatch({ type: 'replace', experiment: exp })
    window.location.hash = '#/app'
    window.scrollTo(0, 0)
    if (!localStorage.getItem(GUIDE_SEEN_KEY)) {
      setGuideOpen(true)
      localStorage.setItem(GUIDE_SEEN_KEY, '1')
    }
  }, [dispatch])

  const goLanding = useCallback(() => {
    setGuideOpen(false)
    window.location.hash = ''
    window.scrollTo(0, 0)
  }, [])

  if (route === 'landing') return <Landing onOpen={openApp} resumeName={hasDraft ? experiment.name : null} />
  return (
    <>
      <Simulator experiment={experiment} dispatch={dispatch} undoState={undoState} onGuide={() => setGuideOpen(true)} onHome={goLanding} />
      <Guide open={guideOpen} onClose={() => setGuideOpen(false)} onLanding={goLanding} />
    </>
  )
}

function Simulator({ experiment, dispatch, undoState, onGuide, onHome }: {
  experiment: Experiment
  dispatch: (a: Action) => void
  undoState: UndoState
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
      const mod = e.metaKey || e.ctrlKey
      if (mod && e.key.toLowerCase() === 'z') {
        e.preventDefault()
        if (e.shiftKey) undoState.redo(); else undoState.undo()
        return
      }
      if (mod && e.key.toLowerCase() === 'y') { e.preventDefault(); undoState.redo(); return }
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
  }, [step, selectedId, setStep, dispatch, onGuide, undoState])

  const clampedStep = Math.min(step, experiment.runtime - 1)
  const invalid = sim.problems.length > 0

  return (
    <div className="app">
      <TopBar
        experiment={experiment} dispatch={dispatch} undoState={undoState}
        status={{ ...sim, elapsedMs: sim.result?.elapsedMs }} onGuide={onGuide} onHome={onHome}
      />
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
          {sim.result && sim.resultExperiment ? (
            <div className={`results-wrap${invalid ? ' stale' : ''}`}>
              <Results
                experiment={sim.resultExperiment}
                result={sim.result}
                step={Math.min(clampedStep, sim.result.steps - 1)}
                setStep={setStep}
                probe={{ x: Math.min(probe.x, sim.result.w), y: Math.min(probe.y, sim.result.h) }}
                setProbe={setProbe}
                selectedObjectId={selectedId}
              />
              {invalid && (
                <div className="stale-overlay" role="status">
                  <div className="stale-card">
                    <h3>Results are from the last valid experiment</h3>
                    <Problems experiment={experiment} problems={sim.problems} dispatch={dispatch} />
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="results-empty">
              {invalid ? (
                <>
                  <h3>Almost there</h3>
                  <Problems experiment={experiment} problems={sim.problems} dispatch={dispatch} />
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

/** Why the experiment can't run, plus one-click fixes where there is an obvious one. */
function Problems({ experiment, problems, dispatch }: { experiment: Experiment; problems: string[]; dispatch: (a: Action) => void }) {
  const outside = outOfBounds(experiment)
  return (
    <>
      <ul className="problem-list">{problems.map((p) => <li key={p}>{p}</li>)}</ul>
      {outside.length > 0 && Number.isInteger(experiment.canvas) && experiment.canvas >= 1 && (
        <button className="btn small" onClick={() => dispatch({ type: 'obj/clamp' })}>
          Move {outside.length === 1 ? `“${outside[0].name}”` : `${outside.length} objects`} inside the {experiment.canvas} × {experiment.canvas} field
        </button>
      )}
    </>
  )
}
