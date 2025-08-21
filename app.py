import streamlit as st
st.set_page_config(page_title="B2B AI Suite", layout="wide")
st.title("B2B AI Suite — Procurement & Planning")

import pandas as pd
store = st.session_state.get("data_store", {})
sup = store.get("suppliers.csv")
dem = store.get("demand.csv")

c1,c2,c3 = st.columns(3)
c1.metric("Suppliers loaded", f"{0 if sup is None else len(sup):,}")
avg_otd = (sup["otd_rate"].mean()*100 if sup is not None else 0)
c2.metric("Avg OTD", f"{avg_otd:.1f}%")
next_14 = (dem[dem["date"]>=pd.Timestamp.today().normalize()]["qty"].head(14).sum()
           if dem is not None and "date" in dem else 0)
c3.metric("Next 14-day demand", f"{int(next_14):,}")

st.markdown("""
Use the pages on the left:
1) **Data Upload** — load CSVs or use samples  
2) **Supplier Scorecard** — rank suppliers with adjustable weights  
3) **Demand Forecast** — moving-average baseline + export  
4) **What-If** — simulate service level, lead time, MOQ  
""")
