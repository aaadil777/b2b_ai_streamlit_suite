import numpy as np
import pandas as pd

def minmax(x):
    return (x - x.min()) / (x.max() - x.min() + 1e-9)

def supplier_scores(df, w):
    df = df.copy()
    for c in ["otd_rate","cost_variance","quality_ppm","risk_events_12m"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["otd_rate"] = df["otd_rate"].clip(0,1)

    score = (
        w["otd"]*minmax(df["otd_rate"]) +
        w["cost"]*minmax(-df["cost_variance"]) +
        w["qual"]*minmax(-np.log1p(df["quality_ppm"])) +
        w["risk"]*minmax(-df["risk_events_12m"])
    ).round(4)

    df["score"] = score
    return df.sort_values("score", ascending=False)

def moving_average_forecast(ts, window, horizon):
    ma = ts.rolling(window, min_periods=1).mean()
    last_val = float(ma.iloc[-1]) if len(ma) else 0.0
    future_idx = pd.date_range(ts.index.max()+pd.Timedelta(days=1), periods=horizon, freq="D")
    future = pd.Series([last_val]*horizon, index=future_idx, name="forecast")
    return ma, future
