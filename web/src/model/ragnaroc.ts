/**
 * RAGNAROC model — TypeScript port of cython/ragnaroc.pyx (Wyble et al.).
 *
 * This is a line-for-line port of the reference model. It is verified against
 * outputs of the compiled Cython extension by ragnaroc.test.ts, so please keep
 * the arithmetic order identical when editing.
 *
 * Numerical-fidelity notes:
 *  - The Cython source declares most constants as `cdef float` (single
 *    precision). Those are reproduced with Math.fround so the promoted double
 *    values match bit for bit. Constants that were plain Python literals
 *    (e.g. the 0.07 passed to Attnfunction) stay double.
 *  - Internally grids are indexed [x][y] like the Cython arrays; the returned
 *    frames are transposed to row-major [y][x] like the reference output.
 */

import type { Experiment, MapSeries, SimulationResult } from './types'

const f = Math.fround

// ---- model constants (see ragnaroc.pyx) -------------------------------------
const dt_vm = f(0.015)
const dt_vm_IG = f(0.04)
const dt_vm_II = f(0.0025)
const EE_EEG = f(65)
const EE = f(30)
const EL = f(0)
const EI = f(-10)
const individuation = f(0.2)
const AMexcitebias = f(0.2)
const EVsalInput = f(1)
const LAI = f(0.45)
const ThreshLV_II = f(0)
const Thresh = f(14)
const ThreshIG = f(8)
const attentionweight = f(2)
const EVthresh = f(7)
const LVthresh = f(5)
const AM_highthresh = f(8)
const AMtoIG_inhib = f(0.25)
const AMtoIG_excite = f(0.4)
const LVtoII = f(0.02)
const ILVoLV = f(6.5)
const MaxLVtoIG = f(0.35)
const MaxAMtoIG = f(0.35)

/** t1onset in the reference is `100-1`; visual object onsets are offset by it. */
const T1_ONSET = 99

export interface RunOptions {
  /** called every few steps with progress in [0, 1]; return false to abort */
  onProgress?: (fraction: number) => boolean | void
}

/**
 * Run the model. Throws if the experiment is not runnable (see validate()).
 */
