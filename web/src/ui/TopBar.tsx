import { useEffect, useRef, useState } from 'react'

import { PRESETS } from '../model/presets'
import type { Experiment } from '../model/types'
import { loadLibrary, removeFromLibrary, saveToLibrary, shareUrl, type Action, type SavedExperiment } from '../state/experiment'

interface Props {
  experiment: Experiment
  dispatch: (a: Action) => void
  status: { running: boolean; progress: number | null; problems: string[]; error: string | null; elapsedMs?: number }
  onGuide: () => void
  onHome: () => void
}

export function TopBar({ experiment, dispatch, status, onGuide, onHome }: Props) {
  const [menu, setMenu] = useState<null | 'presets' | 'library'>(null)
  const [library, setLibrary] = useState<SavedExperiment[]>([])
  const [toast, setToast] = useState<string | null>(null)
  const wrapRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!menu) return
    const onDoc = (e: MouseEvent) => {
      if (!wrapRef.current?.contains(e.target as Node)) setMenu(null)
    }
    document.addEventListener('mousedown', onDoc)
    return () => document.removeEventListener('mousedown', onDoc)
  }, [menu])

  useEffect(() => {
    if (!toast) return
    const t = setTimeout(() => setToast(null), 2200)
    return () => clearTimeout(t)
  }, [toast])

  const openLibrary = () => {
    setLibrary(loadLibrary())
    setMenu(menu === 'library' ? null : 'library')
  }

  const share = async () => {
    const url = shareUrl(experiment)
    history.replaceState(null, '', url)
    try {
      await navigator.clipboard.writeText(url)
      setToast('Link copied — it contains the whole experiment.')
    } catch {
      setToast('Link is in the address bar.')
    }
  }

  const save = () => {
    saveToLibrary(experiment)
    setToast(`Saved “${experiment.name}” in this browser.`)
  }

  return (
    <header className="topbar" ref={wrapRef}>
      <a className="brand" href="#" onClick={(e) => { e.preventDefault(); onHome() }} title="About / introduction">
        <img src="./logo.png" alt="" />
        <span>Ragnaroc</span>
      </a>

      <input
        className="exp-name"
        value={experiment.name}
        onChange={(e) => dispatch({ type: 'set', patch: { name: e.target.value } })}
        aria-label="experiment name"
        spellCheck={false}
      />

      <div className="status" aria-live="polite">
        {status.problems.length > 0 ? (
          <span className="status-pill warn" title={status.problems.join('\n')}>⚠ {status.problems[0]}</span>
        ) : status.error ? (
          <span className="status-pill error">✕ {status.error}</span>
        ) : status.running ? (
          <span className="status-pill running">
            <span className="spinner" /> simulating {status.progress != null ? `${Math.round(status.progress * 100)}%` : ''}
          </span>
        ) : (
          <span className="status-pill ok">● live</span>
        )}
      </div>

      <nav className="actions">
        <div className="menu-wrap">
          <button className={`btn${menu === 'presets' ? ' active' : ''}`} onClick={() => setMenu(menu === 'presets' ? null : 'presets')}>Presets ▾</button>
          {menu === 'presets' && (
            <ul className="menu">
              {PRESETS.map((p) => (
                <li key={p.key}>
                  <button onClick={() => { dispatch({ type: 'replace', experiment: p.experiment }); setMenu(null) }}>
                    <b>{p.title}</b>
                    <span>{p.description}</span>
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
        <div className="menu-wrap">
          <button className={`btn${menu === 'library' ? ' active' : ''}`} onClick={openLibrary}>Saved ▾</button>
          {menu === 'library' && (
            <ul className="menu">
              {library.length === 0 && <li className="menu-empty muted">Nothing saved yet in this browser.</li>}
              {library.map((s) => (
                <li key={s.experiment.name} className="menu-row">
                  <button onClick={() => { dispatch({ type: 'replace', experiment: s.experiment }); setMenu(null) }}>
                    <b>{s.experiment.name}</b>
                    <span>{new Date(s.savedAt).toLocaleString()} · {s.experiment.objects.length} objects</span>
                  </button>
                  <button className="icon-btn" title="delete" onClick={() => setLibrary(removeFromLibrary(s.experiment.name))}>×</button>
                </li>
              ))}
            </ul>
          )}
        </div>
        <button className="btn" onClick={save}>Save</button>
        <button className="btn primary" onClick={share}>Share link</button>
        <button className="btn guide-btn" onClick={onGuide} title="Quick guide (?)">?</button>
      </nav>
      {toast && <div className="toast">{toast}</div>}
    </header>
  )
}
