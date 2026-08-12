# Tasks

Each task is a YAML under `configs/` plus a loader in `maxwellbench.tasks`.

## Regime A — photonic (`photonic`)

Solver: Meep FDTD, adjoint available for baselines.

| Task ID | Object | Source of exam items | Predict / emit |
| --- | --- | --- | --- |
| `pho.metalens` | Achromatic or monochromatic metalens | Meep adjoint examples + published metalens papers | Focal field, Strehl / focusing efficiency |
| `pho.modeconv` | Waveguide mode converter | Published silicon-photonics inverse designs | Transmission, mode overlap, volume fields |
| `pho.metaatom` | Periodic meta-atom | Literature unit cells | Complex transmission / reflection vs λ |

Template grammar (train): binary or level-set permittivity on a regular grid, min-feature filter, substrate optional. Wavelengths in the near-IR / visible band listed in `configs/photonic.yaml`.

## Regime B — microwave (`microwave`)

Solver: openEMS.

| Task ID | Object | Source of exam items | Predict / emit |
| --- | --- | --- | --- |
| `mw.patch` | Pixelated microstrip patch | Recreated IEEE TAP pixel-antennas | S11, realized gain, E/H near-field |
| `mw.filter` | Planar microwave filter | Published hairpin / SIR / pixel filters | S11, S21 over band |
| `mw.tile` | Small array tile (≤ 8 elements) | Public array papers with dimensions | Embedded S, scan element pattern |

Template grammar: metal pixels on a dielectric slab, feed pin or inset, ground plane. Bands: 2.4, 5.8, 10, 24, 28 GHz families (see YAML). Not all families in one sample.

## Regime C — board coupon (`board`)

Solver: openEMS.

| Task ID | Object | Source of exam items | Predict / emit |
| --- | --- | --- | --- |
| `brd.coupon` | Two-layer metal/dielectric coupon with two ports | Recreated SI/RF coupons from public app notes and papers | Full S, near-field on a cut plane |
| `brd.coupler` | Coupled-line or branchline | Textbook + published layouts | S, isolation, field between traces |

This is the “64×64 two-layer grid” toy that makes the combinatorial point without pretending it is an F-35.

## Inverse protocol

1. Model emits geometry (grid or template parameters).
2. Geometry is legalized (min feature, connectivity of the feed, port presence).
3. Public solver runs with the **same** mesh recipe as the corpus (pinned in YAML).
4. Score is the task FoM on the solver output, not on the model’s self-prediction.
5. Baseline: Meep adjoint (photonic) or CMA-ES / random search (microwave, board) with a stated evaluation budget.

Wall-clock is wall-clock to first geometry that beats the baseline FoM, including legalization and failed solves. Do not hide retries.

## Few-shot transfer

Train on any two regimes. Evaluate forward-field and inverse on the third with k ∈ {0, 8, 32, 128} labelled examples from that regime’s `val` (not `exam`). `exam` is still zero-shot at the item level.

## Active learning

1. Start from a small labelled seed (N0, pinned).
2. Unlabelled `pool` is public.
3. Method proposes a batch B. We simulate B with the public solver (oracle).
4. Retrain or fine-tune. Repeat until budget Σ|B| = B_max.
5. After each batch, score `test_id` and `exam`.
6. Required baselines: uniform random, Sobol, uncertainty (ensemble variance), and “expert template grid” (round-robin through the grammar).

The headline plot is `exam` field error vs number of solver calls.
