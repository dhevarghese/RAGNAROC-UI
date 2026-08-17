import type { Experiment } from './types'

export interface Preset {
  key: string
  title: string
  description: string
  experiment: Experiment
}

const base = { runtime: 600, canvas: 27, mask: 3 }

export const PRESETS: Preset[] = [
  {
    key: 'brisson',
    title: 'Single relevant target',
    description: 'One salient, task-relevant object flashes for 100 ms. Watch attention lock on, then release.',
    experiment: {
      ...base, name: 'Brisson',
      stimulusTypes: [{ id: 'T', name: 'target', td: 0.4, bu: 0.6 }],
      objects: [{ id: 'o1', name: 'T1', x: 7, y: 14, latency: 0, duration: 100, stimulus: 'T' }],
    },
  },
  {
    key: 'single',
    title: 'One lasting object',
    description: 'A modestly salient object stays on for 500 ms. Attention builds slowly, then inhibition catches up.',
    experiment: {
      ...base, name: 'Single',
      stimulusTypes: [{ id: 'T', name: 'target', td: 0.18, bu: 0.15 }],
      objects: [{ id: 'o1', name: 'T1', x: 7, y: 14, latency: 0, duration: 500, stimulus: 'T' }],
    },
  },
  {
    key: 'same',
    title: 'Two in a row, same place',
    description: 'A second object appears where the first just was. Does attention re-engage the same location?',
    experiment: {
      ...base, name: 'Same location',
      stimulusTypes: [
        { id: 'A', name: 'first', td: 0.18, bu: 0.15 },
        { id: 'B', name: 'second', td: 0.18, bu: 0.15 },
      ],
      objects: [
        { id: 'o1', name: 'T1', x: 7, y: 14, latency: 0, duration: 120, stimulus: 'A' },
        { id: 'o2', name: 'T2', x: 7, y: 14, latency: 120, duration: 120, stimulus: 'B' },
      ],
    },
  },
  {
    key: 'diff',
    title: 'Two in a row, different places',
    description: 'Same timing as above, but the second object is on the other side, so attention has to shift.',
    experiment: {
      ...base, name: 'Different locations',
      stimulusTypes: [
        { id: 'A', name: 'first', td: 0.18, bu: 0.15 },
        { id: 'B', name: 'second', td: 0.18, bu: 0.15 },
      ],
      objects: [
        { id: 'o1', name: 'T1', x: 7, y: 14, latency: 0, duration: 120, stimulus: 'A' },
        { id: 'o2', name: 'T2', x: 21, y: 14, latency: 120, duration: 120, stimulus: 'B' },
      ],
    },
  },
  {
    key: 'lateral',
    title: 'Target with a lateral distractor',
    description: 'A relevant target above fixation and a salient-but-irrelevant distractor to the left, shown together. Classic N2pc / PD setup.',
    experiment: {
      ...base, name: 'Target + distractor',
      stimulusTypes: [
        { id: 'T', name: 'target', td: 0.4, bu: 0.15 },
        { id: 'D', name: 'distractor', td: 0.18, bu: 0.17 },
      ],
      objects: [
        { id: 'o1', name: 'T', x: 14, y: 7, latency: 0, duration: 500, stimulus: 'T' },
        { id: 'o2', name: 'D', x: 7, y: 14, latency: 0, duration: 500, stimulus: 'D' },
      ],
    },
  },
  {
    key: 'eimer',
    title: 'Two rapid targets',
    description: 'Two brief, highly salient targets 10 ms apart at different locations (Eimer & Grubert). Can attention split?',
    experiment: {
      ...base, name: 'Eimer & Grubert',
      stimulusTypes: [
        { id: 'A', name: 'target 1', td: 0.7, bu: 0.6 },
        { id: 'B', name: 'target 2', td: 0.7, bu: 0.6 },
      ],
      objects: [
        { id: 'o1', name: 'T1', x: 10, y: 10, latency: 0, duration: 40, stimulus: 'A' },
        { id: 'o2', name: 'T2', x: 10, y: 18, latency: 10, duration: 40, stimulus: 'B' },
      ],
    },
  },
]

export const DEFAULT_PRESET = PRESETS[4] // target + distractor: the richest first impression
