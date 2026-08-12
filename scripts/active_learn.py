#!/usr/bin/env python3
"""Budget-matched active-learning curves.

Required baselines (docs/TASKS.md): random, Sobol, uncertainty ensemble, expert grid.
Headline: exam field nRMSE vs solver calls.
"""

from __future__ import annotations

import argparse

from maxwellbench.tasks import bench_config


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--budget", type=int, default=None)
    args = p.parse_args()
    cfg = bench_config()["active_learn"]
    budget = args.budget or cfg["b_max"]
    print(f"active-learn protocol: n0={cfg['n0']} batch={cfg['batch']} b_max={budget}")
    print("baselines:", ", ".join(cfg["baselines"]))
    print("oracle + retrain loop is not implemented in 0.1.0")


if __name__ == "__main__":
    main()
