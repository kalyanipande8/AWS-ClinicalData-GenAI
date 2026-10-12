# Veeva CDMS & eDC Integration — Design Documentation

**Status: an authored integration design, not a live connection to a real
Veeva instance — no Veeva account/API access is available in this
environment.**

## Integration pattern
Veeva CDMS/Vault exposes a REST API (and SFTP-based bulk export) for
clinical data extracts. The intended integration:

1. **Scheduled extract**: a nightly API pull (or SFTP bulk export) of new/
   changed EDC records, landing in the S3 raw zone (see
   `docs/aws_architecture.md`).
2. **Query/data-management-task sync**: Veeva's query/task objects (the
   real-world analog of `src/automation_simulator.py`'s simulated data
   queries) would be pulled via the same API, triaged by the automation
   layer, and routed back to Veeva as an updated query status/assignment
   via its write API.
3. **Supply module integration**: Veeva's Clinical Supply Management
   module exposes site-level inventory data, which `src/
   supply_chain_analytics.py`'s stockout-risk and resupply-forecast logic
   would consume in place of the simulated `simulate_supply_data()`.

## Honest disclosure
No real Veeva connection exists in this environment. This document
describes the integration pattern a real deployment would follow; the
executable code in this repository operates on simulated data standing in
for what a live Veeva API would provide.
