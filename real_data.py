from pathlib import Path
import re
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "data.xlsx"

ALIASES = {
    "duration_min": ["durmin", "duration_min", "durationminutes", "actual_wait_min"],
    "duration_seconds": ["duration", "duration_seconds", "durationsec"],
    "order_time": ["ordertime", "order_time", "order time"],
    "delivery_time": ["servicetime", "service_time", "deliverytime", "delivery_time"],
    "perceived_duration": ["perception_duration", "perceived_duration"],
    "time_satisfaction": ["time_satisfactiongeneral", "time_satisfaction_general"],
    "satisfaction1": ["satisfaction1"],
    "satisfaction2": ["satisfaction2"],
    "satisfaction3": ["satisfaction3"],
    "satisfaction4": ["satisfaction4"],
    "time_satisfaction1": ["time_satisfaction1"],
    "time_satisfaction2": ["time_satisfaction2"],
    "time_satisfaction3": ["time_satisfaction3"],
    "time_satisfaction4": ["time_satisfaction4"],
}

def norm(s):
    return re.sub(r"[^a-z0-9]", "", str(s).strip().lower())

def load_workbook(path=DATA_PATH):
    if not path.exists():
        raise FileNotFoundError(
            f"Real dataset workbook not found: {path}\n"
            "Download it from https://data.mendeley.com/datasets/79zt3t734g/1 "
            "and place data.xlsx inside the project's data folder."
        )
    xls = pd.ExcelFile(path)
    candidates = []
    for sheet in xls.sheet_names:
        df = pd.read_excel(path, sheet_name=sheet)
        if len(df.columns):
            candidates.append((sheet, df))
    if not candidates:
        raise ValueError("The workbook contains no readable sheets.")
    # Prefer sheet containing duration-like fields.
    chosen = None
    for sheet, df in candidates:
        cols = {norm(c) for c in df.columns}
        if any(norm(a) in cols for a in ALIASES["duration_min"] + ALIASES["duration_seconds"]):
            chosen = (sheet, df)
            break
    if chosen is None:
        print("Available sheets and columns:")
        for sheet, df in candidates:
            print(f"- {sheet}: {list(df.columns)}")
        raise ValueError("Could not identify a duration column. See printed columns and update ALIASES.")
    sheet, df = chosen
    return sheet, df

def find_column(df, alias_list):
    by_norm = {norm(c): c for c in df.columns}
    for alias in alias_list:
        if norm(alias) in by_norm:
            return by_norm[norm(alias)]
    return None

def prepare_data(df):
    out = df.copy()
    # Prefer explicit minutes field. Otherwise duration is treated as seconds,
    # matching the dataset description; validate against observed values.
    cmin = find_column(out, ALIASES["duration_min"])
    csec = find_column(out, ALIASES["duration_seconds"])
    if cmin is not None and norm(cmin) in [norm(x) for x in ALIASES["duration_min"]]:
        out["actual_duration_min"] = pd.to_numeric(out[cmin], errors="coerce")
        source = f"{cmin} (minutes)"
    elif csec is not None:
        out["actual_duration_min"] = pd.to_numeric(out[csec], errors="coerce") / 60.0
        source = f"{csec} (converted from seconds to minutes)"
    else:
        raise ValueError(f"No recognized duration column. Columns found: {list(out.columns)}")
    # Canonical convenience fields, if present.
    for target in ["order_time", "delivery_time", "perceived_duration", "time_satisfaction",
                   "satisfaction1", "satisfaction2", "satisfaction3", "satisfaction4"]:
        col = find_column(out, ALIASES.get(target, []))
        if col is not None:
            out[target] = out[col]
    out["actual_duration_min"] = out["actual_duration_min"].replace([np.inf, -np.inf], np.nan)
    # Keep zero/negative values for quality reporting; exclude them only in duration analysis.
    return out, source

def data_quality(df):
    return pd.DataFrame({
        "check": ["Rows", "Columns", "Duplicate rows", "Missing cells", "Missing duration",
                  "Non-positive duration", "Negative duration"],
        "value": [
            len(df), len(df.columns), int(df.duplicated().sum()), int(df.isna().sum().sum()),
            int(df["actual_duration_min"].isna().sum()),
            int((df["actual_duration_min"].dropna() <= 0).sum()),
            int((df["actual_duration_min"].dropna() < 0).sum())
        ]
    })

