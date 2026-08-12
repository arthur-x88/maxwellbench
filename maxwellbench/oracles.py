"""Closed-form Maxwell oracles. No Meep, no SciPy.

v0.1 exam truth is produced here. Sign convention: e^{+j ω t},
propagation e^{-j k z} for +z travel.
"""

from __future__ import annotations

import numpy as np

C0 = 299792458.0
Z0 = 376.730313668
EPS = 1e-15


def _kz(n: np.ndarray, k0: float, n0: complex, theta0: float) -> np.ndarray:
    arg = np.asarray(n, dtype=np.complex128) ** 2 - (n0 * np.sin(theta0)) ** 2
    s = np.sqrt(arg)
    s = np.where(np.imag(s) > 0, -s, s)
    return k0 * s


def _admittance(n, kz, k0, pol: str) -> np.ndarray:
    if pol.upper() == "TE":
        return kz / (k0 * Z0 + EPS)
    return (k0 * np.asarray(n, dtype=np.complex128) ** 2) / (kz * Z0 + EPS)


def tmm_sparams(
    frequencies_hz: np.ndarray,
    n_layers: list[complex],
    d_layers: list[float],
    n0: complex = 1.0,
    ns: complex = 1.0,
    theta0: float = 0.0,
    pol: str = "TE",
) -> tuple[np.ndarray, np.ndarray]:
    """Return S11, S21 (power-normalized) vs frequency."""
    f = np.asarray(frequencies_hz, dtype=np.float64)
    s11 = np.zeros(f.shape, dtype=np.complex128)
    s21 = np.zeros(f.shape, dtype=np.complex128)
    n_lay = np.asarray(n_layers, dtype=np.complex128)
    d_lay = np.asarray(d_layers, dtype=np.float64)
    for i, fi in enumerate(f):
        k0 = 2.0 * np.pi * fi / C0
        kz0 = _kz(n0, k0, n0, theta0)
        kzs = _kz(ns, k0, n0, theta0)
        y0 = _admittance(n0, kz0, k0, pol)
        ys = _admittance(ns, kzs, k0, pol)
        m = np.eye(2, dtype=np.complex128)
        for n, d in zip(n_lay, d_lay):
            kz = _kz(n, k0, n0, theta0)
            y = _admittance(n, kz, k0, pol)
            delta = kz * d
            c, s = np.cos(delta), np.sin(delta)
            layer = np.array(
                [[c, 1j * s / (y + EPS)], [1j * y * s, c]],
                dtype=np.complex128,
            )
            m = m @ layer
        yin = (m[1, 0] + m[1, 1] * ys) / (m[0, 0] + m[0, 1] * ys + EPS)
        r = (y0 - yin) / (y0 + yin + EPS)
        t_e = (1.0 + r) / (m[0, 0] + m[0, 1] * ys + EPS)
        s11[i] = r
        scale = np.sqrt((np.real(ys) + 0j) / (np.real(y0) + EPS))
        s21[i] = t_e * scale
    return s11, s21


