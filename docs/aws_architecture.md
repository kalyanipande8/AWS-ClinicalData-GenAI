# AWS Clinical Data Ecosystem — Architecture Design

**Status: an authored architecture design, not a deployed AWS environment
— no AWS account/infrastructure is provisioned in this environment.**

## Target architecture
```
Veeva CDMS / eDC  --(API/SFTP)-->  S3 (raw landing zone)
                                        |
                                   AWS Glue (ETL: raw -> curated Parquet)
                                        |
                           Amazon S3 (curated) + AWS Lake Formation (access control)
                                        |
                +-----------------------+------------------------+
                |                                                |
     Amazon Bedrock (GenAI query triage,          Amazon Athena / Redshift Spectrum
     per src/automation_simulator.py's                 (ad hoc + BI analytics,
     classification logic, scaled to an                supply-chain dashboards per
     LLM-based router in production)                   src/supply_chain_analytics.py)
                |                                                |
        Step Functions (orchestrates triage -> routing -> notification)
                |
         Amazon SNS / SES (routes flagged queries to the right data-management team)
```

## Why this shape
- **S3 + Glue + Lake Formation** is the standard AWS pattern for a
  governed, access-controlled clinical data lake — raw and curated zones
  kept separate so curated (analysis-ready) data never mixes with
  unvalidated raw ingests.
- **Bedrock** (or an equivalent managed LLM endpoint) is where the real
  production version of `src/automation_simulator.py`'s rule-based
  classifier would be replaced by an actual LLM call — this repository's
  classifier is a deterministic keyword-based stand-in, honestly
  disclosed, since no LLM API is available in this environment.
- **Step Functions** orchestrates the triage → human-review-routing
  workflow as a real state machine, rather than ad hoc scripts.

## Honest disclosure
No part of this architecture is deployed; there is no AWS account, no
provisioned S3 bucket, and no live Bedrock endpoint in this environment.
The executable code in `src/` (query triage, supply-chain analytics)
demonstrates the actual analytical logic this architecture would host, run
locally on simulated data.
