import streamlit as st, pandas as pd
from utils.scoring import moving_average_forecast
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.title("Demand Forecast")
store = st.session_state.get("data_store", {})
if "demand.csv" not in store:
    st.error("Upload demand.csv on the Data Upload page.")
    st.stop()

df = store["demand.csv"].copy()
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])
sku = st.selectbox("SKU", sorted(df["sku"].astype(str).unique()))
window = st.slider("Moving average window", 3, 30, 7, help="Length of the smoothing window")
horizon = st.slider("Forecast horizon (days)", 7, 60, 21)

ts = (
    df[df["sku"].astype(str) == sku]
    .sort_values("date")
    .set_index("date")["qty"]
    .asfreq("D")
    .bfill()
)

ma, future = moving_average_forecast(ts, window, horizon)

# ---- Plotly chart: responsive + zoom + hover
fig = make_subplots(specs=[[{"secondary_y": False}]])
fig.add_trace(go.Scatter(x=ts.index, y=ts.values, name="actual", mode="lines+markers"))
fig.add_trace(go.Scatter(x=ma.index, y=ma.values, name=f"MA({window})", mode="lines"))
fig.add_trace(go.Scatter(x=future.index, y=future.values, name="forecast", mode="lines"))

fig.update_layout(
    height=420,
    margin=dict(l=30, r=20, t=60, b=40),
    template="plotly_dark",
    title=f"{sku} — Actuals, Moving Average, Forecast",
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
)
fig.update_xaxes(showgrid=True)
fig.update_yaxes(showgrid=True, rangemode="tozero")

st.plotly_chart(fig, use_container_width=True, config={"displaylogo": False})

out = (pd.concat([ts.rename("qty"), ma.rename("ma"), future], axis=1)
       .reset_index()
       .rename(columns={"index": "date"}))
st.download_button("⬇️ Download Forecast CSV", out.to_csv(index=False), f"forecast_{sku}.csv")
