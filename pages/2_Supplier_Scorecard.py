# pages/2_🏷️_Supplier_Scorecard.py
import streamlit as st
import pandas as pd
import plotly.express as px
from utils.scoring import supplier_scores

st.title("🏷️ Supplier Scorecard")
store = st.session_state.get("data_store", {})
if "suppliers.csv" not in store:
    st.error("Upload suppliers.csv on the **Data Upload** page.")
    st.stop()

with st.sidebar:
    st.header("Score Weights")
    w = {
        "otd":  st.slider("On-time delivery", 0.0, 1.0, 0.40, 0.05),
        "cost": st.slider("Cost variance",    0.0, 1.0, 0.20, 0.05),
        "qual": st.slider("Quality (PPM)",    0.0, 1.0, 0.25, 0.05),
        "risk": st.slider("Risk events",      0.0, 1.0, 0.15, 0.05),
    }

scores = supplier_scores(store["suppliers.csv"], w)
st.subheader("Ranked Suppliers")
st.dataframe(scores, use_container_width=True)

st.download_button(
    "⬇️ Download Top 10 (CSV)",
    scores.head(10).to_csv(index=False),
    file_name="top_suppliers.csv",
    mime="text/csv",
)

st.divider()
st.subheader("Quality vs On-Time (bubble=size |cost variance|, color=score)")
bubble = scores.copy()
bubble["bubble_size"] = bubble["cost_variance"].abs() + 0.01
fig1 = px.scatter(
    bubble,
    x="otd_rate",
    y="quality_ppm",
    size="bubble_size",
    color="score",
    hover_name="name",
    labels={"otd_rate": "On-time delivery", "quality_ppm": "Quality (PPM)"},
    title="Supplier Segmentation",
)
# Lower PPM is better; flip axis if you want this visual convention
fig1.update_yaxes(autorange="reversed")
st.plotly_chart(fig1, use_container_width=True)

st.subheader("Pareto: Top Quality Issues (PPM)")
pareto = scores.nlargest(10, "quality_ppm").sort_values("quality_ppm", ascending=False)
fig2 = px.bar(
    pareto,
    x="name",
    y="quality_ppm",
    labels={"name": "Supplier", "quality_ppm": "PPM"},
    title="Top Defect Contributors",
)
st.plotly_chart(fig2, use_container_width=True)
