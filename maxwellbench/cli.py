"""CLI entry points."""

from __future__ import annotations

import argparse
from pathlib import Path

from maxwellbench.evaluate import evaluate, write_scores
from maxwellbench.tasks import all_tasks, bench_config


def eval_main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Score predictions against MaxwellBench.")
    p.add_argument("--predictions", type=Path, default=None, help="directory of {id}.npz files")
    p.add_argument(
        "--baseline",
        choices=["incident"],
        default=None,
        help="score a built-in baseline instead of files",
    )
    p.add_argument("--out", type=Path, default=Path("scores.json"))
    p.add_argument("--regime", action="append", dest="regimes")
    args = p.parse_args(argv)
    if args.predictions is None and args.baseline is None:
        p.error("pass --predictions DIR or --baseline incident")
    result = evaluate(predictions=args.predictions, baseline=args.baseline, regimes=args.regimes)
    write_scores(result, args.out)
    s = result["summary"]
    print(f"{result['bench']} {result['version']}")
    print(f"scored {s['n_scored']}/{s['n_items']} items")
    print(f"mean e_nrmse_aligned: {s['e_nrmse_aligned_mean']}")
    print(f"mean s_wmae_db:       {s['s_wmae_db_mean']}")
    print(f"wrote {args.out}")


def generate_main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Run the public-solver data factory.")
    p.add_argument("--regime", choices=["photonic", "microwave", "board"], required=False)
    p.parse_args(argv)
    cfg = bench_config()
    print(f"{cfg['name']} {cfg['version']}")
    for t in all_tasks():
        print(f"  {t.regime:10} {t.id:16}")
    print("Meep/openEMS corpus generation is not in 0.1.1. Exam truth is analytic (see docs/PREDICTIONS.md).")
