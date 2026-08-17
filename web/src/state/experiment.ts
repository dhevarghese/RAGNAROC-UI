/**
 * Experiment state: reducer, URL (de)serialisation for shareable links, and
 * localStorage persistence. Everything the old app kept in DynamoDB lives here.
 */
import { DEFAULT_PRESET } from '../model/presets'
import type { Experiment, StimulusType, VisualObject } from '../model/types'

export type Action =
  | { type: 'replace'; experiment: Experiment }
  | { type: 'set'; patch: Partial<Pick<Experiment, 'name' | 'runtime' | 'canvas' | 'mask'>> }
  | { type: 'stim/add'; stim?: Partial<StimulusType> }
  | { type: 'stim/update'; id: string; patch: Partial<StimulusType> }
  /** Objects of that type are reassigned to `reassignTo`, or removed if it is absent. */
  | { type: 'stim/remove'; id: string; reassignTo?: string }
  | { type: 'obj/add'; obj: Partial<VisualObject> & Pick<VisualObject, 'x' | 'y'> }
  | { type: 'obj/update'; id: string; patch: Partial<VisualObject> }
  | { type: 'obj/remove'; id: string }
  /** Move an object by whole cells, clamped to the canvas. */
  | { type: 'obj/nudge'; id: string; dx: number; dy: number }
  /** Pull every object back inside the current canvas. */
  | { type: 'obj/clamp' }

let counter = 0
export const uid = (prefix: string) => `${prefix}${Date.now().toString(36)}${(counter++).toString(36)}`

const PALETTE = ['#f5b53f', '#5ec4ff', '#ff6b8b', '#7ee787', '#c792ea', '#ffa657']
export function stimColor(index: number) {
  return PALETTE[index % PALETTE.length]
}

export function reducer(state: Experiment, action: Action): Experiment {
  switch (action.type) {
    case 'replace':
      return structuredClone(action.experiment)
    case 'set':
      return { ...state, ...action.patch }
    case 'stim/add': {
      const n = state.stimulusTypes.length + 1
      const stim: StimulusType = {
        id: uid('s'), name: `stimulus ${n}`, td: 0.3, bu: 0.3, ...action.stim,
      }
      return { ...state, stimulusTypes: [...state.stimulusTypes, stim] }
    }
    case 'stim/update':
      return {
        ...state,
        stimulusTypes: state.stimulusTypes.map((s) => (s.id === action.id ? { ...s, ...action.patch } : s)),
      }
    case 'stim/remove': {
      const remaining = state.stimulusTypes.filter((s) => s.id !== action.id)
      const target = remaining.some((s) => s.id === action.reassignTo) ? action.reassignTo : undefined
      return {
        ...state,
        stimulusTypes: remaining,
        objects: target
          ? state.objects.map((o) => (o.stimulus === action.id ? { ...o, stimulus: target } : o))
          : state.objects.filter((o) => o.stimulus !== action.id),
      }
    }
    case 'obj/add': {
      const n = state.objects.length + 1
      const obj: VisualObject = {
        id: uid('o'), name: `obj ${n}`, latency: 0, duration: 100,
        stimulus: state.stimulusTypes[0]?.id ?? '', ...action.obj,
      }
      return { ...state, objects: [...state.objects, obj] }
    }
    case 'obj/update':
      return { ...state, objects: state.objects.map((o) => (o.id === action.id ? { ...o, ...action.patch } : o)) }
    case 'obj/remove':
      return { ...state, objects: state.objects.filter((o) => o.id !== action.id) }
    case 'obj/nudge': {
      const c = state.canvas
      const clamp = (v: number) => Math.min(c, Math.max(1, v))
      return { ...state, objects: state.objects.map((o) => (o.id === action.id ? { ...o, x: clamp(o.x + action.dx), y: clamp(o.y + action.dy) } : o)) }
    }
    case 'obj/clamp': {
      const c = state.canvas
      if (!outOfBounds(state).length) return state
      return {
        ...state,
        objects: state.objects.map((o) => ({ ...o, x: Math.min(Math.max(1, o.x), c), y: Math.min(Math.max(1, o.y), c) })),
      }
    }
  }
}

/** Objects that lie outside the current canvas (e.g. after it was shrunk). */
export function outOfBounds(exp: Experiment): VisualObject[] {
  return exp.objects.filter((o) => o.x < 1 || o.y < 1 || o.x > exp.canvas || o.y > exp.canvas)
}

// ---- undo / redo -----------------------------------------------------------

export interface History {
  past: Experiment[]
  present: Experiment
  future: Experiment[]
  /** identity of the last edit, so a run of the same edit (dragging, typing) collapses into one undo step */
  lastKey: string | null
  lastAt: number
}

export type HistoryAction = Action | { type: 'undo' } | { type: 'redo' }

const MAX_HISTORY = 100
const COALESCE_MS = 1000

/** Two edits coalesce when they change the same field of the same thing in quick succession. */
function editKey(a: Action): string | null {
  switch (a.type) {
    case 'set': return `set:${Object.keys(a.patch).sort().join(',')}`
    case 'stim/update': return `stim:${a.id}:${Object.keys(a.patch).sort().join(',')}`
    case 'obj/update': return `obj:${a.id}:${Object.keys(a.patch).sort().join(',')}`
    case 'obj/nudge': return `nudge:${a.id}`
    default: return null
  }
}

