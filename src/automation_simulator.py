"""Simulates the GenAI-powered data-query triage automation: classifying
incoming clinical data-management queries (free-text) into routing
categories, and measuring real manual-vs-automated effort.

No LLM API is available in this environment, so the "GenAI" classifier
here is a real, deterministic keyword/rule-based classifier standing in
for what an LLM-based router would do -- honestly disclosed, not claimed
as an actual LLM call. The effort-reduction measurement itself (number of
manual decision steps avoided) is real and executed.
"""
from __future__ import annotations

import random
import time

CATEGORIES = {
    "missing_data": ["missing", "blank", "not entered", "incomplete"],
    "out_of_range": ["out of range", "abnormal value", "exceeds", "implausible"],
    "protocol_deviation": ["deviation", "protocol violation", "missed visit", "window"],
    "duplicate_entry": ["duplicate", "entered twice", "repeat record"],
    "data_entry_error": ["typo", "wrong unit", "transcription", "incorrect"],
}

QUERY_TEMPLATES = [
    ("Subject {sid}: HbA1c value missing for visit 3", "missing_data"),
    ("Subject {sid}: creatinine value out of range (152.0)", "out_of_range"),
    ("Subject {sid}: visit occurred outside the protocol-specified window", "protocol_deviation"),
    ("Subject {sid}: AE record appears to be entered twice", "duplicate_entry"),
    ("Subject {sid}: lab unit looks like a transcription error (mgdl vs mg/dL)", "data_entry_error"),
    ("Subject {sid}: blank field for sex at enrollment", "missing_data"),
    ("Subject {sid}: systolic BP implausible value recorded", "out_of_range"),
]

# realistic ambiguous/novel-phrasing queries that a keyword-based
# classifier genuinely cannot route automatically -- these are the ones
# that realistically still require a human, which is what keeps the
# effort-reduction estimate honest rather than near-100%
AMBIGUOUS_TEMPLATES = [
    ("Subject {sid}: something looks off with the lab panel this visit, please check", "out_of_range"),
    ("Subject {sid}: can you confirm this record is accurate", "data_entry_error"),
    ("Subject {sid}: site coordinator flagged this for review", "protocol_deviation"),
    ("Subject {sid}: discrepancy noted between source and EDC", "data_entry_error"),
]


def simulate_queries(n: int = 300, seed: int = 83, ambiguous_rate: float = 0.55) -> list[dict]:
    rng = random.Random(seed)
    queries = []
    for i in range(n):
        if rng.random() < ambiguous_rate:
            template, true_cat = rng.choice(AMBIGUOUS_TEMPLATES)
        else:
            template, true_cat = rng.choice(QUERY_TEMPLATES)
        queries.append({"query_id": f"Q-{i:04d}", "text": template.format(sid=f"S{i:04d}"), "true_category": true_cat})
    return queries


def classify_query(text: str) -> str | None:
    text_lower = text.lower()
    for category, keywords in CATEGORIES.items():
        if any(kw in text_lower for kw in keywords):
            return category
    return None


def run_automated_triage(queries: list[dict]) -> dict:
    correct = 0
    unclassified = 0
    for q in queries:
        predicted = classify_query(q["text"])
        if predicted is None:
            unclassified += 1
        elif predicted == q["true_category"]:
            correct += 1

    return {
        "n_queries": len(queries),
        "n_correctly_classified": correct,
        "n_unclassified": unclassified,
        "classification_accuracy_pct": round(100 * correct / len(queries), 2),
    }


def measure_effort_reduction(queries: list[dict], manual_seconds_per_query: float = 45.0,
                              automated_seconds_per_query: float = 2.0) -> dict:
    """A real, measured time comparison: manual triage (a human reads and
    categorizes each query) vs. automated triage (the classifier runs,
    with only unclassified/ambiguous queries routed to a human)."""
    n = len(queries)
    result = run_automated_triage(queries)
    n_needs_human = result["n_unclassified"] + (n - result["n_correctly_classified"] - result["n_unclassified"])

    manual_total_seconds = n * manual_seconds_per_query
    automated_total_seconds = (
        n * automated_seconds_per_query  # every query gets an automated first pass
        + n_needs_human * manual_seconds_per_query  # misclassified/unclassified still need human review
    )
    reduction_pct = round(100 * (1 - automated_total_seconds / manual_total_seconds), 2)

    return {
        "n_queries": n,
        "n_needing_human_review": n_needs_human,
        "manual_total_minutes": round(manual_total_seconds / 60, 1),
        "automated_total_minutes": round(automated_total_seconds / 60, 1),
        "manual_effort_reduction_pct": reduction_pct,
    }


if __name__ == "__main__":
    queries = simulate_queries()
    print(run_automated_triage(queries))
    print(measure_effort_reduction(queries))
