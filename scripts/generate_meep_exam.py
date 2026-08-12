#!/usr/bin/env python3
"""Run the 2D Meep exam and write data/exam_fields/{id}.npz plus manifests."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from maxwellbench.meep_cases import CASES, run_case  # noqa: E402

OUT = ROOT / "data" / "exam_fields"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    by_regime: dict[str, list[dict]] = {"photonic": [], "microwave": [], "board": []}
    for case in CASES:
        dest = OUT / f"{case.id}.npz"
        print(f"running {case.id} ...", flush=True)
        arrays = run_case(case)
        np_savez = __import__("numpy").savez_compressed
        np_savez(dest, **arrays, cell=case.cell, frequency=case.frequency, resolution=case.resolution)
        by_regime[case.regime].append(
            {
                "id": case.id,
                "oracle": "meep2d",
                "params": {
                    "geometry": case.geometry,
                    "cell": list(case.cell),
                    "resolution": case.resolution,
                    "frequency": case.frequency,
                    "pml": case.pml,
                    "until": case.until,
                    **case.params,
                },
                "field_file": f"data/exam_fields/{case.id}.npz",
            }
        )
        print(f"  wrote {dest} E{arrays['E'].shape}", flush=True)

    man_dir = ROOT / "data" / "manifests"
    for regime, items in by_regime.items():
        path = man_dir / f"exam_{regime}_meep.json"
        path.write_text(json.dumps({"regime": regime, "oracle": "meep2d", "items": items}, indent=2), encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()
