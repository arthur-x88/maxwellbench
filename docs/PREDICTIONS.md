# Submitting a score

Default track (`meep`) scores **forward Ez** on 15 frozen 2D FDTD cases. Ground truth is Meep 1.34 DFT fields in `data/exam_fields/{id}.npz`. Inverse design and 3D are not scored.

```bash
pip install -e .
maxwellbench-eval --baseline incident --out scores.json
maxwellbench-eval --predictions ./preds --out scores.json
maxwellbench-eval --track analytic --baseline incident --out scores_analytic.json
```

`preds/` contains one `{id}.npz` per item.

| Track | key | shape |
| --- | --- | --- |
| meep | `E` | 2D complex, same as the shipped field file |
| analytic | `E`, optional `S` | see item `grid`; `S` is `(2, F)` = S11, S21 |

Phase of `E` is aligned by one global factor before nRMSE. Do not rescale amplitude.

Meep cases are defined in `maxwellbench/meep_cases.py`. To regenerate labels (needs Meep 1.34 in WSL or Linux):

```bash
scripts/run_meep_exam.sh
```

The published Meep baseline is a zero field (nRMSE 1.0). The analytic incident-wave baseline is `data/baselines/incident.json`.

A row is `scores.json` plus: parameter count, training data, wall-clock, `configs/bench.yaml` version.