export function runTrial(exp: Experiment, opts: RunOptions = {}): SimulationResult {
  const t0 = performance.now()
  const xDim = exp.canvas
  const yDim = exp.canvas
  const NNMask = exp.mask
  const steps = exp.runtime
  const N = xDim * yDim
  const ix = (x: number, y: number) => x * yDim + y // 0-based internal [x][y]

  // ---- sombrero / receptive field kernels ---------------------------------
  // xx = arange(-xDim, xDim+1); grids are (2*yDim+1) x (2*xDim+1); the app only
  // ever uses square canvases, and both kernels are radially symmetric anyway.
  const KW = 2 * xDim + 1
  const KH = 2 * yDim + 1
  const sombrero = new Float64Array(KW * KH)
  const gausRF0 = new Float64Array(KW * KH)
  let gausMax = -Infinity
  for (let r = 0; r < KH; r++) {
    const yg = -yDim + r
    for (let c = 0; c < KW; c++) {
      const xg = -xDim + c
      const t = xg * xg + yg * yg
      // Attnfunction(xgrid, ygrid, .07, individuation): .07 is a Python double literal
      const z1 = -Math.exp(-0.5 * t * 0.07)
      const z2 = 2 * Math.exp(-0.5 * t * individuation)
      sombrero[r * KW + c] = z1 + z2
      // RFfunction(xgrid, ygrid, RFsize=1)
      const g = Math.exp(-0.5 * t * 1)
      gausRF0[r * KW + c] = g
      if (g > gausMax) gausMax = g
    }
  }
  const gausRF = new Float64Array(KW * KH)
  for (let i = 0; i < gausRF.length; i++) gausRF[i] = gausRF0[i] / gausMax
  // Reference indexes kernels as [xdiff-1, ydiff-1] on a meshgrid whose first
  // axis is y. Because the app uses square canvases and both kernels are
  // symmetric under x<->y this is equivalent; the loops below keep that
  // convention: kernel[(xdiff-1)*KW + (ydiff-1)].

  // ---- stimulus types & objects ------------------------------------------
  const S = exp.stimulusTypes.length
  const stimIndex: Record<string, number> = {}
  const bu = new Float64Array(S)
  const td = new Float64Array(S)
  exp.stimulusTypes.forEach((st, i) => {
    stimIndex[st.id] = i
    bu[i] = st.bu
    td[i] = st.td
  })
  const O = exp.objects.length
  const ox = new Int32Array(O)
  const oy = new Int32Array(O)
  const oStype = new Int32Array(O)
  const onset = new Float64Array(O)
  const period = new Float64Array(O)
  exp.objects.forEach((o, i) => {
    ox[i] = o.x
    oy[i] = o.y
    oStype[i] = stimIndex[o.stimulus]
    onset[i] = o.latency + T1_ONSET
    period[i] = o.latency + o.duration + T1_ONSET
  })

  // ---- state: previous-step activations (double) and outputs (float32) ----
  // EV has S+1 maps (last = master). Recurrence reads only the previous step,
  // so keep prev/cur double grids and stream float32 copies into the outputs.
  const mk = () => new Float64Array(N)
  const EVprev = Array.from({ length: S + 1 }, mk)
  const EVcur = Array.from({ length: S + 1 }, mk)
  const LVprev = Array.from({ length: S }, mk)
  const LVcur = Array.from({ length: S }, mk)
  const IIprev = Array.from({ length: S }, mk)
  const IIcur = Array.from({ length: S }, mk)
  const AMprev = mk().fill(5) // AM = zeros + 5
  const AMcur = mk()
  const IGprev = mk()
  const IGcur = mk()

  const out = {
    EV: Array.from({ length: S + 1 }, () => new Float32Array(steps * N)),
    LV: Array.from({ length: S }, () => new Float32Array(steps * N)),
    II: Array.from({ length: S }, () => new Float32Array(steps * N)),
    AM: new Float32Array(steps * N),
    IG: new Float32Array(steps * N),
  }
  const n2pc = new Float64Array(steps)

  // currents
  const EV_ex = Array.from({ length: S + 1 }, mk)
  const EV_in = Array.from({ length: S + 1 }, mk)
  const LV_ex = Array.from({ length: S }, mk)
  const LV_in = Array.from({ length: S }, mk)
  const II_ex = Array.from({ length: S }, mk)
  const AM_ex = mk()
  const AM_in = mk()
  const AM_eeg = mk()
  const IG_exLV = mk()
  const IG_exAM = mk()
  const IG_in = mk()
  const IGex = mk()

  const halfX = Math.ceil(xDim / 2)

  for (let step = 0; step < steps; step++) {
    // reset currents
    for (let s = 0; s < S; s++) {
      EV_ex[s].fill(0); LV_ex[s].fill(0); II_ex[s].fill(0)
      EV_in[s].fill(0); LV_in[s].fill(0)
    }
    EV_ex[S].fill(0); EV_in[S].fill(0)
    AM_ex.fill(AMexcitebias)
    IG_exLV.fill(0); IG_exAM.fill(0)
    AM_in.fill(0); IG_in.fill(0)

    // On step 0 the reference reads "prev = 0", i.e. the initial state (zeros,
    // AM = 5). Our prev buffers hold exactly that before the first step.

    // stimulus input
    for (let o = 0; o < O; o++) {
      const p = ix(ox[o] - 1, oy[o] - 1)
      if (step >= onset[o] && step < period[o]) EV_ex[oStype[o]][p] = EVsalInput
      EV_ex[S][p] = EVsalInput
    }

    // feed-forward sweep over every neuron
    for (let xi = 1; xi <= xDim; xi++) {
      for (let yi = 1; yi <= yDim; yi++) {
        const p = ix(xi - 1, yi - 1)
        for (let s = 0; s < S; s++) {
          const lv = LVprev[s][p]
          if (lv > LVthresh) II_ex[s][p] += (lv - LVthresh) * LVtoII
          const ii = IIprev[s][p]
          if (ii > ThreshLV_II) LV_in[s][p] += (ii - ThreshLV_II) * ILVoLV
        }
        const amp = AMprev[p]
        if (amp > Thresh + AM_highthresh) IG_in[p] = (amp - Thresh + AM_highthresh) * AMtoIG_inhib

        const xmin = Math.max(xi - NNMask, 1)
        const xmax = Math.min(xi + NNMask, xDim)
        const ymin = Math.max(yi - NNMask, 1)
        const ymax = Math.min(yi + NNMask, yDim)

        // kernel row for this neuron: kernelAt(k, xdiff, ydiff) = k[(xdiff-1)*KW + (ydiff-1)]
        // with xdiff = x2 - xi + xDim + 1  →  row base = (x2 - xi + xDim) * KW, col = y2 - yi + yDim
        for (let x2 = xmin; x2 <= xmax; x2++) {
          const qRow = (x2 - 1) * yDim
          const kRow = (x2 - xi + xDim) * KW - yi + yDim
          for (let y2 = ymin; y2 <= ymax; y2++) {
            const q = qRow + y2 - 1
            const RF_local = gausRF[kRow + y2]

            let attention = 1
            const amq = AMprev[q]
            if (amq > Thresh) attention = Math.max(1, Math.log(amq - Thresh + 1) * attentionweight)

            for (let s = 0; s < S; s++) {
              const ev = EVprev[s][q]
              if (ev > EVthresh) LV_ex[s][p] += (ev - EVthresh) * bu[s] * attention * RF_local
              const lv = LVprev[s][q]
              if (lv > LVthresh) {
                const drive = (lv - LVthresh) * td[s] * RF_local
                AM_ex[p] += drive
                IG_exLV[p] += drive
              }
            }
          }
        }

        AM_in[p] += Math.max(0, (IGprev[p] - ThreshIG) * LAI)

        if (amp > Thresh) {
          const gain = Math.max(0, amp - Thresh) * AMtoIG_excite
          for (let x2i = 1; x2i <= xDim; x2i++) {
            const qRow = (x2i - 1) * yDim
            const kRow = (x2i - xi + xDim) * KW - yi + yDim
            const skipY = x2i === xi ? yi : -1
            for (let y2i = 1; y2i <= yDim; y2i++) {
              if (y2i === skipY) continue
              const somb = sombrero[kRow + y2i]
              if (somb < 0) IG_exAM[qRow + y2i - 1] += gain * somb * -1
            }
          }
        }
      }
    }

    // integrate
    for (let p = 0; p < N; p++) {
      const exLV = Math.min(IG_exLV[p], MaxLVtoIG)
      const exAM = Math.min(IG_exAM[p], MaxAMtoIG)
      IGex[p] = exLV + exAM
    }

    for (let s = 0; s < S; s++) {
      const evp = EVprev[s], lvp = LVprev[s], iip = IIprev[s]
      const evc = EVcur[s], lvc = LVcur[s], iic = IIcur[s]
      const eex = EV_ex[s], ein = EV_in[s], lex = LV_ex[s], lin = LV_in[s], iex = II_ex[s]
      const oEV = out.EV[s], oLV = out.LV[s], oII = out.II[s]
      for (let p = 0; p < N; p++) {
        const evExcite = dt_vm * ((EE - evp[p]) * eex[p])
        const lvExcite = dt_vm * ((EE - lvp[p]) * lex[p])
        const iiExcite = dt_vm_II * ((EE - iip[p]) * iex[p])
        const evLeak = dt_vm * (EL - evp[p])
        const lvLeak = dt_vm * (EL - lvp[p])
        const iiLeak = dt_vm_II * (EL - iip[p])
        const evInhib = dt_vm * ((EI - evp[p]) * ein[p])
        const lvInhib = dt_vm * ((EI - lvp[p]) * lin[p])
        evc[p] = Math.max(EI, evp[p] + evExcite + evInhib + evLeak)
        lvc[p] = Math.max(EI, lvp[p] + lvExcite + lvInhib + lvLeak)
        iic[p] = Math.max(EI, iip[p] + iiExcite + iiLeak)
      }
      writeTransposed(oEV, step, evc, xDim, yDim)
      writeTransposed(oLV, step, lvc, xDim, yDim)
      writeTransposed(oII, step, iic, xDim, yDim)
    }
    {
      const evp = EVprev[S], evc = EVcur[S], eex = EV_ex[S], ein = EV_in[S]
      for (let p = 0; p < N; p++) {
        const excite = dt_vm * ((EE - evp[p]) * eex[p])
        const leak = dt_vm * (EL - evp[p])
        const inhib = dt_vm * ((EI - evp[p]) * ein[p])
        evc[p] = Math.max(EI, evp[p] + excite + inhib + leak)
      }
      writeTransposed(out.EV[S], step, evc, xDim, yDim)
    }

    let n2 = 0
    for (let p = 0; p < N; p++) {
      const amp = AMprev[p], igp = IGprev[p]
      const amExcite = dt_vm * ((EE - amp) * AM_ex[p])
      // The reference overwrites AM_Current[excite] with the integrated value
      // *before* computing the EEG term from it, so the EEG uses amExcite.
      const amEEG = dt_vm * ((EE_EEG - amp) * amExcite)
      const igExcite = dt_vm_IG * ((EE - igp) * IGex[p])
      const amLeak = dt_vm * (EL - amp)
      const igLeak = dt_vm_IG * (EL - igp)
      const amInhib = dt_vm * ((EI - amp) * AM_in[p])
      const igInhib = dt_vm_IG * ((EI - igp) * IG_in[p])
      AMcur[p] = Math.max(EI, amp + amExcite + amInhib + amLeak)
      IGcur[p] = Math.max(EI, igp + igExcite + igInhib + igLeak)
      AM_eeg[p] = amEEG
      AM_in[p] = amInhib // reuse: store the integrated inhib for the N2pc below
    }
    // N2pc: sum of trimmed AM over the left half of x minus the right half
    // (the middle column at x = ceil(xDim/2) is excluded, as in the reference).
    for (let x = 0; x < xDim; x++) {
      if (x === halfX) continue
      const sign = x < halfX ? 1 : -1
      for (let y = 0; y < yDim; y++) {
        const p = ix(x, y)
        const trimmed = Math.max(0, AM_eeg[p] + AM_in[p])
        n2 += sign * trimmed
      }
    }
    n2pc[step] = n2
    writeTransposed(out.AM, step, AMcur, xDim, yDim)
    writeTransposed(out.IG, step, IGcur, xDim, yDim)

    // swap prev <- cur
    for (let s = 0; s < S; s++) {
      EVprev[s].set(EVcur[s]); LVprev[s].set(LVcur[s]); IIprev[s].set(IIcur[s])
    }
    EVprev[S].set(EVcur[S])
    AMprev.set(AMcur)
    IGprev.set(IGcur)

    if (opts.onProgress && (step % 8 === 0 || step === steps - 1)) {
      if (opts.onProgress((step + 1) / steps) === false) throw new AbortError()
    }
  }

  const wrap = (d: Float32Array): MapSeries => ({ data: d })
  return {
    steps, w: xDim, h: yDim, stimIndex,
    AM: wrap(out.AM), IG: wrap(out.IG),
    EV: out.EV.map(wrap), LV: out.LV.map(wrap), II: out.II.map(wrap),
    n2pc,
    elapsedMs: performance.now() - t0,
  }
}

