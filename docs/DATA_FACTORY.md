# Data factory

There is no public Maxwell corpus worth training on. The factory **is** the dataset.

## Principles

1. Sample from a **template grammar**, not from a uniform pixel prior. Almost all random metal is electromagnetically dead. Dead samples waste solver hours and teach the model the wrong measure.
2. Every sample stores: template ID, parameter vector, raster grid, material table, solver recipe hash, fields, S (if any), wall-clock, mesh stats.
3. Reject on solver failure, unfinished transients, or port-calibration residual above the YAML threshold. Do not impute.
4. Min-feature and connectivity constraints are applied **before** the solver. Illegal geometry is not a negative example unless the task says so.
5. The factory is allowed to stay partly closed (the grammar that makes the next million cheap). The **manifest schema** and the **exam IDs** are not.

## Generation loop

```
template ~ grammar(regime)
params   ~ prior(template)          # expert-seeded, not U[0,1]^d
geom     = rasterize(template, params)
geom     = legalize(geom)           # min feature, feed connected
if not legal: continue
result   = public_solver(geom, recipe)
if not converged: log and continue
write sample + hash
```

Active learning replaces `params ~ prior` with `params ~ q_θ` (the model’s acquisition).

## Target scale (v0)

| Regime | Order of labelled samples | Notes |
| --- | --- | --- |
| photonic | 3×10^5 – 1×10^6 | Meep is slower; adjoint samples are gold |
| microwave | 1×10^6 – 3×10^6 | Pixel patches are cheap-ish |
| board | 3×10^5 – 1×10^6 | Two-port coupons |

A serious forward model can start showing life at ~10^5 per regime. The few-shot and active-learn claims need the pool and the exam, not just more ID samples.

## Storage

- Grid + fields: chunked HDF5 / Zarr, one shard per template family.
- Sidecar parquet: IDs, params, S, metrics, hashes.
- Do not commit shards. Commit `data/manifests/*.json` and the exam parameter files.

## Exam recreation

Each `exam` item is a small JSON: citation, dimensions, materials, ports, frequency list, raster hash. A third party with Meep/openEMS must be able to regenerate the solver-truth from that JSON. If they cannot, the item is not in the bench.

## Sim-to-real (v1, not v0)

When a measurement cell exists:

- Store as-designed grid, as-built metrology, S, near-field.
- Score models on as-built → measured, not only as-designed → solver.
- Fixture and de-embed recipe is part of the item. Uncalibrated VNA traces are not labels.
