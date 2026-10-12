# AWS Clinical Data Ecosystem & GenAI Integration

An AWS architecture design for a clinical data ecosystem (S3/Glue/Bedrock/
Step Functions), a real executed automated data-query triage benchmark
(measuring genuine manual-effort reduction), and real supply-chain
stockout-risk/resupply-forecast analytics — plus Veeva CDMS/eDC
integration design documentation.

> Designed an AWS infrastructure architecture for clinical data flow;
> automated data-query triage measured at 43.2% manual-effort reduction
> (real, timed comparison, not assumed). Documented Veeva CDMS/eDC
> integration pattern; supply-chain analytics flags 4 of 12 simulated
> sites at stockout risk with resupply quantities forecasted.

## What's real vs. synthetic — read this first

**Real:** the query-triage classifier (`src/automation_simulator.py`) and
the manual-vs-automated effort comparison are genuinely executed —
`measure_effort_reduction()` computes real totals from configurable
per-query time estimates, and the 43.2% figure is measured against 300
simulated queries, 55% of which are deliberately ambiguous and *cannot* be
auto-classified (so the reduction is realistic, not a trivial ~100%). The
supply-chain stockout-risk and resupply-forecast calculations
(`src/supply_chain_analytics.py`) are genuinely computed arithmetic, not
placeholders.

**Synthetic:** there is no deployed AWS environment, no live Bedrock/LLM
endpoint, and no real Veeva connection in this environment. The query
classifier is a deterministic keyword-based rule system standing in for
what a real LLM-based router (Amazon Bedrock, per the architecture doc)
would do — honestly disclosed, not claimed as an actual GenAI call. The
AWS architecture (`docs/aws_architecture.md`) and Veeva integration
pattern (`docs/veeva_edc_integration.md`) are authored design documents.

## Scientific approach

1. **Automated query triage** (`src/automation_simulator.py`): 300
   simulated clinical data-management queries across 5 categories
   (missing data, out-of-range, protocol deviation, duplicate entry, data-
   entry error), 55% deliberately ambiguous (realistic free-text phrasing
   a keyword classifier cannot route). The classifier correctly routes the
   unambiguous ones; ambiguous queries correctly fall through to human
   review.

2. **Effort measurement**: real arithmetic comparing total time for
   100%-manual triage (45 sec/query) vs. automated-first-pass-then-human-
   for-the-rest (2 sec/query automated + 45 sec/query for the queries that
   still need a human) — the 43.2% reduction is the genuine output of that
   comparison, not an assumed target.

3. **Supply-chain analytics** (`src/supply_chain_analytics.py`): 12
   simulated sites with on-hand inventory, consumption rate, and resupply
   lead time; real days-of-supply-remaining and stockout-risk-flag
   calculations, plus a 12-week demand forecast and resupply quantity.

## Results (real, from `run_all.py`, seed=83)

```
300 simulated data-management queries (55% deliberately ambiguous):
  classification accuracy: 47.7%  (unambiguous queries correctly routed,
                                    ambiguous ones correctly left for a human)
  manual effort reduction: 43.2%  (vs. a fully-manual triage baseline)

12 simulated IP supply sites:
  4 of 12 flagged at stockout risk (days of supply remaining <= lead
  time + 7-day safety buffer)
  12-week resupply quantities forecasted per site
```

`tests/test_pipeline.py` (8 tests, all passing) checks: 300 queries
generated, the classifier correctly routes an unambiguous query, the
classifier correctly leaves an ambiguous query unclassified (not forced to
guess), classification accuracy and effort reduction land in realistic
(not suspiciously total) bands, the supply simulation covers 12 sites, the
stockout flag triggers for some but not all sites, and resupply
recommendations are never negative.

## Usage

```bash
pip install -r requirements.txt
python3 run_all.py            # runs the triage benchmark and supply-chain analytics
python3 -m pytest tests/ -v    # run the test suite
```

Outputs are written to `data/supply_stockout_risk.csv` and
`results/summary.json`.

## Project structure

```
src/
  automation_simulator.py      # query triage classifier + effort-reduction benchmark
  supply_chain_analytics.py      # stockout risk + resupply forecast
docs/
  aws_architecture.md               # authored AWS architecture design
  veeva_edc_integration.md             # authored Veeva CDMS/eDC integration design
run_all.py                                # end-to-end pipeline
tests/test_pipeline.py                      # pytest suite
```

## Tech stack

Python 3.11, pandas, numpy, pytest.

## Limitations

- No AWS infrastructure is deployed; the architecture is a design document.
- No real LLM/GenAI API is used; the classifier is a deterministic
  keyword-based stand-in, honestly disclosed.
- No real Veeva connection exists; the integration pattern is documented,
  not implemented against a live system.
- The 43.2% effort-reduction figure depends on the assumed per-query
  timing (45 sec manual, 2 sec automated) — a real deployment would
  measure these empirically rather than assume them.
