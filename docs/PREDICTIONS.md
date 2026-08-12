# Submitting a score

v0.1.1 scores **forward fields and S-parameters** on 15 frozen analytic items. Inverse design, few-shot transfer, and active learning are specified and not scored yet.

## Run

```bash
pip install -e .
maxwellbench-eval --baseline incident --out scores.json
maxwellbench-eval --predictions ./preds --out scores.json
```

`preds/` contains one file per item: `{id}.npz`.

| key | shape | notes |
| --- | --- | --- |
| `E` | matches the item grid | complex128, SI, e^{+jωt} |
| `S` | `(2, F)` | `S[0]=S11`, `S[1]=S21`, only on `tmm` and `te10` items |

Grid axes are in the item JSON (`grid.z`, optional `grid.x`). `E` is `shape (nz,)` for 1D TMM and `(nz, nx)` for slab2d / te10.

Phase of `E` is aligned with a single global factor before nRMSE. Do not rescale amplitude.

## What is on the exam

Closed-form Maxwell, not FDTD:

| Oracle | Physics |
| --- | --- |
| `tmm` | Stratton / transfer-matrix stack. S11, S21, E(z). |
| `slab2d` | One dielectric slab, plane wave at an angle, E(x,z). |
| `te10` | Matched rectangular TE10 section, including cutoff. |

Five items in each of `photonic`, `microwave`, `board`. IDs live in `data/manifests/exam_*.json`. Ground truth is computed from those parameters. There is no downloaded field dump.

The published baseline is `--baseline incident`: no stack, S21=1, incident wave only.

## What a row must include

`scores.json` from this CLI, plus in the PR or issue: parameter count, what you trained on, wall-clock, and `configs/bench.yaml` version.

A Meep / openEMS 3D exam is not in this version. Do not compare these numbers to HFSS.
