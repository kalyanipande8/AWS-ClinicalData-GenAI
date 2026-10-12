import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from src.automation_simulator import simulate_queries, run_automated_triage, measure_effort_reduction, classify_query
from src.supply_chain_analytics import simulate_supply_data, compute_stockout_risk, forecast_resupply_quantity


@pytest.fixture(scope="module")
def queries():
    return simulate_queries()


def test_300_queries_generated(queries):
    assert len(queries) == 300


def test_classifier_correctly_routes_an_unambiguous_query():
    assert classify_query("Subject S0001: HbA1c value missing for visit 3") == "missing_data"


def test_classifier_leaves_ambiguous_queries_unclassified():
    assert classify_query("Subject S0001: something looks off, please check") is None


def test_triage_accuracy_in_realistic_band(queries):
    result = run_automated_triage(queries)
    assert 0.3 <= result["classification_accuracy_pct"] / 100 <= 0.95


def test_effort_reduction_is_positive_but_not_total(queries):
    """A real automation benefit should show up, but shouldn't eliminate
    human review entirely -- ambiguous queries genuinely need a person."""
    result = measure_effort_reduction(queries)
    assert 0 < result["manual_effort_reduction_pct"] < 100
    assert result["n_needing_human_review"] > 0


def test_supply_simulation_has_12_sites():
    df = simulate_supply_data()
    assert len(df) == 12


def test_stockout_risk_flags_some_but_not_all_sites():
    df = simulate_supply_data()
    risk = compute_stockout_risk(df)
    assert 0 < risk["stockout_risk_flag"].sum() < len(risk)


def test_resupply_forecast_never_negative():
    df = simulate_supply_data()
    forecast = forecast_resupply_quantity(df)
    assert (forecast["recommended_resupply_units"] >= 0).all()
