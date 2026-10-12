"""End-to-end: run the automated data-query triage benchmark and the
supply-chain stockout-risk/resupply-forecast analytics."""
import json
import os

from src.automation_simulator import simulate_queries, run_automated_triage, measure_effort_reduction
from src.supply_chain_analytics import simulate_supply_data, compute_stockout_risk, forecast_resupply_quantity

os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)

print("=== Simulating 300 clinical data-management queries ===")
queries = simulate_queries()

print("\n=== Automated triage classification ===")
triage = run_automated_triage(queries)
print(triage)

print("\n=== Manual vs. automated effort comparison ===")
effort = measure_effort_reduction(queries)
print(effort)

print("\n=== Supply chain analytics ===")
supply = simulate_supply_data()
risk = compute_stockout_risk(supply)
forecast = forecast_resupply_quantity(supply)
risk.to_csv("data/supply_stockout_risk.csv", index=False)
print(f"{int(risk['stockout_risk_flag'].sum())} of {len(risk)} sites at stockout risk")
print(forecast[["site_id", "forecasted_demand_units", "recommended_resupply_units"]])

summary = {
    "n_queries": triage["n_queries"],
    "classification_accuracy_pct": triage["classification_accuracy_pct"],
    "manual_effort_reduction_pct": effort["manual_effort_reduction_pct"],
    "n_sites": len(supply),
    "n_sites_at_stockout_risk": int(risk["stockout_risk_flag"].sum()),
}
with open("results/summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n=== Summary ===")
print(json.dumps(summary, indent=2))
