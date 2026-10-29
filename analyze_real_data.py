from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
from real_data import load_workbook, prepare_data, data_quality, duration_summary, duration_sensitivity, correlation_summary, theoretical_capacity_experiment

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs"
OUT.mkdir(exist_ok=True)

def main():
    sheet, raw = load_workbook()
    df, duration_source = prepare_data(raw)
    print(f"Loaded sheet: {sheet}")
    print(f"Rows: {len(df)} | columns: {len(df.columns)}")
    print(f"Duration source: {duration_source}")
    print("Columns:", list(raw.columns))

    quality = data_quality(df)
    summary = duration_summary(df)
    sensitivity = duration_sensitivity(df)
    correlations = correlation_summary(df)
    capacity = theoretical_capacity_experiment(df)

    quality.to_csv(OUT / "data_quality.csv", index=False)
    summary.to_csv(OUT / "observed_duration_summary.csv", index=False)
    sensitivity.to_csv(OUT / "duration_sensitivity.csv", index=False)
    correlations.to_csv(OUT / "correlations.csv", index=False)
    capacity.to_csv(OUT / "counterfactual_capacity_scenarios.csv", index=False)
    df.to_csv(OUT / "cleaned_real_data.csv", index=False)

    valid = df["actual_duration_min"].dropna()
    valid = valid[valid > 0]
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(valid, bins=15, edgecolor="black")
    ax.set_xlabel("Observed order-to-delivery duration (minutes)")
    ax.set_ylabel("Respondent count")
    ax.set_title("Observed duration distribution (published dataset)")
    fig.tight_layout()
    fig.savefig(OUT / "observed_duration_distribution.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(sensitivity["scenario"], sensitivity["mean_duration_min"], marker="o", label="Mean")
    ax.plot(sensitivity["scenario"], sensitivity["p95_duration_min"], marker="o", label="95th percentile")
    ax.set_ylabel("Order-to-delivery duration (minutes)")
    ax.set_title("Sensitivity of observed durations to hypothetical increases")
    ax.legend()
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    fig.savefig(OUT / "duration_sensitivity.png", dpi=180)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(capacity["counters_assumed"], capacity["mean_queue_wait_min"], marker="o")
    ax.set_xlabel("Assumed number of counters")
    ax.set_ylabel("Simulated queue wait (minutes)")
    ax.set_title("Counterfactual capacity model (not validated)")
    fig.tight_layout()
    fig.savefig(OUT / "counterfactual_capacity.png", dpi=180)
    plt.close(fig)

    print("\nDATA QUALITY\n", quality.to_string(index=False))
    print("\nOBSERVED DURATION SUMMARY\n", summary.round(3).to_string(index=False))
    print("\nDURATION SENSITIVITY\n", sensitivity.round(3).to_string(index=False))
    if not correlations.empty:
        print("\nCORRELATIONS\n", correlations.round(3).to_string(index=False))
    print("\nCOUNTERFACTUAL CAPACITY SCENARIOS\n", capacity.round(3).to_string(index=False))
    print(f"\nOutputs saved to: {OUT}")
    print("\nInterpretation: duration is order-to-delivery system time, not pure queue waiting or measured service time.")

if __name__ == "__main__":
    main()
