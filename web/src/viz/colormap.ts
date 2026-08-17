/**
 * Colour mapping for activation values. The model's activations live in
 * [EI, EE] = [-10, 30]; the attention map (AM) starts at its resting 5.
 * We use a perceptually ordered "inferno-like" ramp built from a few stops so
 * that no colour library is needed and hot spots read as hot spots.
 */

export const ACT_MIN = -10
export const ACT_MAX = 30

// stops: [t, r, g, b] sampled from inferno
const STOPS: [number, number, number, number][] = [
  [0.0, 0, 0, 4],
  [0.13, 27, 12, 65],
  [0.25, 74, 12, 107],
  [0.38, 120, 28, 109],
  [0.5, 165, 44, 96],
  [0.63, 207, 68, 70],
  [0.75, 237, 105, 37],
  [0.88, 251, 155, 6],
  [1.0, 252, 255, 164],
]

const LUT_SIZE = 256
const LUT = new Uint8ClampedArray(LUT_SIZE * 3)
for (let i = 0; i < LUT_SIZE; i++) {
  const t = i / (LUT_SIZE - 1)
  let k = 0
  while (k < STOPS.length - 2 && t > STOPS[k + 1][0]) k++
  const [t0, r0, g0, b0] = STOPS[k]
  const [t1, r1, g1, b1] = STOPS[k + 1]
  const u = (t - t0) / (t1 - t0)
  LUT[i * 3] = r0 + (r1 - r0) * u
  LUT[i * 3 + 1] = g0 + (g1 - g0) * u
  LUT[i * 3 + 2] = b0 + (b1 - b0) * u
}

/** Map an activation value to a LUT index in [0, 255]. */
export function lutIndex(v: number, min = ACT_MIN, max = ACT_MAX): number {
  let t = (v - min) / (max - min)
  if (t < 0) t = 0
  else if (t > 1) t = 1
  return (t * (LUT_SIZE - 1)) | 0
}

export function rgbAt(v: number, min = ACT_MIN, max = ACT_MAX): [number, number, number] {
  const i = lutIndex(v, min, max) * 3
  return [LUT[i], LUT[i + 1], LUT[i + 2]]
}

export function cssAt(v: number, min = ACT_MIN, max = ACT_MAX): string {
  const [r, g, b] = rgbAt(v, min, max)
  return `rgb(${r},${g},${b})`
}

/** CSS gradient string for a legend bar. */
export function legendGradient(): string {
  return `linear-gradient(to right, ${STOPS.map(([t, r, g, b]) => `rgb(${r},${g},${b}) ${(t * 100).toFixed(0)}%`).join(', ')})`
}

/**
 * Paint one frame of a map into an ImageData buffer (w×h pixels, one per cell).
 * `frame` is row-major [y][x] as produced by the model.
 */
export function paintFrame(img: ImageData, frame: Float32Array, offset: number, n: number, min = ACT_MIN, max = ACT_MAX) {
  const px = img.data
  for (let i = 0; i < n; i++) {
    const li = lutIndex(frame[offset + i], min, max) * 3
    const o = i * 4
    px[o] = LUT[li]
    px[o + 1] = LUT[li + 1]
    px[o + 2] = LUT[li + 2]
    px[o + 3] = 255
  }
}
