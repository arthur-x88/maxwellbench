"""Load frozen exam items and produce ground truth from oracles."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from maxwellbench.oracles import slab_field_grid, te10_field, te10_sparams, tmm_field_vs_z, tmm_sparams
from maxwellbench.tasks import ROOT

MANIFESTS = ROOT / "data" / "manifests"


def load_exam(regimes: list[str] | None = None, tracks: list[str] | None = None) -> list[dict]:
    names = regimes or ["photonic", "microwave", "board"]
    if tracks is None:
        if (MANIFESTS / "exam_photonic_meep.json").is_file():
            tracks = ["meep"]
        else:
            tracks = ["analytic"]
    items: list[dict] = []
    suffixes = []
    if "analytic" in tracks:
        suffixes.append("")
    if "meep" in tracks:
        suffixes.append("_meep")
    for name in names:
        for suffix in suffixes:
            path = MANIFESTS / f"exam_{name}{suffix}.json"
            if not path.is_file():
                continue
            with path.open(encoding="utf-8") as f:
                payload = json.load(f)
            for item in payload.get("items", []):
                item = dict(item)
                item["regime"] = payload["regime"]
                items.append(item)
    return items


def _grid(item: dict) -> tuple[np.ndarray, np.ndarray | None]:
    g = item["grid"]
    if "z" in g:
        z = np.linspace(g["z"][0], g["z"][1], int(g["nz"]))
        if "x" in g:
            x = np.linspace(g["x"][0], g["x"][1], int(g["nx"]))
            return z, x
        return z, None
    raise ValueError(f"{item['id']}: grid needs z")


def ground_truth(item: dict) -> dict[str, np.ndarray]:
    kind = item["oracle"]
    p = item["params"]
    out: dict[str, np.ndarray] = {}
    if kind == "tmm":
        f = np.asarray(p["frequencies_hz"], dtype=np.float64)
        s11, s21 = tmm_sparams(
            f,
            p["n_layers"],
            p["d_layers"],
            n0=p.get("n0", 1.0),
            ns=p.get("ns", 1.0),
            theta0=p.get("theta0", 0.0),
            pol=p.get("pol", "TE"),
        )
        out["S"] = np.stack([s11, s21], axis=0)
        z, _ = _grid(item)
        f0 = float(p["field_hz"])
        out["E"] = tmm_field_vs_z(
            f0,
            z,
            p["n_layers"],
            p["d_layers"],
            n0=p.get("n0", 1.0),
            ns=p.get("ns", 1.0),
            theta0=p.get("theta0", 0.0),
            pol=p.get("pol", "TE"),
        )
        return out
    if kind == "slab2d":
        z, x = _grid(item)
        assert x is not None
        out["E"] = slab_field_grid(
            float(p["frequency_hz"]),
            x,
            z,
            p["n_slab"],
            p["thickness"],
            n0=p.get("n0", 1.0),
            ns=p.get("ns", 1.0),
            theta0=p.get("theta0", 0.0),
            pol=p.get("pol", "TE"),
        )
        return out
    if kind == "te10":
        f = np.asarray(p["frequencies_hz"], dtype=np.float64)
        s11, s21 = te10_sparams(f, p["a"], p["length"], n=p.get("n", 1.0))
        out["S"] = np.stack([s11, s21], axis=0)
        z, x = _grid(item)
        assert x is not None
        out["E"] = te10_field(
            float(p["field_hz"]),
            x,
            z,
            p["a"],
            p["length"],
            n=p.get("n", 1.0),
        )
        return out
    if kind == "meep2d":
        path = ROOT / item["field_file"]
        if not path.is_file():
            raise FileNotFoundError(f"{item['id']}: missing {path}; run scripts/generate_meep_exam.py")
        with np.load(path) as z:
            return {"E": z["E"]}
    raise ValueError(f"{item['id']}: unknown oracle {kind}")


def incident_baseline(item: dict) -> dict[str, np.ndarray]:
    """No stack / empty guide: S11=0, S21=1, incident traveling wave only."""
    from maxwellbench.oracles import C0, _kz

    pred: dict[str, np.ndarray] = {}
    kind = item["oracle"]
    p = item["params"]
    if kind == "meep2d":
        pred["E"] = np.zeros_like(ground_truth(item)["E"])
        return pred
    if kind in {"tmm", "te10"}:
        n_f = len(p["frequencies_hz"])
        s = np.zeros((2, n_f), dtype=np.complex128)
        s[1] = 1.0
        pred["S"] = s
    z, x = _grid(item)
    if kind == "tmm":
        f0 = float(p["field_hz"])
        k0 = 2.0 * np.pi * f0 / C0
        n0 = p.get("n0", 1.0)
        kz = _kz(n0, k0, n0, p.get("theta0", 0.0))
        pred["E"] = np.exp(-1j * kz * z)
    elif kind == "slab2d":
        f0 = float(p["frequency_hz"])
        k0 = 2.0 * np.pi * f0 / C0
        n0 = p.get("n0", 1.0)
        theta = p.get("theta0", 0.0)
        kz = _kz(n0, k0, n0, theta)
        kx = k0 * n0 * np.sin(theta)
        xx, zz = np.meshgrid(x, z)
        pred["E"] = np.exp(-1j * (kx * xx + kz * zz))
    elif kind == "te10":
        assert x is not None
        f0 = float(p["field_hz"])
        k = 2.0 * np.pi * f0 * p.get("n", 1.0) / C0
        xx, zz = np.meshgrid(x, z)
        pred["E"] = np.sin(np.pi * xx / p["a"]) * np.exp(-1j * k * zz)
    return pred
