"""The statistics decide what the report claims, so they get their own known-answer tests."""

import importlib.util
import sys
from pathlib import Path

import pytest

EVAL = Path(__file__).parents[1] / "eval"
sys.path.insert(0, str(EVAL))
spec = importlib.util.spec_from_file_location("score_gold", EVAL / "score_gold.py")
score = importlib.util.module_from_spec(spec)
spec.loader.exec_module(score)


def test_weights_undo_oversampling():
    # 1 in 10 lines disagree in the population, though half the sample is from them
    meta = {
        "repos": {
            "r": {
                "lines": 100,
                "strata": {"agree": {"population": 90}, "disagree": {"population": 10}},
            }
        }
    }
    weights = score.stratum_weights(meta)
    rows = [
        {"repo": "r", "stratum": "agree", "m": True},
        {"repo": "r", "stratum": "disagree", "m": False},
    ]
    assert score.weighted_accuracy(rows, "m", weights) == pytest.approx(0.9)


def test_mcnemar_exact_known_value():
    # 8 wins against 0: two-sided p = 2 * (1 / 256)
    rows = [{"a": False, "b": True}] * 8
    assert score.mcnemar_exact(rows, "a", "b")["p"] == pytest.approx(2 / 256)


def test_mcnemar_no_difference():
    rows = [{"a": True, "b": True}] * 5
    assert score.mcnemar_exact(rows, "a", "b")["p"] == 1.0


def test_kappa():
    assert score.cohen_kappa(["a", "b"], ["a", "b"]) == 1.0
    assert score.cohen_kappa(["a", "a", "b", "b"], ["a", "b", "a", "b"]) == 0.0


def test_commit_matching_needs_enough_characters():
    full = "9c19aff7c7561e3a82978a272ecdaad40dda5c00"
    assert score.same_commit(full, "9c19aff")
    assert not score.same_commit(full, "9c1")
    assert not score.same_commit(full, "")
