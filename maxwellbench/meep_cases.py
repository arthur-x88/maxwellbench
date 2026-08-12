"""2D Meep exam geometries.

Meep units: c = 1. Each case dumps a DFT Ez array on the cell.
S-parameters are not scored on this track (flux without a blank-cell
calibration is not S).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class MeepCase:
    id: str
    regime: str
    cell: tuple[float, float]
    resolution: int
    frequency: float
    pml: float
    until: float
    geometry: str
    params: dict


CASES: list[MeepCase] = [
    MeepCase("pho.meep.straight_wg", "photonic", (16.0, 8.0), 20, 0.15, 1.0, 200.0, "straight_wg", {"w": 1.0, "eps": 12.0, "src_x": -6.0}),
    MeepCase("pho.meep.bend90", "photonic", (16.0, 16.0), 18, 0.15, 1.0, 280.0, "bend90", {"w": 1.0, "eps": 12.0}),
    MeepCase("pho.meep.y_split", "photonic", (16.0, 10.0), 18, 0.15, 1.0, 260.0, "y_split", {"w": 1.0, "eps": 12.0, "split": 2.5}),
    MeepCase("pho.meep.holey_cavity", "photonic", (16.0, 8.0), 20, 0.25, 1.0, 240.0, "holey_cavity", {"w": 1.0, "eps": 12.0, "r": 0.25, "n_holes": 3}),
    MeepCase("pho.meep.ring", "photonic", (16.0, 16.0), 16, 0.15, 1.0, 360.0, "ring", {"w": 1.0, "eps": 12.0, "r": 1.8, "pad": 0.15}),
    MeepCase("mw.meep.cyl_scatter", "microwave", (12.0, 12.0), 20, 0.20, 1.0, 180.0, "cylinder", {"r": 0.6, "eps": 4.0, "src_x": -4.5}),
    MeepCase("mw.meep.pec_slit", "microwave", (14.0, 10.0), 20, 0.18, 1.0, 200.0, "pec_slit", {"gap": 0.8, "th": 0.3}),
    MeepCase("mw.meep.pec_guide", "microwave", (14.0, 6.0), 20, 0.22, 1.0, 200.0, "pec_guide", {"w": 2.0}),
    MeepCase("mw.meep.strip_on_slab", "microwave", (14.0, 8.0), 18, 0.16, 1.0, 220.0, "strip_on_slab", {"w": 1.2, "th": 0.2, "h_sub": 1.0, "eps_sub": 4.0}),
    MeepCase("mw.meep.two_cyl", "microwave", (14.0, 10.0), 18, 0.19, 1.0, 200.0, "two_cyl", {"r": 0.45, "eps": 6.0, "sep": 1.6}),
    MeepCase("brd.meep.microstrip2d", "board", (14.0, 6.0), 20, 0.14, 0.8, 220.0, "microstrip2d", {"w": 0.6, "h": 0.4, "eps": 4.0}),
    MeepCase("brd.meep.coupled", "board", (14.0, 6.0), 20, 0.14, 0.8, 240.0, "coupled", {"w": 0.5, "gap": 0.25, "h": 0.4, "eps": 4.0}),
    MeepCase("brd.meep.step", "board", (14.0, 6.0), 20, 0.14, 0.8, 220.0, "step", {"h": 0.4, "eps": 4.0}),
    MeepCase("brd.meep.gap", "board", (14.0, 6.0), 20, 0.14, 0.8, 220.0, "gap", {"gap": 0.35, "h": 0.4, "eps": 4.0}),
    MeepCase("brd.meep.stub", "board", (14.0, 8.0), 18, 0.14, 0.8, 260.0, "stub", {"stub": 1.8, "h": 0.4, "eps": 4.0}),
]


def build_geometry(mp, case: MeepCase):
    p = case.params
    metal = mp.metal
    g = case.geometry
    med = lambda e: mp.Medium(epsilon=e)

    if g == "straight_wg":
        return [mp.Block(size=mp.Vector3(mp.inf, p["w"], mp.inf), center=mp.Vector3(), material=med(p["eps"]))]
    if g == "bend90":
        w, e = p["w"], p["eps"]
        return [
            mp.Block(size=mp.Vector3(case.cell[0] * 0.5 + w, w, mp.inf), center=mp.Vector3(-case.cell[0] * 0.25, 0), material=med(e)),
            mp.Block(size=mp.Vector3(w, case.cell[1] * 0.5 + w, mp.inf), center=mp.Vector3(0, case.cell[1] * 0.25), material=med(e)),
        ]
    if g == "y_split":
        w, e, s = p["w"], p["eps"], p["split"]
        return [
            mp.Block(size=mp.Vector3(case.cell[0] * 0.5, w, mp.inf), center=mp.Vector3(-case.cell[0] * 0.25, 0), material=med(e)),
            mp.Block(size=mp.Vector3(case.cell[0] * 0.5, w, mp.inf), center=mp.Vector3(case.cell[0] * 0.25, s), material=med(e)),
            mp.Block(size=mp.Vector3(case.cell[0] * 0.5, w, mp.inf), center=mp.Vector3(case.cell[0] * 0.25, -s), material=med(e)),
        ]
    if g == "holey_cavity":
        objs = [mp.Block(size=mp.Vector3(mp.inf, p["w"], mp.inf), center=mp.Vector3(), material=med(p["eps"]))]
        for i in range(1, int(p["n_holes"]) + 1):
            objs.append(mp.Cylinder(radius=p["r"], center=mp.Vector3(-float(i)), material=mp.air))
            objs.append(mp.Cylinder(radius=p["r"], center=mp.Vector3(float(i)), material=mp.air))
        return objs
    if g == "ring":
        w, e, rad = p["w"], p["eps"], p["r"]
        return [
            mp.Block(size=mp.Vector3(mp.inf, w, mp.inf), center=mp.Vector3(0, -(rad + p["pad"] + w)), material=med(e)),
            mp.Cylinder(radius=rad + w / 2, material=med(e)),
            mp.Cylinder(radius=rad - w / 2, material=mp.air),
        ]
    if g == "cylinder":
        return [mp.Cylinder(radius=p["r"], material=med(p["eps"]))]
    if g == "two_cyl":
        s = p["sep"] / 2.0
        m = med(p["eps"])
        return [
            mp.Cylinder(radius=p["r"], center=mp.Vector3(0, s), material=m),
            mp.Cylinder(radius=p["r"], center=mp.Vector3(0, -s), material=m),
        ]
    if g == "pec_slit":
        gap, th, h = p["gap"], p["th"], case.cell[1]
        return [
            mp.Block(size=mp.Vector3(th, (h - gap) / 2, mp.inf), center=mp.Vector3(0, (h + gap) / 4), material=metal),
            mp.Block(size=mp.Vector3(th, (h - gap) / 2, mp.inf), center=mp.Vector3(0, -(h + gap) / 4), material=metal),
        ]
    if g == "pec_guide":
        w, h = p["w"], case.cell[1]
        wall = (h - w) / 2
        return [
            mp.Block(size=mp.Vector3(mp.inf, wall, mp.inf), center=mp.Vector3(0, (w + wall) / 2), material=metal),
            mp.Block(size=mp.Vector3(mp.inf, wall, mp.inf), center=mp.Vector3(0, -(w + wall) / 2), material=metal),
        ]
    if g == "strip_on_slab":
        return [
            mp.Block(size=mp.Vector3(mp.inf, p["h_sub"], mp.inf), center=mp.Vector3(0, -p["h_sub"] / 2), material=med(p["eps_sub"])),
            mp.Block(size=mp.Vector3(mp.inf, p["th"], mp.inf), center=mp.Vector3(0, p["th"] / 2), material=metal),
        ]

    h, e = p["h"], p["eps"]
    th = 0.08
    ground = mp.Block(size=mp.Vector3(mp.inf, 0.08, mp.inf), center=mp.Vector3(0, -h - 0.04), material=metal)
    sub = mp.Block(size=mp.Vector3(mp.inf, h, mp.inf), center=mp.Vector3(0, -h / 2), material=med(e))
    if g == "microstrip2d":
        return [ground, sub, mp.Block(size=mp.Vector3(mp.inf, th, mp.inf), center=mp.Vector3(0, th / 2), material=metal)]
    if g == "coupled":
        return [
            ground,
            sub,
            mp.Block(size=mp.Vector3(mp.inf, th, mp.inf), center=mp.Vector3(0, th / 2), material=metal),
            mp.Block(size=mp.Vector3(mp.inf, th, mp.inf), center=mp.Vector3(0, th / 2 + p["gap"] + th), material=metal),
        ]
    if g == "step":
        return [
            ground,
            sub,
            mp.Block(size=mp.Vector3(case.cell[0] / 2, th, mp.inf), center=mp.Vector3(-case.cell[0] / 4, th / 2), material=metal),
            mp.Block(size=mp.Vector3(case.cell[0] / 2, th * 2, mp.inf), center=mp.Vector3(case.cell[0] / 4, th), material=metal),
        ]
    if g == "gap":
        L, gap = case.cell[0], p["gap"]
        half = (L - gap) / 2
        return [
            ground,
            sub,
            mp.Block(size=mp.Vector3(half, th, mp.inf), center=mp.Vector3(-(gap + half) / 2, th / 2), material=metal),
            mp.Block(size=mp.Vector3(half, th, mp.inf), center=mp.Vector3((gap + half) / 2, th / 2), material=metal),
        ]
    if g == "stub":
        return [
            ground,
            sub,
            mp.Block(size=mp.Vector3(mp.inf, th, mp.inf), center=mp.Vector3(0, th / 2), material=metal),
            mp.Block(size=mp.Vector3(th, p["stub"], mp.inf), center=mp.Vector3(0, th + p["stub"] / 2), material=metal),
        ]
    raise ValueError(g)


def run_case(case: MeepCase) -> dict[str, np.ndarray]:
    import meep as mp

    cell = mp.Vector3(case.cell[0], case.cell[1], 0)
    src_x = case.params.get("src_x", -(case.cell[0] / 2 - case.pml - 0.8))
    sim = mp.Simulation(
        cell_size=cell,
        boundary_layers=[mp.PML(case.pml)],
        geometry=build_geometry(mp, case),
        sources=[
            mp.Source(
                mp.GaussianSource(case.frequency, fwidth=0.1 * case.frequency),
                component=mp.Ez,
                center=mp.Vector3(src_x, 0),
                size=mp.Vector3(0, min(2.0, case.cell[1] * 0.4)),
            )
        ],
        resolution=case.resolution,
        default_material=mp.air,
    )
    dft = sim.add_dft_fields(
        [mp.Ez],
        case.frequency,
        case.frequency,
        1,
        center=mp.Vector3(),
        size=cell,
    )
    sim.run(until_after_sources=case.until)
    ez = np.asarray(sim.get_dft_array(dft, mp.Ez, 0), dtype=np.complex64)
    return {"E": ez}
