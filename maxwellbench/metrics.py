"""Metric formulas. If docs/METRICS.md disagrees, this file wins."""

from __future__ import annotations

import numpy as np

EPS = 1e-12


def mag_db(s: np.ndarray) -> np.ndarray:
    return 20.0 * np.log10(np.abs(s) + EPS)


def s_wmae_db(
    pred: np.ndarray,
    gt: np.ndarray,
    weights: np.ndarray | None = None,
) -> float:
    """Magnitude-weighted MAE in dB. pred, gt: complex, same shape (..., F)."""
    err = np.abs(mag_db(pred) - mag_db(gt))
    if weights is None:
        return float(np.mean(err))
    w = np.asarray(weights, dtype=np.float64)
    return float(np.sum(w * err) / (np.sum(w) + EPS))


def s_phase_mae_deg(pred: np.ndarray, gt: np.ndarray) -> float:
    d = np.angle(pred * np.conjugate(gt))
    return float(np.mean(np.abs(np.degrees(d))))


def s_complex_rmse(pred: np.ndarray, gt: np.ndarray) -> float:
    d = pred - gt
    return float(np.sqrt(np.mean(np.real(d * np.conjugate(d)))))


def field_nrmse(pred: np.ndarray, gt: np.ndarray) -> float:
    """Relative L2 on a field array. Last axis may be vector components."""
    num = np.linalg.norm(pred - gt)
    den = np.linalg.norm(gt) + EPS
    return float(num / den)


def align_global_phase(pred: np.ndarray, gt: np.ndarray) -> np.ndarray:
    """Multiply pred by a unit complex so <pred, gt> is real and positive."""
    p = np.asarray(pred)
    g = np.asarray(gt)
    ip = np.vdot(p, g)
    if np.abs(ip) < EPS:
        return p
    return p * (ip / np.abs(ip))


def field_nrmse_aligned(pred: np.ndarray, gt: np.ndarray) -> float:
    """nRMSE after a single global phase. Source phase is not a degree of freedom we score."""
    return field_nrmse(align_global_phase(pred, gt), gt)


def area_over_random(err_method: np.ndarray, err_rand: np.ndarray, b: np.ndarray) -> float:
    """Mean(e_rand - e_method) along solver-call axis b."""
    if err_method.shape != err_rand.shape or err_method.shape != b.shape:
        raise ValueError("curve shapes must match")
    integ = getattr(np, "trapezoid", np.trapz)
    return float(integ(err_rand - err_method, b) / (b[-1] - b[0] + EPS))
