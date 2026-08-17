/**
 * Runs the model in a Web Worker whenever the experiment changes (debounced),
 * exposing the latest result plus progress. Stale results are discarded.
 */
import { useEffect, useMemo, useRef, useState } from 'react'

import { validate } from '../model/ragnaroc'
import type { Experiment, SimulationResult } from '../model/types'
import type { WorkerRequest, WorkerResponse } from '../model/worker'

export interface SimulationState {
  result: SimulationResult | null
  /** 0..1 while running, null when idle */
  progress: number | null
  running: boolean
  problems: string[]
  error: string | null
}

const DEBOUNCE_MS = 120

export function useSimulation(experiment: Experiment): SimulationState {
  const [result, setResult] = useState<SimulationResult | null>(null)
  const [progress, setProgress] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const workerRef = useRef<Worker | null>(null)
  const idRef = useRef(0)

  const problems = useMemo(() => validate(experiment), [experiment])

  useEffect(() => {
    const worker = new Worker(new URL('../model/worker.ts', import.meta.url), { type: 'module' })
    workerRef.current = worker
    worker.onmessage = (ev: MessageEvent<WorkerResponse>) => {
      const msg = ev.data
      if (msg.id !== idRef.current) return
      if (msg.type === 'progress') setProgress(msg.fraction)
      else if (msg.type === 'result') {
        setResult(msg.result)
        setProgress(null)
        setError(null)
      } else if (msg.type === 'error') {
        setError(msg.message)
        setProgress(null)
      }
    }
    return () => {
      worker.terminate()
      workerRef.current = null
    }
  }, [])

  useEffect(() => {
    if (problems.length > 0) {
      setProgress(null)
      return
    }
    const id = ++idRef.current
    const t = setTimeout(() => {
      setProgress(0)
      const req: WorkerRequest = { type: 'run', id, experiment }
      workerRef.current?.postMessage(req)
    }, DEBOUNCE_MS)
    return () => clearTimeout(t)
  }, [experiment, problems])

  return { result, progress, running: progress !== null, problems, error }
}
