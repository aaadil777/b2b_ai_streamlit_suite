# home.py
import streamlit as st
import pandas as pd

st.set_page_config(page_title="B2B AI Suite", layout="wide")

# ---- minimal styling (keeps requirements clean)
st.markdown("""
<style>
.hero {font-size:1.05rem; opacity:.95; margin-top:-6px;}
.card {padding:14px 16px; border:1px solid rgba(255,255,255,.08); border-radius:14px; background:rgba(255,255,255,.03);}
.card h3{margin:0 0 6px 0; font-size:1.05rem}
.grid {display:grid; grid-template-columns:repeat(auto-fit,minmax(240px,1fr)); gap:14px;}
.badge {display:inline-block; padding:4px 10px; border-radius:999px; border:1px solid rgba(255,255,255,.2); font-size:.85rem; margin-right:6px;}
.kicker {font-size:.9rem; letter-spacing:.08em; text-transform:uppercase; opacity:.7}
</style>
""", unsafe_allow_html=True)

st.title("B2B AI Suite — Procurement & Planning")
st.markdown(
    """
<p class="hero">
<strong>Purpose:</strong> give supply-chain teams a fast, self-serve way to
spot supplier risk, baseline demand, and run inventory <em>what-ifs</em> — without heavy BI setup.<br>
<strong>Business value:</strong> better service levels with less working capital, fewer expedites, and
clear vendor conversations (OTD • quality • cost variance • risk).
</p>
""",
    unsafe_allow_html=True,
)

# ---- KPIs (live once data is uploaded)
store = st.session_state.get("data_store", {})
sup = store.get("suppliers.csv")
dem = store.get("demand.csv")

c1, c2, c3 = st.columns(3)
c1.metric("Suppliers loaded", f"{0 if sup is None else len(sup):,}")
avg_otd = (sup["otd_rate"].mean()*100 if sup is not None else 0)
c2.metric("Avg OTD", f"{avg_otd:.1f}%")
next_14 = (dem[dem["date"]>=pd.Timestamp.today().normalize()]["qty"].head(14).sum()
           if dem is not None and "date" in dem else 0)
c3.metric("Next 14-day demand", f"{int(next_14):,}")

st.markdown("---")

# ---- feature cards with icons
st.markdown('<div class="kicker">What’s inside</div>', unsafe_allow_html=True)
st.markdown('<div class="grid">', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        """<div class="card">
        <h3>📦 Supplier Scorecard</h3>
        KPI-weighted ranks across OTD, quality (PPM), cost variance, 12-mo risk.
        Includes bubble & Pareto views for quick focus.</div>""", unsafe_allow_html=True)

with col2:
    st.markdown(
        """<div class="card">
        <h3>📈 Demand Baseline</h3>
        Moving-average forecast + weekday/weekly patterns with CSV export.</div>""",
        unsafe_allow_html=True)

with col3:
    st.markdown(
        """<div class="card">
        <h3>🧪 What-If Scenarios</h3>
        Simulate lead time, service level, MOQ, safety stock; dual-axis
        charts for demand vs on-hand; backlog distribution.</div>""",
        unsafe_allow_html=True)

with col4:
    st.markdown(
        """<div class="card">
        <h3>🧰 Practical</h3>
        Built in Streamlit/Pandas. Lightweight, fast to demo, and easy to extend
        for real supplier & SKU data.</div>""",
        unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ---- quick start
st.markdown("### Quick start (3 steps)")
st.markdown(
    """
1. **Data Upload** — drag in `suppliers.csv` and `demand.csv` (or use samples).  
2. **Supplier Scorecard** — tune weights → download top-10 list.  
3. **What-If** — set lead time / service target → export scenario CSV.  
"""
)

# ---- small badges / links
st.markdown(
    """
<span class="badge">Streamlit</span>
<span class="badge">Pandas</span>
<span class="badge">NumPy</span>
<span class="badge">Matplotlib</span>
<span class="badge">Plotly</span>
""",
    unsafe_allow_html=True,
)
