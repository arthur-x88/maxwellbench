from maxwellbench.evaluate import evaluate
from maxwellbench.exam import load_exam


def test_exam_has_fifteen_items():
    items = load_exam()
    assert len(items) == 15
    ids = [i["id"] for i in items]
    assert len(set(ids)) == 15


def test_perfect_prediction_is_zero():
    from maxwellbench.exam import ground_truth, load_exam
    from maxwellbench.evaluate import score_item

    item = load_exam(["photonic"])[0]
    row = score_item(item, ground_truth(item))
    assert row["s_wmae_db"] < 1e-10
    assert row["e_nrmse_aligned"] < 1e-10


def test_incident_baseline_runs():
    result = evaluate(baseline="incident")
    assert result["summary"]["n_scored"] == 15
    assert result["summary"]["e_nrmse_aligned_mean"] > 0.0
