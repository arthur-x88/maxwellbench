# MaxwellBench specification

Status: draft, frozen-split pending. Version the YAML in `configs/bench.yaml`, not this prose.

## Purpose

Score a geometry → field (and inverse) model the way a physicist would reject a liar:

- Does it predict **fields**, not only ports?
- Does one set of weights work across **frequency, scale, and material class**?
- Does it **choose the next simulation** better than a budget-matched random or expert grid?

A model that wins only on in-distribution S-parameters of one template family is a surrogate. It can be useful. It is not what this bench exists to crown.

## Units and conventions

- SI units everywhere. Geometry in metres, frequency in Hz, fields in V/m and A/m.
- Time-harmonic convention \(e^{+j\omega t}\) unless a task file says otherwise (Meep is \(e^{-j\omega t}\); converters live in `maxwellbench.solvers`).
- S-parameters are complex, referenced to the port impedance in the task file (default 50 Ω).
- Geometry is a voxel occupancy / material ID grid plus a continuous parameter vector for the template. Both are stored. Inverse models may emit either; the scorer rasterizes to the grid the solver used.

## Splits

| Split | Role | Leakage rule |
| --- | --- | --- |
| `train` | Synthetic, template-sampled | May be regenerated; not scored |
| `pool` | Unlabelled synthetic pool for active learning | No labels in the public release of the *query* set |
| `val` | Synthetic, same families as train | For model selection only |
| `test_id` | Synthetic, same families, held-out seeds | In-distribution forward / inverse |
| `test_ood` | Template families never seen in train | Near-OOD |
| `exam` | Recreated **published** structures | Frozen IDs. Never train. Never tune. |

`exam` is the only number that may be advertised. `test_id` is for ablations.

## Tasks (summary)

Full definitions: [TASKS.md](TASKS.md).

1. **Forward-field** — predict E, H on a specified grid (and S if ports exist).
2. **Forward-S** — predict S(f) only. Reported, not sufficient.
3. **Inverse-from-spec** — target metric or S-mask → geometry. Solver-verified.
4. **Few-shot transfer** — train on two regimes, k-shot the third (k ∈ {0, 8, 32, 128}).
5. **Active-learn** — fixed simulation budget, model proposes the next batch, retrain, score `exam` + `test_id`.

## What is out of scope for v0

- Nonlinear media, plasma, moving matter.
- Full-packaged SoC + enclosure + human body.
- Commercial solver bit-exactness.
- Fabricated ground truth (v1, after the first cell exists).

v0 is solver-truth. Sim-to-real is a later track, with as-built metrology as a first-class label.

## Versioning

`maxwellbench-v0.1` is the first frozen exam list + metric code. Changing an exam ID or a metric formula requires a minor version bump. Changing a task definition requires a major bump.

## Protocol for a public claim

A leaderboard row must include:

- Model name, parameter count, training regime IDs, number of solver-hours.
- Forward field error and S error on `exam`, per regime.
- Inverse figure-of-merit vs the published adjoint / CMA-ES baseline, wall-clock to that FoM.
- Few-shot matrix (train on {A,B} → C).
- Active-learn curve vs random and Sobol, same budget.
- Solver versions (`meep`, `openEMS`) and `configs/bench.yaml` git hash.

No HFSS multiplier without the project file and mesh report in the appendix.