export function initialHistory(present: Experiment): History {
  return { past: [], present, future: [], lastKey: null, lastAt: 0 }
}

/** `now` is passed in (not read inside) to keep the reducer pure. */
export function historyReducer(h: History, action: HistoryAction & { now?: number }): History {
  if (action.type === 'undo') {
    if (!h.past.length) return h
    return { past: h.past.slice(0, -1), present: h.past[h.past.length - 1], future: [h.present, ...h.future], lastKey: null, lastAt: 0 }
  }
  if (action.type === 'redo') {
    if (!h.future.length) return h
    return { past: [...h.past, h.present], present: h.future[0], future: h.future.slice(1), lastKey: null, lastAt: 0 }
  }
  const next = reducer(h.present, action)
  if (next === h.present) return h
  const key = editKey(action)
  const now = action.now ?? 0
  const coalesce = key !== null && key === h.lastKey && now - h.lastAt < COALESCE_MS
  const past = coalesce ? h.past : [...h.past, h.present].slice(-MAX_HISTORY)
  return { past, present: next, future: [], lastKey: key, lastAt: now }
}

// ---- draft autosave --------------------------------------------------------

const DRAFT_KEY = 'ragnaroc.draft.v1'

export function loadDraft(): Experiment | null {
  try {
    const raw = localStorage.getItem(DRAFT_KEY)
    if (!raw) return null
    const exp = JSON.parse(raw) as Experiment
    return Array.isArray(exp.stimulusTypes) && Array.isArray(exp.objects) ? exp : null
  } catch {
    return null
  }
}

export function saveDraft(exp: Experiment) {
  try {
    localStorage.setItem(DRAFT_KEY, JSON.stringify(exp))
  } catch {
    /* quota or private mode: the draft is a convenience, not a requirement */
  }
}

// ---- URL sharing -----------------------------------------------------------
// The whole experiment fits comfortably in a hash fragment as compact JSON.

type Compact = [
  name: string, runtime: number, canvas: number, mask: number,
  stims: [id: string, name: string, td: number, bu: number][],
  objs: [id: string, name: string, x: number, y: number, latency: number, duration: number, stimulus: string][],
]

export function encodeExperiment(exp: Experiment): string {
  const c: Compact = [
    exp.name, exp.runtime, exp.canvas, exp.mask,
    exp.stimulusTypes.map((s) => [s.id, s.name, s.td, s.bu]),
    exp.objects.map((o) => [o.id, o.name, o.x, o.y, o.latency, o.duration, o.stimulus]),
  ]
  return base64url(JSON.stringify(c))
}

export function decodeExperiment(hash: string): Experiment | null {
  try {
    const c = JSON.parse(fromBase64url(hash)) as Compact
    if (!Array.isArray(c) || c.length !== 6) return null
    return {
      name: String(c[0]), runtime: Number(c[1]), canvas: Number(c[2]), mask: Number(c[3]),
      stimulusTypes: c[4].map(([id, name, td, bu]) => ({ id, name, td: Number(td), bu: Number(bu) })),
      objects: c[5].map(([id, name, x, y, latency, duration, stimulus]) => ({
        id, name, x: Number(x), y: Number(y), latency: Number(latency), duration: Number(duration), stimulus,
      })),
    }
  } catch {
    return null
  }
}

function base64url(s: string) {
  const bytes = new TextEncoder().encode(s)
  let bin = ''
  bytes.forEach((b) => (bin += String.fromCharCode(b)))
  return btoa(bin).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '')
}

function fromBase64url(s: string) {
  const b64 = s.replace(/-/g, '+').replace(/_/g, '/')
  const bin = atob(b64 + '='.repeat((4 - (b64.length % 4)) % 4))
  const bytes = Uint8Array.from(bin, (ch) => ch.charCodeAt(0))
  return new TextDecoder().decode(bytes)
}

export function experimentFromLocation(): Experiment | null {
  const h = window.location.hash
  if (!h.startsWith('#e=')) return null
  return decodeExperiment(h.slice(3))
}

export function shareUrl(exp: Experiment): string {
  const u = new URL(window.location.href)
  u.hash = 'e=' + encodeExperiment(exp)
  return u.toString()
}

// ---- local library ---------------------------------------------------------

const LS_KEY = 'ragnaroc.experiments.v1'
export interface SavedExperiment { savedAt: string; experiment: Experiment }

export function loadLibrary(): SavedExperiment[] {
  try {
    const raw = localStorage.getItem(LS_KEY)
    return raw ? (JSON.parse(raw) as SavedExperiment[]) : []
  } catch {
    return []
  }
}

export function saveToLibrary(exp: Experiment): SavedExperiment[] {
  const lib = loadLibrary().filter((s) => s.experiment.name !== exp.name)
  lib.unshift({ savedAt: new Date().toISOString(), experiment: structuredClone(exp) })
  localStorage.setItem(LS_KEY, JSON.stringify(lib.slice(0, 50)))
  return lib
}

export function removeFromLibrary(name: string): SavedExperiment[] {
  const lib = loadLibrary().filter((s) => s.experiment.name !== name)
  localStorage.setItem(LS_KEY, JSON.stringify(lib))
  return lib
}

/** A shared link wins, then whatever was being edited last time, then the default preset. */
export function initialExperiment(): Experiment {
  return experimentFromLocation() ?? loadDraft() ?? structuredClone(DEFAULT_PRESET.experiment)
}
