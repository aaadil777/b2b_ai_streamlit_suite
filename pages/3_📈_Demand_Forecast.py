# pages/3_📈_Demand_Forecast.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from utils.scoring import moving_average_forecast

st.title("📈 Demand Forecast")
store = st.session_state.get("data_store", {})
if "demand.csv" not in store:
    st.error("Upload demand.csv on the **Data Upload** page.")
    st.stop()

df = store["demand.csv"].copy()
df["date"] = pd.to_datetime(df["date"], errors="coerce")
df = df.dropna(subset=["date"])
sku = st.selectbox("SKU", sorted(df["sku"].astype(str).unique()))
window = st.slider("Moving average window (days)", 3, 30, 7)
horizon = st.slider("Forecast horizon (days)", 7, 60, 14)

ts = (
    df[df["sku"].astype(str) == sku]
    .sort_values("date")
    .set_index("date")["qty"]
    .asfreq("D")
    .bfill()
)

ma, future = moving_average_forecast(ts, window, horizon)

# Matplotlib line for classic look (meets your original spec)
fig = plt.figure()
plt.plot(ts.index, ts.values, label="actual")
plt.plot(ma.index, ma.values, label=f"MA({window})")
plt.plot(future.index, future.values, label="forecast")
plt.title(f"{sku} — Actuals, Moving Average, Forecast")
plt.legend()
st.pyplot(fig, clear_figure=True)

out = (
    pd.concat([ts.rename("qty"), ma.rename("ma"), future], axis=1)
    .reset_index()
    .rename(columns={"index": "date"})
)
st.download_button(
    "⬇️ Download Forecast CSV",
    out.to_csv(index=False),
    file_name=f"forecast_{sku}.csv",
    mime="text/csv",
)

st.divider()
st.subheader("Seasonality & Ops Views")

df2 = df[df["sku"].astype(str) == sku].copy()
df2["week"] = df2["date"].dt.isocalendar().week.astype(int)
df2["dow_name"] = df2["date"].dt.day_name()
dow_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Heatmap: Week × Weekday
pivot = (
    df2.pivot_table(index="dow_name", columns="week", values="qty", aggfunc="sum")
    .reindex(dow_order)
)
fig3 = px.imshow(
    pivot,
    aspect="auto",
    title="Demand Heatmap (Week × Weekday)",
    labels=dict(x="ISO Week", y="Weekday", color="Qty"),
)
st.plotly_chart(fig3, use_container_width=True)

# Bar: Avg demand by weekday
avg_dow = df2.groupby("dow_name")["qty"].mean().reindex(dow_order).reset_index()
fig4 = px.bar(
    avg_dow,
    x="dow_name",
    y="qty",
    title="Average Demand by Weekday",
    labels={"dow_name": "Weekday", "qty": "Avg Qty"},
)
st.plotly_chart(fig4, use_container_width=True)
