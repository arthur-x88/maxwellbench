import numpy as np

from maxwellbench.metrics import field_nrmse, s_wmae_db
from maxwellbench.tasks import all_tasks, bench_config


def test_perfect_s_is_zero():
    s = np.array([0.1 + 0.2j, 0.3 - 0.1j])
    assert s_wmae_db(s, s) < 1e-12


def test_field_nrmse_zero():
    e = np.ones((4, 4, 3))
    assert field_nrmse(e, e) < 1e-12


def test_bench_loads_eight_tasks():
    ids = [t.id for t in all_tasks()]
    assert bench_config()["version"] == "0.2.0"
    assert len(ids) == 8
    assert "pho.metalens" in ids and "brd.coupon" in ids
