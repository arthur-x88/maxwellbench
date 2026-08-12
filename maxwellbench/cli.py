"""Thin CLIs. Generation and scoring logic lands here as the factory is wired."""

from __future__ import annotations

import argparse

from maxwellbench.tasks import all_tasks, bench_config


def eval_main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Score predictions against MaxwellBench.")
    p.add_argument("--predictions", required=False, help="directory of pred arrays (not yet wired)")
    p.parse_args(argv)
    cfg = bench_config()
    print(f"{cfg['name']} {cfg['version']}")
    for t in all_tasks():
        print(f"  {t.regime:10} {t.id:16} grid={t.grid} fom={t.fom}")
    print("evaluation against prediction shards is not implemented in 0.1.0")


def generate_main(argv: list[str] | None = None) -> None:
    p = argparse.ArgumentParser(description="Run the public-solver data factory.")
    p.add_argument("--regime", choices=["photonic", "microwave", "board"], required=False)
    p.parse_args(argv)
    print("corpus generation is specified in docs/DATA_FACTORY.md; solver farm is not in 0.1.0")
