import streamlit as st, pandas as pd, matplotlib.pyplot as plt
from utils.scoring import moving_average_forecast

st.title("Demand Forecast")
store = st.session_state.get("data_store", {})
if "demand.csv" not in store:
    st.error("Upload demand.csv on the Data Upload page.")
    st.stop()

df = store["demand.csv"]
sku = st.selectbox("SKU", sorted(df["sku"].astype(str).unique()))
window = st.slider("Moving average window", 3, 30, 7)
horizon = st.slider("Forecast horizon (days)", 7, 60, 14)

ts = (df[df["sku"].astype(str)==sku]
      .sort_values("date").set_index("date")["qty"].asfreq("D").bfill())

ma, future = moving_average_forecast(ts, window, horizon)

fig = plt.figure()
plt.plot(ts.index, ts.values, label="actual")
plt.plot(ma.index, ma.values, label=f"MA({window})")
plt.plot(future.index, future.values, label="forecast")
plt.legend(); st.pyplot(fig, clear_figure=True)

out = (pd.concat([ts.rename("qty"), ma.rename("ma"), future], axis=1)
        .reset_index().rename(columns={"index":"date"}))
st.download_button("Download Forecast CSV", out.to_csv(index=False), f"forecast_{sku}.csv")