/** Copy an [x][y] double grid into the row-major [y][x] float32 output at `step`. */
function writeTransposed(dst: Float32Array, step: number, src: Float64Array, xDim: number, yDim: number) {
  const base = step * xDim * yDim
  for (let x = 0; x < xDim; x++) {
    for (let y = 0; y < yDim; y++) {
      dst[base + y * xDim + x] = src[x * yDim + y]
    }
  }
}

export class AbortError extends Error {
  constructor() {
    super('simulation aborted')
    this.name = 'AbortError'
  }
}

/** Human-readable reasons an experiment can't run, in the order the model needs them fixed. */
/**
 * Bytes the result frames of a run will occupy in the browser: every map keeps
 * one Float32 grid per simulated ms (AM, IG, and EV/LV/II per stimulus type).
 */
export function estimateResultBytes(exp: Experiment): number {
  const cells = exp.canvas * exp.canvas
  const maps = 2 + 3 * Math.max(1, exp.stimulusTypes.length)
  return exp.runtime * cells * maps * 4
}
/** Above this the tab risks running out of memory (frames are transferred to the UI thread too). */
export const MAX_RESULT_BYTES = 400 * 1024 * 1024
export const WARN_RESULT_BYTES = 120 * 1024 * 1024

export function validate(exp: Experiment): string[] {
  const problems: string[] = []
  if (!Number.isInteger(exp.runtime) || exp.runtime < 1 || exp.runtime > 3000) problems.push('Runtime must be a whole number of ms between 1 and 3000.')
  if (!Number.isInteger(exp.canvas) || exp.canvas < 1 || exp.canvas > 50) problems.push('Canvas size must be a whole number between 1 and 50.')
  if (!Number.isInteger(exp.mask) || exp.mask < 1 || exp.mask > 10) problems.push('Mask size must be a whole number between 1 and 10.')
  if (exp.mask > exp.canvas) problems.push('Mask cannot be larger than the canvas.')
  if (Number.isFinite(exp.runtime) && Number.isFinite(exp.canvas)) {
    const bytes = estimateResultBytes(exp)
    if (bytes > MAX_RESULT_BYTES) problems.push(`This run would produce about ${Math.round(bytes / 1048576)} MB of results, more than the browser can safely hold (${Math.round(MAX_RESULT_BYTES / 1048576)} MB). Reduce the runtime, the canvas or the number of stimulus types.`)
  }
  if (exp.stimulusTypes.length === 0) problems.push('Add at least one stimulus type.')
  if (exp.objects.length === 0) problems.push('Place at least one visual object.')
  const ids = new Set(exp.stimulusTypes.map((s) => s.id))
  for (const st of exp.stimulusTypes) {
    if (!(st.td >= 0 && st.td <= 1)) problems.push(`Top-down weight for "${st.name}" must be between 0 and 1.`)
    if (!(st.bu >= 0 && st.bu <= 1)) problems.push(`Bottom-up weight for "${st.name}" must be between 0 and 1.`)
  }
  for (const o of exp.objects) {
    if (!ids.has(o.stimulus)) problems.push(`Object "${o.name}" has no stimulus type.`)
    if (!(o.x >= 1 && o.x <= exp.canvas && Number.isInteger(o.x))) problems.push(`Object "${o.name}": X must be a whole number between 1 and ${exp.canvas}.`)
    if (!(o.y >= 1 && o.y <= exp.canvas && Number.isInteger(o.y))) problems.push(`Object "${o.name}": Y must be a whole number between 1 and ${exp.canvas}.`)
    if (!(o.duration >= 0 && o.duration <= 1000)) problems.push(`Object "${o.name}": duration must be between 0 and 1000 ms.`)
    if (!(o.latency >= 0 && o.latency <= 1000)) problems.push(`Object "${o.name}": latency must be between 0 and 1000 ms.`)
  }
  return problems
}
