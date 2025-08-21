import streamlit as st
import pandas as pd, numpy as np
import matplotlib.pyplot as plt
from matplotlib.dates import AutoDateLocator, DateFormatter

st.title("🧪 What-If Scenarios (Inventory)")

store = st.session_state.get("data_store", {})
if "demand.csv" not in store:
    st.error("Upload demand.csv on the **Data Upload** page (or load synthetic samples).")
    st.stop()

demand = store["demand.csv"].copy()
demand["date"] = pd.to_datetime(demand["date"], errors="coerce")
demand = demand.dropna(subset=["date"])

sku = st.selectbox("SKU", sorted(demand["sku"].astype(str).unique()))
lead = st.slider("Lead time (days)", 1, 120, 30)
service = st.slider("Service level target", 0.80, 0.999, 0.95, 0.005)
moq = st.number_input("MOQ (units)", min_value=0, value=0, step=10)
ss_sigma = st.slider("Safety stock factor (σ)", 0.0, 3.0, 1.0, 0.1)
horizon = st.slider("Simulation horizon (days)", 30, 180, 120)

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
    rng.normal(mu, sigma if sigma > 0 else max(mu * 0.1, 1), horizon), 0, None
).astype(int)

on_hand, backlog, pipe = 0.0, 0.0, []
rows = []
for d, dem in zip(dates, future_demand):
    # Receive arrivals
    arrivals = sum(q for (arr, q) in pipe if arr == d)
    pipe = [(a, q) for (a, q) in pipe if a != d]
    on_hand += arrivals

    # Policy: reorder when position < safety
    if (on_hand - backlog) < safety:
        order_qty = max(moq, int(mu * lead))
        if order_qty > 0:
            pipe.append((d + pd.Timedelta(days=lead), order_qty))

    # Ship demand with backlog
    available = max(0.0, on_hand - backlog)
    shipped = min(available, dem + backlog)
    if shipped >= backlog:
        shipped_net = shipped - backlog
        backlog = 0.0
        on_hand = max(0.0, on_hand - shipped_net)
        unmet = dem - shipped_net
        backlog = max(0.0, backlog + unmet)
    else:
        backlog -= shipped

    rows.append({"date": d, "demand": int(dem), "on_hand": float(on_hand), "backlog": float(backlog)})

sim = pd.DataFrame(rows)
inv_position = sim["on_hand"] - sim["backlog"]

# ---- KPIs
delayed = sim["backlog"].diff().clip(lower=0).sum() if sim["backlog"].sum() > 0 else 0.0
fill_rate = 1.0 - (delayed / sim["demand"].sum() if sim["demand"].sum() else 0.0)
c1, c2, c3 = st.columns(3)
c1.metric("Fill rate", f"{fill_rate:.1%}")
c2.metric("Stockout days", int((sim["on_hand"] <= 0).sum()))
c3.metric("Avg on-hand", f"{sim['on_hand'].mean():.1f}")

# ---- Roomier dual-axis chart + position area
plt.rcParams.update({"font.size": 11})
fig, ax1 = plt.subplots(figsize=(11.5, 4.6), constrained_layout=True)

locator, fmt = AutoDateLocator(), DateFormatter("%Y-%m-%d")
ax1.xaxis.set_major_locator(locator)
ax1.xaxis.set_major_formatter(fmt)

ax1.plot(sim["date"], sim["demand"], label="demand", alpha=.9)
ax1.plot(sim["date"], sim["backlog"], label="backlog", alpha=.9)
ax1.set_ylabel("Demand / Backlog")
ax1.grid(True, alpha=.25)

ax2 = ax1.twinx()
ax2.plot(sim["date"], sim["on_hand"], label="on_hand", alpha=.9)
ax2.fill_between(sim["date"], inv_position, 0, alpha=.15, label="inventory position")
ax2.set_ylabel("On-hand")
ax2.grid(False)

ax1.set_title(f"Inventory Simulation • {sku} (dual y-axes)")
lines, labels = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines + lines2, labels + labels2, loc="upper left")

st.pyplot(fig, clear_figure=True, use_container_width=True)

# ---- Backlog distribution (where the 'risk' lives)
fig2, ax = plt.subplots(figsize=(11.5, 3.6), constrained_layout=True)
ax.hist(sim["backlog"], bins=20, alpha=.8)
ax.set_title("Backlog distribution")
ax.set_xlabel("Units in backlog")
ax.set_ylabel("Days")
ax.grid(True, alpha=.25)
st.pyplot(fig2, clear_figure=True, use_container_width=True)

st.download_button("Export scenario CSV", sim.to_csv(index=False), file_name=f"what_if_{sku}.csv", mime="text/csv")
