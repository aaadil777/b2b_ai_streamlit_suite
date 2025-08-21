import streamlit as st
st.set_page_config(page_title="B2B AI Suite", layout="wide")
st.title("B2B AI Suite — Procurement & Planning")
st.markdown("""
Use the pages on the left:
1) **Data Upload** — load CSVs or use samples  
2) **Supplier Scorecard** — rank suppliers with adjustable weights  
3) **Demand Forecast** — moving-average baseline + export  
4) **What-If** — simulate service level, lead time, MOQ  
""")
