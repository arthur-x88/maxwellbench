# Contributing

This repo is the exam. Treat it that way.

- **New exam item:** JSON with citation, full dimensions, materials, ports, solver recipe, raster hash. A stranger must be able to regenerate the fields. Open a PR against `data/manifests/`. Bump `configs/bench.yaml` patch version.
- **New metric:** implement in `maxwellbench/metrics.py`, document in `docs/METRICS.md`, add a test. Changing a formula is a minor version bump.
- **New task / regime:** major version. Discuss in an issue first.
- **Training shards:** do not commit. Do not open PRs that add `.h5` / `.npz`.
- **Commercial solvers:** appendix comparisons only, with the project file. Not a dependency.

Code is Apache-2.0. Do not paste client geometries, ITAR, or unpublished vendor boards into `exam`.
