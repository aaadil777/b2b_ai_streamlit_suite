import streamlit as st, pandas as pd, numpy as np

st.title("Data Upload")
st.caption("Upload suppliers.csv and demand.csv, or load synthetic samples.")

store = st.session_state.setdefault("data_store", {})

c1,c2 = st.columns(2)
with c1:
    sup = st.file_uploader("Upload suppliers.csv", type=["csv"])
    if sup: store["suppliers.csv"] = pd.read_csv(sup)
with c2:
    dem = st.file_uploader("Upload demand.csv", type=["csv"])
    if dem:
        df = pd.read_csv(dem)
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        store["demand.csv"] = df.dropna(subset=["date"])

st.divider()
if st.button("Load synthetic samples"):
    rng = np.random.default_rng(42)
    suppliers = pd.DataFrame({
      "supplier_id":[f"S{i:03d}" for i in range(1,21)],
      "name":[f"Supplier {i}" for i in range(1,21)],
      "otd_rate":rng.uniform(0.85,0.99,20),
      "cost_variance":rng.normal(0.0,0.03,20),
      "quality_ppm":rng.integers(80,1200,20),
      "risk_events_12m":rng.integers(0,5,20)
    })
    dates = pd.date_range("2024-01-01","2024-06-30",freq="D")
    demand = pd.DataFrame({"date":dates, "sku":"HVLV-256",
                           "qty":(rng.poisson(20,len(dates))+rng.normal(0,3,len(dates))).clip(0).astype(int)})
    store["suppliers.csv"], store["demand.csv"] = suppliers, demand
    st.success("Loaded synthetic datasets.")

for k,v in store.items():
    with st.expander(f"Preview: {k}"):
        st.dataframe(v.head(25), use_container_width=True)
