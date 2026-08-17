import { describe, expect, it } from 'vitest'

import { PRESETS } from '../model/presets'
import { historyReducer, initialHistory, outOfBounds, reducer } from './experiment'

const lateral = PRESETS.find((p) => p.key === 'lateral')!.experiment

describe('stim/remove', () => {
  it('reassigns objects when a target is given', () => {
    const next = reducer(lateral, { type: 'stim/remove', id: 'D', reassignTo: 'T' })
    expect(next.stimulusTypes.map((s) => s.id)).toEqual(['T'])
    expect(next.objects).toHaveLength(2)
    expect(next.objects.every((o) => o.stimulus === 'T')).toBe(true)
  })
  it('removes the objects otherwise', () => {
    const next = reducer(lateral, { type: 'stim/remove', id: 'D' })
    expect(next.objects.map((o) => o.stimulus)).toEqual(['T'])
  })
  it('ignores a reassign target that does not exist', () => {
    const next = reducer(lateral, { type: 'stim/remove', id: 'D', reassignTo: 'nope' })
    expect(next.objects).toHaveLength(1)
  })
})

describe('obj/nudge', () => {
  it('moves by whole cells and clamps to the canvas', () => {
    let e = reducer(lateral, { type: 'obj/nudge', id: 'o1', dx: 1, dy: 5 })
    expect(e.objects[0]).toMatchObject({ x: 15, y: 12 })
    e = reducer(e, { type: 'obj/nudge', id: 'o1', dx: 100, dy: -100 })
    expect(e.objects[0]).toMatchObject({ x: 27, y: 1 })
  })
})

describe('obj/clamp', () => {
  it('pulls objects back inside a shrunken canvas', () => {
    const shrunk = reducer(lateral, { type: 'set', patch: { canvas: 10 } })
    expect(outOfBounds(shrunk).map((o) => o.id)).toEqual(['o1', 'o2']) // T at (14, 7) and D at (7, 14)
    const clamped = reducer(shrunk, { type: 'obj/clamp' })
    expect(outOfBounds(clamped)).toHaveLength(0)
    expect(clamped.objects[0]).toMatchObject({ x: 10, y: 7 })
    expect(clamped.objects[1]).toMatchObject({ x: 7, y: 10 })
  })
  it('is a no-op when nothing is outside', () => {
    expect(reducer(lateral, { type: 'obj/clamp' })).toBe(lateral)
  })
})

describe('history', () => {
  it('undoes and redoes', () => {
    let h = initialHistory(lateral)
    h = historyReducer(h, { type: 'set', patch: { runtime: 300 }, now: 0 })
    h = historyReducer(h, { type: 'obj/remove', id: 'o2', now: 2000 })
    expect(h.past).toHaveLength(2)
    h = historyReducer(h, { type: 'undo' })
    expect(h.present.objects).toHaveLength(2)
    expect(h.present.runtime).toBe(300)
    h = historyReducer(h, { type: 'undo' })
    expect(h.present).toBe(lateral)
    h = historyReducer(h, { type: 'undo' }) // nothing left: unchanged
    expect(h.present).toBe(lateral)
    h = historyReducer(h, { type: 'redo' })
    expect(h.present.runtime).toBe(300)
    // a new edit clears the redo stack
    h = historyReducer(h, { type: 'set', patch: { mask: 2 }, now: 5000 })
    expect(h.future).toHaveLength(0)
  })
  it('coalesces a quick run of edits to the same field into one step', () => {
    let h = initialHistory(lateral)
    for (let i = 0; i < 5; i++) h = historyReducer(h, { type: 'stim/update', id: 'T', patch: { td: 0.1 * i }, now: i * 100 })
    expect(h.past).toHaveLength(1)
    // a different field starts a new step
    h = historyReducer(h, { type: 'stim/update', id: 'T', patch: { bu: 0.9 }, now: 600 })
    expect(h.past).toHaveLength(2)
    // same field again but after a pause also starts a new step
    h = historyReducer(h, { type: 'stim/update', id: 'T', patch: { bu: 0.8 }, now: 5000 })
    expect(h.past).toHaveLength(3)
    h = historyReducer(h, { type: 'undo' })
    expect(h.present.stimulusTypes[0].bu).toBe(0.9)
  })
  it('does not record no-op actions', () => {
    const h = initialHistory(lateral)
    expect(historyReducer(h, { type: 'obj/clamp', now: 0 })).toBe(h)
  })
})
