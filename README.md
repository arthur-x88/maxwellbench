# MaxwellBench

Public evaluation harness for electromagnetic foundation models.

There is no ImageNet for Maxwell. Literature surrogates are trained and scored on private, single-family sets (one patch antenna, one metasurface class, one board stackup). Arena Physica said the quiet part out loud: there is no internet of Maxwell solutions. MaxwellBench is the exam. Anyone can sit it. The training corpus is generated from **public solvers**. The held-out items are **published structures**. The score that matters is whether one set of weights generalizes across regimes, and whether the model can choose the next simulation better than a human grid.

This repository is the specification, the task definitions, the metrics, and the factory that builds the public split. It is not a product studio and it is not a client-data warehouse.

## What the bench measures

Three claims. Fail any one and you have a surrogate paper, not a foundation model.

| Claim | Meaning |
| --- | --- |
| **Forward, full fields** | Geometry in. **E** and **H** out, plus S-parameters. Tens of milliseconds. Sub-1 dB magnitude-weighted S-error **and** a field error a physicist will not laugh at. |
| **One model, three regimes** | Same weights on photonics, microwave, and a two-layer board coupon. Train on two, few-shot the third. |
| **The model improves the next experiment** | Generation *n* picks the next 10k geometries by information gain. Generation *n+1*, same simulation budget, beats random / Sobol / expert-grid on the held-out split. That curve is ε in public. |

S-parameters alone are not enough. A model that only hits ports cannot claim it sees the fields.

## Three regimes

| Track | Solver (public) | Objects | Outputs |
| --- | --- | --- | --- |
| `photonic` | [Meep](https://github.com/NanoComp/meep) (FDTD + adjoint) | Metalens, mode converter, meta-atom | Volume / slice fields, transmission, focus metric |
| `microwave` | [openEMS](https://github.com/thliebig/openEMS) | Pixelated patch, filter, small array tile | Near-field, far-field, S-parameters |
| `board` | openEMS (FDTD) | Two-layer metal/dielectric coupon | S-parameters + near-field on the coupon |

Held-out exam items are recreated from published papers (IEEE TAP, Meep inverse-design examples, documented metasurfaces). Those IDs are frozen. They are not used for training.

See [docs/SPEC.md](docs/SPEC.md), [docs/TASKS.md](docs/TASKS.md), [docs/METRICS.md](docs/METRICS.md).

## Public data means this

1. **Public solvers** — Meep, openEMS. No HFSS/CST as a required dependency.
2. **You generate the corpus** — 1–10M geometry → field (and geometry → S) pairs from expert-seeded templates, not uniform random junk.
3. **Published structures are the exam** — listed, hashed, frozen.
4. **The exam is open.** Training recipes that make the next million samples cheap can stay closed. The split cannot.

Compare speed and error to Meep/openEMS first. A single paid HFSS run on a named public board is allowed as an appendix, with the project file. Do not claim 800,000× against a commercial solver without that protocol.

## Repository layout

```
maxwellbench/
  configs/           # frozen bench + per-regime templates
  docs/              # spec, tasks, metrics, factory, demo
  maxwellbench/      # Python package (metrics, tasks, solvers, generate)
  scripts/           # corpus generation, evaluate, active-learn
```

## Status

Specification and harness skeleton. Corpus generation and the first frozen split are the next commit, not this one.

## Install (harness only)

```bash
pip install -e .
```

Solvers are optional extras:

```bash
pip install -e ".[photonic]"   # Meep
pip install -e ".[microwave]"  # openEMS bindings, if available
```

## License

Apache-2.0 for code. Benchmark item descriptions and frozen IDs are CC-BY-4.0. Recreated published geometries remain under their original paper copyrights; we ship parameters and hashes, not pirated figures.

## Cite

See `CITATION.cff`. Until a paper lands, cite this repository.
