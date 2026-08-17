import { describe, expect, it } from 'vitest'

import { PRESETS } from '../model/presets'
import { runTrial } from '../model/ragnaroc'
import { experimentJson, frameCsv, parseExperimentJson, slug, tracesCsv } from './exportData'

const small = { ...PRESETS.find((p) => p.key === 'lateral')!.experiment, runtime: 120, canvas: 10 }
small.objects = small.objects.map((o) => ({ ...o, x: Math.min(o.x, 10), y: Math.min(o.y, 10) }))

describe('experiment JSON', () => {
  it('round-trips through the wrapper format', () => {
    const exp = parseExperimentJson(experimentJson(small))
    expect(exp).toEqual(small)
  })
  it('accepts a bare experiment object and rejects junk', () => {
    expect(parseExperimentJson(JSON.stringify(small))).toEqual(small)
    expect(parseExperimentJson('{"hello": 1}')).toBeNull()
    expect(parseExperimentJson('not json')).toBeNull()
  })
  it('slugs names for filenames', () => {
    expect(slug('Target + distractor')).toBe('target-distractor')
    expect(slug('   ')).toBe('experiment')
  })
})

describe('CSV', () => {
  const r = runTrial(small)
  it('traces: one row per ms, columns for n2pc, probe maps and pins', () => {
    const csv = tracesCsv(small, r, { x: 7, y: 5 }, [{ x: 3, y: 3 }])
    const lines = csv.trim().split('\n')
    expect(lines).toHaveLength(1 + small.runtime)
    const header = lines[0].split(',')
    // t, n2pc, AM, IG, 3 per stimulus x 2 stimuli, 2 per pin
    expect(header).toHaveLength(1 + 1 + 2 + 3 * 2 + 2)
    expect(header[1]).toBe('n2pc')
    expect(header[2]).toBe('AM@x7y5')
    expect(header.at(-1)).toBe('IG@x3y3')
    // the AM value at t=110 in the CSV equals the frame value
    const t = 110
    const amCol = Number(lines[t + 1].split(',')[2])
    expect(amCol).toBeCloseTo(r.AM.data[t * 100 + (5 - 1) * 10 + (7 - 1)], 5)
  })
  it('frame: h rows of w values with 1-based headers', () => {
    const csv = frameCsv(r.AM.data, r.w, r.h, 110)
    const lines = csv.trim().split('\n')
    expect(lines).toHaveLength(1 + r.h)
    expect(lines[0].split(',')).toHaveLength(1 + r.w)
    expect(lines[1].split(',')[0]).toBe('1')
    expect(Number(lines[5].split(',')[7])).toBeCloseTo(r.AM.data[110 * 100 + 4 * 10 + 6], 5)
  })
})
