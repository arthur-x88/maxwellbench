# MaxwellBench

A public evaluation harness for electromagnetic foundation models.

Most neural Maxwell papers train and score on a private set drawn from one template family: one patch antenna, one metasurface, one board stackup. Those numbers do not transfer. There is also no public corpus of Maxwell solutions large enough to train on, so every group builds its own data and its own exam.

MaxwellBench is the exam. v0.1.1 scores forward fields and S-parameters on 15 frozen closed-form items (layered media, slabs, TE10). A later freeze will add Meep / openEMS 3D structures. Inverse design and active learning are specified and not scored yet.

## Community

- [Discord](https://discord.gg/gw5WGZWHFS)
- [X](https://x.com/Hyper88)

## What is scored

Three tasks. A model that only hits in-distribution S-parameters is a surrogate. That can be useful. It is not what this bench ranks.

| Task | Requirement |
| --- | --- |
| Forward fields | Predict **E** and **H** on the evaluation grid, and S-parameters when ports exist. Target: magnitude-weighted S-error below 1 dB on the task band, plus field nRMSE. |
| Cross-regime | Same weights on photonics, microwave, and a two-layer board coupon. Train on two regimes, evaluate few-shot on the third. |
| Active learning | Generation *n* selects the next batch of geometries. Generation *n+1*, same solver budget, is compared to random, Sobol, and an expert template grid on the held-out split. |

S-parameters without fields are reported and are not sufficient. A network that matches ports can still be wrong inside the volume.

Full definitions are in [docs/SPEC.md](docs/SPEC.md), [docs/TASKS.md](docs/TASKS.md), and [docs/METRICS.md](docs/METRICS.md).

## Regimes

| Track | Public solver | Objects | Outputs |
| --- | --- | --- | --- |
| `photonic` | [Meep](https://github.com/NanoComp/meep) (FDTD and adjoint) | Metalens, mode converter, meta-atom | Volume or slice fields, transmission, focus metric |
| `microwave` | [openEMS](https://github.com/thliebig/openEMS) | Pixelated patch, filter, small array tile | Near-field, far-field, S-parameters |
| `board` | openEMS | Two-layer metal/dielectric coupon | S-parameters and near-field on the coupon |

Exam items are recreated from published papers (IEEE TAP, Meep inverse-design examples, documented metasurfaces). Their IDs are frozen and are not used for training.

## Data

Exam truth is produced by the oracles in `maxwellbench/oracles.py` from the JSON in `data/manifests/`. There is no field dump to download. See [docs/PREDICTIONS.md](docs/PREDICTIONS.md).

Meep and openEMS are the planned 3D oracles. They are not required to sit the current exam. HFSS and CST are not dependencies.

## Layout

```
configs/        frozen protocol and per-regime templates
docs/           spec, tasks, metrics, factory
maxwellbench/   metrics, task loaders
scripts/        generate, evaluate, active-learn
data/manifests/ exam IDs (empty until items are recreated and hashed)
```

## Status

v0.1.1 is a runnable forward exam: 15 analytic items, a scorer, and an incident-wave baseline. The 3D FDTD exam, inverse track, and active-learn track are not shipping.

```bash
pip install -e .
maxwellbench-eval --baseline incident --out scores.json
```

Published incident baseline (see `data/baselines/incident.json`): mean aligned field nRMSE 0.738, mean S-parameter wMAE 84.1 dB. Beat both.

## Install

```bash
pip install -e .
```

Optional solver extras:

```bash
pip install -e ".[photonic]"
pip install -e ".[microwave]"
```

## License

Code is Apache-2.0. Benchmark item descriptions and frozen IDs are CC-BY-4.0. Recreated published geometries remain under their original paper copyrights. This repo ships parameters and hashes, not figures.

## Citation

See `CITATION.cff`. Until a paper exists, cite the repository.
