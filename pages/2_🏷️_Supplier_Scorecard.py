import streamlit as st, pandas as pd
from utils.scoring import supplier_scores

st.title("Supplier Scorecard")
store = st.session_state.get("data_store", {})
if "suppliers.csv" not in store:
    st.error("Upload suppliers.csv on the Data Upload page.")
    st.stop()

with st.sidebar:
    st.header("Weights")
    w = {
      "otd": st.slider("On-time delivery", 0.0,1.0,0.4,0.05),
      "cost": st.slider("Cost variance", 0.0,1.0,0.2,0.05),
      "qual": st.slider("Quality (PPM)", 0.0,1.0,0.25,0.05),
      "risk": st.slider("Risk events", 0.0,1.0,0.15,0.05)
    }

scores = supplier_scores(store["suppliers.csv"], w)
st.dataframe(scores, use_container_width=True)
st.download_button("Download Top 10", scores.head(10).to_csv(index=False), "top_suppliers.csv")