def duration_summary(df):
    x = df["actual_duration_min"].dropna()
    x = x[x > 0]
    if x.empty:
        raise ValueError("No positive, non-missing duration values are available.")
    return pd.DataFrame([{
        "n_valid": int(x.size),
        "mean_min": x.mean(),
        "median_min": x.median(),
        "std_min": x.std(ddof=1),
        "p90_min": x.quantile(.90),
        "p95_min": x.quantile(.95),
        "min_min": x.min(),
        "max_min": x.max()
    }])

def duration_sensitivity(df, increases=(0, .05, .10, .15)):
    x = df["actual_duration_min"].dropna()
    x = x[x > 0]
    rows = []
    for bump in increases:
        y = x * (1 + bump)
        rows.append({
            "scenario": f"Duration +{bump:.0%}",
            "multiplier": 1 + bump,
            "n": len(y),
            "mean_duration_min": y.mean(),
            "median_duration_min": y.median(),
            "p95_duration_min": y.quantile(.95),
            "share_over_15min": (y > 15).mean(),
            "share_over_20min": (y > 20).mean(),
        })
    return pd.DataFrame(rows)

def correlation_summary(df):
    pairs = []
    if "perceived_duration" in df.columns:
        a = pd.to_numeric(df["perceived_duration"], errors="coerce")
        b = df["actual_duration_min"]
        z = pd.concat([a, b], axis=1).dropna()
        if len(z) >= 3:
            pairs.append({"relationship": "Perceived duration vs actual order-to-delivery duration",
                          "n": len(z), "pearson_r": z.iloc[:,0].corr(z.iloc[:,1])})
    if "time_satisfaction" in df.columns:
        a = pd.to_numeric(df["time_satisfaction"], errors="coerce")
        b = df["actual_duration_min"]
        z = pd.concat([a, b], axis=1).dropna()
        if len(z) >= 3:
            pairs.append({"relationship": "Time satisfaction vs actual order-to-delivery duration",
                          "n": len(z), "pearson_r": z.iloc[:,0].corr(z.iloc[:,1])})
    return pd.DataFrame(pairs, columns=["relationship", "n", "pearson_r"])

def theoretical_capacity_experiment(df, counters=(1, 2, 3, 4, 5), repetitions=300, seed=42):
    """Explicitly illustrative queue what-if using system duration as a proxy.

    The observed order-to-delivery duration is NOT a measured service time.
    This is therefore a sensitivity demonstration, not a validated model.
    Arrivals are estimated from order timestamps only if parseable and enough rows exist;
    otherwise an illustrative rate is used and the result is marked.
    """
    from simulation_core import simulate_mm_s
    x = df["actual_duration_min"].dropna()
    x = x[x > 0]
    proxy_mean = float(x.mean())
    arrival_col = df.get("order_time")
    arrival_rate = None
    arrival_source = "fallback illustrative arrival rate (0.05 customers/min)"
    if arrival_col is not None:
        parsed = pd.to_datetime(arrival_col, errors="coerce")
        parsed = parsed.dropna().sort_values()
        if len(parsed) >= 3:
            gaps = parsed.diff().dt.total_seconds().dropna() / 60
            gaps = gaps[gaps > 0]
            if len(gaps):
                arrival_rate = float(1 / gaps.mean())
                arrival_source = "estimated from observed order-time gaps"
    if arrival_rate is None or not np.isfinite(arrival_rate) or arrival_rate <= 0:
        arrival_rate = 0.05
    rows = []
    for s in counters:
        vals = []
        for i in range(repetitions):
            waits = simulate_mm_s(
                n_customers=max(100, len(x)), arrival_rate=arrival_rate,
                proxy_service_mean=proxy_mean, counters=s, seed=seed + s*10000 + i
            )
            vals.append([waits.mean(), np.quantile(waits, .95), (waits > 5).mean()])
        a = np.asarray(vals)
        rows.append({
            "counters_assumed": s, "arrival_rate_per_min": arrival_rate,
            "proxy_mean_system_duration_min": proxy_mean,
            "arrival_rate_basis": arrival_source,
            "mean_queue_wait_min": a[:,0].mean(),
            "p95_queue_wait_min": np.quantile(a[:,1], .5),
            "prob_wait_over_5min": a[:,2].mean(),
            "repetitions": repetitions,
            "warning": "COUNTERFACTUAL ONLY: system duration used as service-time proxy"
        })
    return pd.DataFrame(rows)
