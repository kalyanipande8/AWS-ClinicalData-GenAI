"""Clinical trial supply-chain analytics: simulated investigational
product (IP) inventory across sites, with real stockout-risk and
resupply-forecast calculations -- the analytics layer the AWS architecture
(docs/aws_architecture.md) is designed to support in real time."""
from __future__ import annotations

import numpy as np
import pandas as pd

N_SITES = 12
SEED = 83


def simulate_supply_data(n_sites: int = N_SITES, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_sites):
        on_hand = int(rng.integers(5, 80))
        weekly_consumption = round(float(rng.uniform(1.5, 12.0)), 1)
        lead_time_days = int(rng.integers(7, 28))
        rows.append({
            "site_id": f"SITE-{i+1:03d}", "units_on_hand": on_hand,
            "mean_weekly_consumption": weekly_consumption, "resupply_lead_time_days": lead_time_days,
        })
    return pd.DataFrame(rows)


def compute_stockout_risk(df: pd.DataFrame, safety_buffer_days: int = 7) -> pd.DataFrame:
    out = df.copy()
    daily_consumption = out["mean_weekly_consumption"] / 7
    out["days_of_supply_remaining"] = (out["units_on_hand"] / daily_consumption).round(1)
    out["reorder_threshold_days"] = out["resupply_lead_time_days"] + safety_buffer_days
    out["stockout_risk_flag"] = out["days_of_supply_remaining"] <= out["reorder_threshold_days"]
    return out


def forecast_resupply_quantity(df: pd.DataFrame, forecast_weeks: int = 12) -> pd.DataFrame:
    out = df.copy()
    out["forecasted_demand_units"] = (out["mean_weekly_consumption"] * forecast_weeks).round(0)
    out["recommended_resupply_units"] = (out["forecasted_demand_units"] - out["units_on_hand"]).clip(lower=0)
    return out


if __name__ == "__main__":
    df = simulate_supply_data()
    risk = compute_stockout_risk(df)
    print(risk)
    print(f"\n{risk['stockout_risk_flag'].sum()} of {len(risk)} sites at stockout risk")
    forecast = forecast_resupply_quantity(df)
    print(forecast[["site_id", "forecasted_demand_units", "recommended_resupply_units"]])
