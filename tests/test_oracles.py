import numpy as np

from maxwellbench.oracles import C0, te10_sparams, tmm_field_vs_z, tmm_sparams


def test_fresnel_normal_interface():
    n0, ns = 1.0, 1.5
    s11, s21 = tmm_sparams(np.array([3e8 / 1e-6]), [], [], n0=n0, ns=ns)
    r = (n0 - ns) / (n0 + ns)
    assert abs(s11[0] - r) < 1e-10
    assert abs(abs(s11[0]) ** 2 + abs(s21[0]) ** 2 - 1.0) < 1e-8


def test_quarter_wave_ar_low_reflection():
    n0, ns = 1.0, 1.5
    n1 = np.sqrt(n0 * ns)
    lam = 550e-9
    d = lam / (4.0 * n1)
    f = C0 / lam
    s11, s21 = tmm_sparams(np.array([f]), [n1], [d], n0=n0, ns=ns)
    assert abs(s11[0]) < 1e-6
    assert abs(abs(s21[0]) - 1.0) < 1e-6


def test_field_incident_side_matches_s11():
    n0, ns = 1.0, 2.0
    f = 1e9
    z = np.array([-0.1])
    e = tmm_field_vs_z(f, z, [], [], n0=n0, ns=ns)
    s11, _ = tmm_sparams(np.array([f]), [], [], n0=n0, ns=ns)
    k0 = 2 * np.pi * f / C0
    expect = np.exp(-1j * k0 * n0 * z[0]) + s11[0] * np.exp(+1j * k0 * n0 * z[0])
    assert abs(e[0] - expect) < 1e-10


def test_te10_above_cutoff_is_all_pass():
    a = 0.02286
    fc = C0 / (2 * a)
    f = np.array([1.5 * fc])
    s11, s21 = te10_sparams(f, a, 0.1)
    assert abs(s11[0]) < 1e-15
    assert abs(abs(s21[0]) - 1.0) < 1e-12


def test_te10_below_cutoff_decays():
    a = 0.02286
    fc = C0 / (2 * a)
    f = np.array([0.5 * fc])
    _, s21 = te10_sparams(f, a, 0.1)
    assert abs(s21[0]) < 1e-3
