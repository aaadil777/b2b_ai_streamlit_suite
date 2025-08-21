import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="B2B AI Mini", layout="wide")

st.title("B2B AI Mini — Supplier Scorecard & Quick Forecast")
st.caption("Upload CSVs • Score Suppliers • Forecast Demand (moving average)")

# --- Uploads ---
col1, col2 = st.columns(2)
with col1:
    sup_file = st.file_uploader("Upload suppliers.csv", type=["csv"], key="sup")
with col2:
    dem_file = st.file_uploader("Upload demand.csv", type=["csv"], key="dem")

# Load data
df_sup, df_dem = None, None
if sup_file:
    df_sup = pd.read_csv(sup_file)
if dem_file:
    df_dem = pd.read_csv(dem_file)

st.markdown("---")
st.header("1) Supplier Scorecard")

if df_sup is None:
    st.info("Upload suppliers.csv with columns: supplier_id, name, otd_rate, cost_variance, quality_ppm, risk_events_12m")
else:
    with st.sidebar:
        st.header("Weights")
        w_otd = st.slider("On-time delivery", 0.0, 1.0, 0.4, 0.05)
        w_cost = st.slider("Cost variance", 0.0, 1.0, 0.2, 0.05)
        w_quality = st.slider("Quality (PPM)", 0.0, 1.0, 0.25, 0.05)
        w_risk = st.slider("Risk events", 0.0, 1.0, 0.15, 0.05)

    def mm(x): return (x - x.min()) / (x.max() - x.min() + 1e-9)

    df = df_sup.copy()
    # Safety: coerce numeric cols
    for c in ["otd_rate","cost_variance","quality_ppm","risk_events_12m"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["otd_rate"] = df["otd_rate"].clip(0,1)

    df["score"] = (
        w_otd*mm(df["otd_rate"]) +
        w_cost*mm(-df["cost_variance"]) +
        w_quality*mm(-np.log1p(df["quality_ppm"])) +
        w_risk*mm(-df["risk_events_12m"])
    ).round(4)

    st.dataframe(df.sort_values("score", ascending=False), use_container_width=True)

    st.download_button(
        "Download Top 10 Suppliers",
        df.nlargest(10, "score").to_csv(index=False),
        file_name="top_suppliers.csv"
    )

st.markdown("---")
st.header("2) Quick Demand Forecast (Moving Average)")

if df_dem is None:
    st.info("Upload demand.csv with columns: date, sku, qty (YYYY-MM-DD)")
else:
    df_dem["date"] = pd.to_datetime(df_dem["date"], errors="coerce")
    df_dem = df_dem.dropna(subset=["date"])
    df_dem["qty"] = pd.to_numeric(df_dem["qty"], errors="coerce").fillna(0)

    sku = st.selectbox("Choose SKU", sorted(df_dem["sku"].astype(str).unique()))
    window = st.slider("MA window (days)", 3, 30, 7)
    horizon = st.slider("Forecast horizon (days)", 7, 60, 14)

    ts = (
        df_dem[df_dem["sku"].astype(str) == sku]
        .sort_values("date")
        .set_index("date")["qty"]
        .asfreq("D").bfill()
    )
    ma = ts.rolling(window, min_periods=1).mean()

    last_val = float(ma.iloc[-1]) if len(ma) else 0.0
    future_idx = pd.date_range(ts.index.max()+pd.Timedelta(days=1), periods=horizon, freq="D")
    future = pd.Series([last_val]*horizon, index=future_idx, name="forecast")

    fig = plt.figure()
    plt.plot(ts.index, ts.values, label="actual")
    plt.plot(ma.index, ma.values, label=f"MA({window})")
    plt.plot(future.index, future.values, label="forecast")
    plt.legend()
    st.pyplot(fig)

    out = (
        pd.concat([ts.rename("qty"), ma.rename("ma"), future], axis=1)
        .reset_index().rename(columns={"index":"date"})
    )
    st.download_button("Download Forecast CSV", out.to_csv(index=False), file_name=f"forecast_{sku}.csv")
