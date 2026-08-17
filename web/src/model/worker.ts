/// <reference lib="webworker" />
/**
 * Web Worker that runs the model off the main thread.
 * Protocol: main → { type: 'run', id, experiment } ; worker → progress / result / error.
 * A newer 'run' supersedes an in-flight one (the old run is aborted at its next progress tick).
 */
import { AbortError, runTrial } from './ragnaroc'
import type { Experiment, SimulationResult } from './types'

export type WorkerRequest = { type: 'run'; id: number; experiment: Experiment }
export type WorkerResponse =
  | { type: 'progress'; id: number; fraction: number }
  | { type: 'result'; id: number; result: SimulationResult }
  | { type: 'error'; id: number; message: string }

let latestId = 0

self.onmessage = (ev: MessageEvent<WorkerRequest>) => {
  const msg = ev.data
  if (msg.type !== 'run') return
  latestId = msg.id
  const id = msg.id
  // Yield once so a burst of requests collapses to the newest before heavy work starts.
  setTimeout(() => {
    if (id !== latestId) return
    try {
      const result = runTrial(msg.experiment, {
        onProgress: (fraction) => {
          if (id !== latestId) return false
          post({ type: 'progress', id, fraction })
          return true
        },
      })
      const transfer = [
        result.AM.data.buffer, result.IG.data.buffer, result.n2pc.buffer,
        ...result.EV.map((m) => m.data.buffer),
        ...result.LV.map((m) => m.data.buffer),
        ...result.II.map((m) => m.data.buffer),
      ] as ArrayBuffer[]
      ;(self as unknown as Worker).postMessage({ type: 'result', id, result } satisfies WorkerResponse, transfer)
    } catch (err) {
      if (err instanceof AbortError) return
      post({ type: 'error', id, message: err instanceof Error ? err.message : String(err) })
    }
  }, 0)
}

function post(msg: WorkerResponse) {
  ;(self as unknown as Worker).postMessage(msg)
}
