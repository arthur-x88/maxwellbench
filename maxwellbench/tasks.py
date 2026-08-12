"""Task and regime loaders. YAML is the source of truth for IDs."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIGS = ROOT / "configs"


@dataclass(frozen=True)
class Task:
    id: str
    regime: str
    grid: list
    fom: str


def load_yaml(name: str) -> dict:
    path = CONFIGS / name
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def bench_config() -> dict:
    return load_yaml("bench.yaml")


def regime_config(regime: str) -> dict:
    return load_yaml(f"{regime}.yaml")


def all_tasks() -> list[Task]:
    out: list[Task] = []
    for regime in bench_config()["regimes"]:
        cfg = regime_config(regime)
        for t in cfg["tasks"]:
            out.append(Task(id=t["id"], regime=regime, grid=t["grid"], fom=t["fom"]))
    return out
