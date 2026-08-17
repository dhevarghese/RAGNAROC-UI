/** A kind of thing that can appear: how salient (bottom-up) and how task-relevant (top-down). */
export interface StimulusType {
  id: string
  name: string
  /** top-down weight, 0..1 (task relevance) */
  td: number
  /** bottom-up weight, 0..1 (physical salience) */
  bu: number
}

/** One appearance of a stimulus type on the canvas. Coordinates are 1-based like the model. */
export interface VisualObject {
  id: string
  name: string
  x: number
  y: number
  /** ms after trial start before it appears */
  latency: number
  /** ms it stays visible */
  duration: number
  /** StimulusType.id */
  stimulus: string
}

export interface Experiment {
  name: string
  /** simulated milliseconds */
  runtime: number
  /** canvas is canvas × canvas cells */
  canvas: number
  /** neighborhood radius for lateral interactions */
  mask: number
  stimulusTypes: StimulusType[]
  objects: VisualObject[]
}

/**
 * Model output. Grids are stored per time step, row-major with y as the row
 * and x as the column (matching the transposed arrays the Cython model returns),
 * i.e. value at (x, y) for step t is `frames[t * w * h + (y - 1) * w + (x - 1)]`.
 */
export interface MapSeries {
  /** Float32 grid values, length steps * w * h */
  data: Float32Array
}

export interface SimulationResult {
  steps: number
  w: number
  h: number
  /** stimulus id → index into per-stimulus maps */
  stimIndex: Record<string, number>
  /** shared across stimuli */
  AM: MapSeries
  IG: MapSeries
  /** per stimulus; EV has one extra "master" entry at the end */
  EV: MapSeries[]
  LV: MapSeries[]
  II: MapSeries[]
  /** simulated EEG (N2pc) per step */
  n2pc: Float64Array
  /** wall-clock ms the run took */
  elapsedMs: number
}