def tmm_field_vs_z(
    frequency_hz: float,
    z: np.ndarray,
    n_layers: list[complex],
    d_layers: list[float],
    n0: complex = 1.0,
    ns: complex = 1.0,
    theta0: float = 0.0,
    pol: str = "TE",
) -> np.ndarray:
    """Complex E_parallel(z). z = 0 is the first interface; incident from z < 0."""
    s11, _ = tmm_sparams(
        np.array([frequency_hz]), n_layers, d_layers, n0, ns, theta0, pol
    )
    r = s11[0]
    k0 = 2.0 * np.pi * frequency_hz / C0
    z = np.asarray(z, dtype=np.float64)
    kz0 = _kz(n0, k0, n0, theta0)
    kzs = _kz(ns, k0, n0, theta0)
    y0 = _admittance(n0, kz0, k0, pol)
    e = np.zeros(z.shape, dtype=np.complex128)
    inc = z < 0.0
    e[inc] = np.exp(-1j * kz0 * z[inc]) + r * np.exp(+1j * kz0 * z[inc])
    e_if = 1.0 + r
    h_if = y0 * (1.0 - r)
    z_lo = 0.0
    for n, d in zip(n_layers, d_layers):
        kz = _kz(n, k0, n0, theta0)
        y = _admittance(n, kz, k0, pol)
        a = 0.5 * (e_if + h_if / (y + EPS))
        b = 0.5 * (e_if - h_if / (y + EPS))
        z_hi = z_lo + d
        inside = (z >= z_lo) & (z < z_hi)
        dz = z[inside] - z_lo
        e[inside] = a * np.exp(-1j * kz * dz) + b * np.exp(+1j * kz * dz)
        e_if = a * np.exp(-1j * kz * d) + b * np.exp(+1j * kz * d)
        h_if = y * (a * np.exp(-1j * kz * d) - b * np.exp(+1j * kz * d))
        z_lo = z_hi
    ext = z >= z_lo
    e[ext] = e_if * np.exp(-1j * kzs * (z[ext] - z_lo))
    return e


def slab_field_grid(
    frequency_hz: float,
    x: np.ndarray,
    z: np.ndarray,
    n_slab: complex,
    thickness: float,
    n0: complex = 1.0,
    ns: complex = 1.0,
    theta0: float = 0.0,
    pol: str = "TE",
) -> np.ndarray:
    """E(x, z) for a single slab 0<z<thickness. Shape (nz, nx)."""
    xx, zz = np.meshgrid(x, z)
    u = tmm_field_vs_z(
        frequency_hz, zz.ravel(), [n_slab], [thickness], n0, ns, theta0, pol
    ).reshape(zz.shape)
    k0 = 2.0 * np.pi * frequency_hz / C0
    kx = k0 * n0 * np.sin(theta0)
    return u * np.exp(-1j * kx * xx)


def te10_sparams(
    frequencies_hz: np.ndarray, a: float, length: float, n: complex = 1.0
) -> tuple[np.ndarray, np.ndarray]:
    """Matched TE10 section. S11 = 0. S21 = exp(-j β L) or evanescent."""
    f = np.asarray(frequencies_hz, dtype=np.float64)
    fc = C0 / (2.0 * a * np.real(n) + EPS)
    s11 = np.zeros(f.shape, dtype=np.complex128)
    s21 = np.zeros(f.shape, dtype=np.complex128)
    for i, fi in enumerate(f):
        k = 2.0 * np.pi * fi * n / C0
        kc = np.pi / a
        disc = k**2 - kc**2
        if np.real(disc) >= 0 and np.real(fi) >= fc:
            beta = np.sqrt(disc)
            if np.imag(beta) > 0:
                beta = -beta
            s21[i] = np.exp(-1j * beta * length)
        else:
            gamma = np.sqrt(-disc)
            if np.real(gamma) < 0:
                gamma = -gamma
            s21[i] = np.exp(-gamma * length)
    return s11, s21


def te10_field(
    frequency_hz: float,
    x: np.ndarray,
    z: np.ndarray,
    a: float,
    length: float,
    n: complex = 1.0,
) -> np.ndarray:
    """Ey(x, z) for a matched TE10 guide, 0<x<a. Shape (nz, nx)."""
    xx, zz = np.meshgrid(x, z)
    k = 2.0 * np.pi * frequency_hz * n / C0
    kc = np.pi / a
    disc = k**2 - kc**2
    if np.real(disc) >= 0:
        beta = np.sqrt(disc)
        if np.imag(beta) > 0:
            beta = -beta
        prop = np.exp(-1j * beta * zz)
    else:
        gamma = np.sqrt(-disc)
        if np.real(gamma) < 0:
            gamma = -gamma
        prop = np.exp(-gamma * zz)
    return np.sin(np.pi * xx / a) * prop
