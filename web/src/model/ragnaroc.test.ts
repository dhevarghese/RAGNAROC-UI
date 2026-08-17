/**
 * Differential test: the TypeScript port must reproduce the compiled Cython
 * reference model. Fixtures come from scripts/export_reference.py.
 *
 * Outputs are stored as float32 (the reference is float64), so comparisons use
 * a tolerance that is orders of magnitude tighter than any porting mistake
 * would produce, but loose enough for float32 rounding of the stored frames.
 */
import { describe, expect, it } from 'vitest'

import reference from './__fixtures__/reference.json'
import { runTrial } from './ragnaroc'
import type { Experiment } from './types'

type MapRef = { stepSums: number[] | number[][]; finalFrame: number[] | number[][] }
type CaseRef = {
  input: {
    canvas: number; mask: number; steps: number
    stim_types: { stimName: string; td: number; bu: number }[]
    vis_objs: { name: string; X: number; Y: number; duration: number; latency: number; stimulus: string }[]
  }
  stimMap: Record<string, number>
  n2pc: number[]
  EV: MapRef; LV: MapRef; II: MapRef; AM: MapRef; IG: MapRef
}

const cases = reference as unknown as Record<string, CaseRef>

function toExperiment(c: CaseRef): Experiment {
  return {
    name: 'ref',
    runtime: c.input.steps,
    canvas: c.input.canvas,
    mask: c.input.mask,
    stimulusTypes: c.input.stim_types.map((s) => ({ id: s.stimName, name: s.stimName, td: s.td, bu: s.bu })),
    objects: c.input.vis_objs.map((o) => ({
      id: o.name, name: o.name, x: o.X, y: o.Y, latency: o.latency, duration: o.duration, stimulus: o.stimulus,
    })),
  }
}

function stepSums(data: Float32Array, steps: number, n: number): number[] {
  const out = new Array<number>(steps)
  for (let t = 0; t < steps; t++) {
    let s = 0
    const base = t * n
    for (let i = 0; i < n; i++) s += data[base + i]
    out[t] = s
  }
  return out
}

/** max |a-b| / max(1, |b|) across two arrays */
function maxRelDiff(a: ArrayLike<number>, b: ArrayLike<number>): number {
  expect(a.length).toBe(b.length)
  let worst = 0
  for (let i = 0; i < a.length; i++) {
    const d = Math.abs(a[i] - b[i]) / Math.max(1, Math.abs(b[i]))
    if (d > worst) worst = d
  }
  return worst
}

// Per-step sums accumulate float32 rounding over the whole grid; the final
// frames and N2pc are compared value-by-value.
const SUM_TOL = 2e-5
const FRAME_TOL = 1e-5
const N2PC_TOL = 1e-6

describe('TypeScript port matches the Cython reference model', () => {
  for (const [name, ref] of Object.entries(cases)) {
    it(name, () => {
      const exp = toExperiment(ref)
      const res = runTrial(exp)
      const n = res.w * res.h
      expect(res.steps).toBe(ref.input.steps)
      expect(res.stimIndex).toEqual(ref.stimMap)

      // N2pc is computed in float64 on both sides: expect near-exact agreement.
      expect(maxRelDiff(res.n2pc, ref.n2pc)).toBeLessThan(N2PC_TOL)

      const shared: Array<['AM' | 'IG', Float32Array]> = [['AM', res.AM.data], ['IG', res.IG.data]]
      for (const [key, data] of shared) {
        const r = ref[key]
        expect(maxRelDiff(stepSums(data, res.steps, n), r.stepSums as number[]), `${key} step sums`).toBeLessThan(SUM_TOL)
        expect(maxRelDiff(data.subarray((res.steps - 1) * n), r.finalFrame as number[]), `${key} final frame`).toBeLessThan(FRAME_TOL)
      }

      const perStim: Array<['EV' | 'LV' | 'II', Float32Array[]]> = [['EV', res.EV.map((m) => m.data)], ['LV', res.LV.map((m) => m.data)], ['II', res.II.map((m) => m.data)]]
      for (const [key, maps] of perStim) {
        const r = ref[key]
        const sums = r.stepSums as number[][]
        const frames = r.finalFrame as number[][]
        expect(maps.length, `${key} map count`).toBe(sums.length)
        maps.forEach((data, s) => {
          expect(maxRelDiff(stepSums(data, res.steps, n), sums[s]), `${key}[${s}] step sums`).toBeLessThan(SUM_TOL)
          expect(maxRelDiff(data.subarray((res.steps - 1) * n), frames[s]), `${key}[${s}] final frame`).toBeLessThan(FRAME_TOL)
        })
      }
    })
  }

  it('reports elapsed time and aborts on request', () => {
    const exp = toExperiment(cases.small10)
    const res = runTrial(exp)
    expect(res.elapsedMs).toBeGreaterThan(0)
    expect(() => runTrial(exp, { onProgress: () => false })).toThrow(/aborted/)
  })
})
