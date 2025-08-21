# pages/4_🧪_What-If_Scenarios.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px

st.set_page_config(page_title="What-If Scenarios", layout="wide")
st.title("🧪 What-If Scenarios (Inventory)")

# --- Data guardrails ---
store = st.session_state.get("data_store", {})
if "demand.csv" not in store:
    st.error("Upload demand.csv on the **Data Upload** page (or load synthetic samples).")
    st.stop()

# --- Inputs ---
demand = store["demand.csv"].copy().sort_values("date")
demand["date"] = pd.to_datetime(demand["date"], errors="coerce")
demand = demand.dropna(subset=["date"])
sku = st.selectbox("SKU", sorted(demand["sku"].astype(str).unique()))
lead = st.slider("Lead time (days)", 1, 120, 30)
service = st.slider("Service level target", 0.80, 0.999, 0.95, 0.005)
moq = st.number_input("MOQ", min_value=0, value=0, step=10)
ss_sigma = st.slider("Safety stock factor (σ)", 0.0, 3.0, 1.0, 0.1)
horizon = st.slider("Simulation horizon (days)", 30, 180, 90)
chart_mode = st.radio("Chart display", ["Dual y-axes (recommended)", "Normalized (0–1)"], index=0, horizontal=True)

# --- Simple simulator ---
hist = demand[demand["sku"].astype(str) == sku].tail(120)
if hist.empty:
    st.warning("No history for the selected SKU.")
    st.stop()

sigma = float(hist["qty"].std() or 0.0)
mu = float(hist["qty"].mean() or 0.0)
safety = ss_sigma * sigma

start = pd.to_datetime(hist["date"].max()) + pd.Timedelta(days=1)
dates = pd.date_range(start, periods=horizon, freq="D")
rng = np.random.default_rng(123)
future_demand = np.clip(
    rng.normal(mu, sigma if sigma > 0 else max(mu * 0.1, 1), horizon),
    0, None
).astype(int)

on_hand, backlog, pipe = 0.0, 0.0, []
rows = []
for d, dem in zip(dates, future_demand):
    # Receive arrivals
    arrivals = sum(q for (arr, q) in pipe if arr == d)
    pipe = [(a, q) for (a, q) in pipe if a != d]
    on_hand += arrivals

    # Reorder when inventory position < safety stock
    if (on_hand - backlog) < safety:
        order_qty = max(moq, int(mu * lead))
        if order_qty > 0:
            pipe.append((d + pd.Timedelta(days=lead), order_qty))

    # Ship demand
    available = max(0.0, on_hand - backlog)
    shipped = min(available, dem + backlog)
    if shipped >= backlog:
        shipped_net = shipped - backlog
        backlog = 0.0
        on_hand = max(0.0, on_hand - shipped_net)
        unmet = dem - shipped_net
        backlog = max(0.0, backlog + unmet)
    else:
        backlog = backlog - shipped  # on_hand unchanged

    rows.append({"date": d, "demand": int(dem), "on_hand": float(on_hand), "backlog": float(backlog)})

sim = pd.DataFrame(rows)

# --- KPIs ---
delayed = sim["backlog"].diff().clip(lower=0).sum() if sim["backlog"].notna().any() else 0.0
fill_rate = 1.0 - (delayed / sim["demand"].sum() if sim["demand"].sum() else 0.0)
c1, c2, c3 = st.columns(3)
c1.metric("Fill rate", f"{fill_rate:.1%}")
c2.metric("Stockouts (days)", int((sim["on_hand"] <= 0).sum()))
c3.metric("Avg on-hand (units)", f"{sim['on_hand'].mean():.1f}")

# --- Chart (dual y-axes or normalized) ---
fig = plt.figure()
if chart_mode.startswith("Dual"):
    fig, ax1 = plt.subplots()
    ax1.plot(sim["date"], sim["demand"], label="demand")
    ax1.plot(sim["date"], sim["backlog"], label="backlog")
    ax1.set_ylabel("Demand / Backlog")
    ax1.legend(loc="upper left")

    ax2 = ax1.twinx()
    ax2.plot(sim["date"], sim["on_hand"], label="on_hand", alpha=0.9)
    ax2.set_ylabel("On-hand")
    ax2.legend(loc="upper right")

    ax1.set_title(f"Inventory Simulation • {sku}  (dual y-axes)")
else:
    scaled = sim.copy()
    for col in ["demand", "on_hand", "backlog"]:
        mx = scaled[col].max() or 1.0
        scaled[col] = scaled[col] / mx
    plt.plot(scaled["date"], scaled["demand"], label="demand")
    plt.plot(scaled["date"], scaled["on_hand"], label="on_hand")
    plt.plot(scaled["date"], scaled["backlog"], label="backlog")
    plt.ylabel("Normalized (0–1)")
    plt.title(f"Inventory Simulation • {sku}  (normalized)")

plt.xlabel("date")
plt.legend()
st.pyplot(fig, clear_figure=True)

# --- Extra visuals for logistics teams ---
sim["inv_position"] = sim["on_hand"] - sim["backlog"]
figA = px.area(sim, x="date", y=["demand", "inv_position"],
               title="Demand vs Inventory Position (units)")
st.plotly_chart(figA, use_container_width=True)

figB = px.histogram(sim, x="backlog", nbins=25, title="Backlog Distribution")
st.plotly_chart(figB, use_container_width=True)

# --- Export ---
st.download_button(
    "⬇️ Export scenario CSV",
    sim.to_csv(index=False),
    file_name=f"what_if_{sku}.csv",
    mime="text/csv",
)
