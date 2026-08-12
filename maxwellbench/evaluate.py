"""Score a prediction directory against the frozen exam."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from maxwellbench.exam import ground_truth, incident_baseline, load_exam
from maxwellbench.metrics import field_nrmse, field_nrmse_aligned, s_complex_rmse, s_phase_mae_deg, s_wmae_db
from maxwellbench.tasks import bench_config


def _load_pred(directory: Path | None, item_id: str) -> dict[str, np.ndarray] | None:
    if directory is None:
        return None
    path = directory / f"{item_id}.npz"
    if not path.is_file():
        return None
    with np.load(path) as z:
        return {k: z[k] for k in z.files}


def score_item(item: dict, pred: dict[str, np.ndarray] | None) -> dict:
    gt = ground_truth(item)
    row: dict = {"id": item["id"], "regime": item["regime"], "oracle": item["oracle"]}
    if pred is None:
        row["missing"] = True
        return row
    row["missing"] = False
    if "S" in gt:
        if "S" not in pred:
            row["missing_S"] = True
        else:
            row["s_wmae_db"] = s_wmae_db(pred["S"], gt["S"])
            row["s_phase_mae_deg"] = s_phase_mae_deg(pred["S"], gt["S"])
            row["s_complex_rmse"] = s_complex_rmse(pred["S"], gt["S"])
    if "E" in gt:
        if "E" not in pred:
            row["missing_E"] = True
        else:
            row["e_nrmse"] = field_nrmse(pred["E"], gt["E"])
            row["e_nrmse_aligned"] = field_nrmse_aligned(pred["E"], gt["E"])
    return row


def evaluate(
    predictions: Path | None = None,
    baseline: str | None = None,
    regimes: list[str] | None = None,
    tracks: list[str] | None = None,
) -> dict:
    items = load_exam(regimes, tracks=tracks)
    rows = []
    for item in items:
        if baseline == "incident":
            pred = incident_baseline(item)
        else:
            pred = _load_pred(predictions, item["id"])
        rows.append(score_item(item, pred))
    scored = [r for r in rows if not r.get("missing") and "e_nrmse_aligned" in r]
    summary = {
        "n_items": len(rows),
        "n_scored": len(scored),
        "e_nrmse_aligned_mean": (
            float(np.mean([r["e_nrmse_aligned"] for r in scored])) if scored else None
        ),
        "s_wmae_db_mean": (
            float(np.mean([r["s_wmae_db"] for r in rows if "s_wmae_db" in r]))
            if any("s_wmae_db" in r for r in rows)
            else None
        ),
    }
    return {
        "bench": bench_config()["name"],
        "version": bench_config()["version"],
        "baseline": baseline,
        "summary": summary,
        "items": rows,
    }


def write_scores(result: dict, dest: Path | str) -> None:
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2), encoding="utf-8")
