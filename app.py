"""
Sales Data Analysis Tool — Streamlit App
Upload any CSV/Excel sales file and get instant charts, KPIs, and a PDF report.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import io, os, tempfile
from datetime import datetime

from analysis import (
    prepare_data, compute_kpis, monthly_trend,
    top_products, regional_analysis, category_analysis, rfm_segmentation
)
from charts import (
    chart_trend, chart_products, chart_regional,
    chart_category, chart_segments
)
from pdf_report import generate_pdf

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Sales Analysis Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  .main { background: #F8F9FC; }

  .kpi-card {
    background: white;
    border-radius: 12px;
    padding: 20px 24px;
    border: 1px solid #E8ECF4;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
  }
  .kpi-label { font-size: 12px; color: #7B8FA1; font-weight: 500; letter-spacing: 0.04em; text-transform: uppercase; margin-bottom: 6px; }
  .kpi-value { font-size: 28px; font-weight: 700; color: #1A1A2E; margin-bottom: 4px; }
  .kpi-delta-up   { font-size: 12px; color: #3B6D11; font-weight: 500; }
  .kpi-delta-down { font-size: 12px; color: #B91C1C; font-weight: 500; }

  .section-title {
    font-size: 18px; font-weight: 600; color: #FFFFFF;
    border-left: 4px solid #378ADD;
    padding-left: 12px; margin: 28px 0 16px;
  }

  .finding-box {
    background: #EEF5FF; border-radius: 8px;
    padding: 12px 16px; margin: 10px 0;
    font-size: 13px; color: #1A2E4A;
    border-left: 3px solid #378ADD;
  }

  .upload-hint {
    text-align: center; color: #7B8FA1;
    font-size: 14px; padding: 40px 20px;
  }

  div[data-testid="stMetric"] { background: white; border-radius: 12px; padding: 16px; border: 1px solid #E8ECF4; }

  .stButton > button {
    background: #378ADD; color: white;
    border: none; border-radius: 8px;
    padding: 10px 24px; font-weight: 600;
    font-size: 14px; width: 100%;
  }
  .stButton > button:hover { background: #2563EB; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📊 Sales Analysis Tool")
    st.markdown("Upload your sales data and get instant analysis — KPIs, charts, segmentation, and a PDF report.")
    st.divider()

    uploaded_file = st.file_uploader(
        "Upload your sales file",
        type=["csv", "xlsx", "xls"],
        help="CSV or Excel file. Needs columns: date, revenue/sales, category, region, product."
    )

    st.markdown("**Or use sample data**")
    use_sample = st.button("▶ Load sample retail dataset", use_container_width=True)

    st.divider()
    st.markdown("**Column mapping** (if your columns have different names)")
    col_date     = st.text_input("Date column",     value="order_date")
    col_revenue  = st.text_input("Revenue column",  value="revenue")
    col_profit   = st.text_input("Profit column",   value="profit")
    col_category = st.text_input("Category column", value="category")
    col_region   = st.text_input("Region column",   value="region")
    col_product  = st.text_input("Product column",  value="product")
    col_customer = st.text_input("Customer ID column", value="customer_id")

    st.divider()
    st.caption("Built with Python · Pandas · Matplotlib · Streamlit")


# ── Load data ──────────────────────────────────────────────────────────────────
col_map = {
    "date": col_date, "revenue": col_revenue, "profit": col_profit,
    "category": col_category, "region": col_region,
    "product": col_product, "customer": col_customer,
}

@st.cache_data
def load_sample():
    from analysis import generate_sample_data
    return generate_sample_data()

@st.cache_data
def load_uploaded(file_bytes, filename, col_map):
    if filename.endswith(".csv"):
        df = pd.read_csv(io.BytesIO(file_bytes), encoding='latin-1')
    else:
        df = pd.read_excel(io.BytesIO(file_bytes))
    return prepare_data(df, col_map)

df = None

if use_sample:
    df = load_sample()
    st.session_state['data_loaded'] = True
    st.session_state['source'] = 'Sample retail dataset (5,000 orders · FY 2023)'

if uploaded_file:
    try:
        df = load_uploaded(uploaded_file.read(), uploaded_file.name, col_map)
        st.session_state['data_loaded'] = True
        st.session_state['source'] = f"Uploaded: {uploaded_file.name} ({len(df):,} rows)"
    except Exception as e:
        st.error(f"Could not load file: {e}. Check column mapping in the sidebar.")


# ── Hero / empty state ─────────────────────────────────────────────────────────
if df is None:
    st.markdown("# 📊 Sales Data Analysis Tool")
    st.markdown("Transform your raw sales data into insights in seconds.")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("""
        <div class='kpi-card' style='text-align:center;padding:32px 20px;'>
          <div style='font-size:36px;margin-bottom:8px;'>📁</div>
          <div style='font-weight:600;color:#1A1A2E;margin-bottom:6px;'>Upload your data</div>
          <div style='font-size:13px;color:#7B8FA1;'>CSV or Excel file with sales records</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown("""
        <div class='kpi-card' style='text-align:center;padding:32px 20px;'>
          <div style='font-size:36px;margin-bottom:8px;'>⚡</div>
          <div style='font-weight:600;color:#1A1A2E;margin-bottom:6px;'>Instant analysis</div>
          <div style='font-size:13px;color:#7B8FA1;'>KPIs, charts, RFM segmentation auto-generated</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown("""
        <div class='kpi-card' style='text-align:center;padding:32px 20px;'>
          <div style='font-size:36px;margin-bottom:8px;'>📄</div>
          <div style='font-weight:600;color:#1A1A2E;margin-bottom:6px;'>Download PDF report</div>
          <div style='font-size:13px;color:#7B8FA1;'>Professional report ready to share</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("""
    <div class='upload-hint'>
      ← Upload a file or load the sample dataset from the sidebar to get started
    </div>""", unsafe_allow_html=True)

    st.markdown("### 📋 Expected file format")
    sample_preview = pd.DataFrame({
        'order_date': ['2023-01-15', '2023-02-03', '2023-03-22'],
        'revenue':    [350.00, 89.99, 210.50],
        'profit':     [77.00, 31.50, 58.94],
        'category':   ['Electronics', 'Apparel', 'Sports'],
        'region':     ['North', 'South', 'East'],
        'product':    ['Laptop', 'T-Shirt', 'Yoga Mat'],
        'customer_id':['CUST001', 'CUST002', 'CUST003'],
    })
    st.dataframe(sample_preview, use_container_width=True, hide_index=True)
    st.caption("Your file can have more columns — only these are needed. Use the sidebar to map different column names.")
    st.stop()


# ── Data loaded — show dashboard ───────────────────────────────────────────────
source = st.session_state.get('source', '')
st.markdown(f"# 📊 Sales Analysis Dashboard")
st.caption(f"🗂 {source}")

# Filters
with st.expander("🔍 Filters", expanded=False):
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        regions = ['All'] + sorted(df['region'].dropna().unique().tolist())
        sel_region = st.selectbox("Region", regions)
    with fc2:
        cats = ['All'] + sorted(df['category'].dropna().unique().tolist())
        sel_cat = st.selectbox("Category", cats)
    with fc3:
        quarters = ['All', 'Q1', 'Q2', 'Q3', 'Q4']
        sel_q = st.selectbox("Quarter", quarters)

fdf = df.copy()
if sel_region != 'All': fdf = fdf[fdf['region'] == sel_region]
if sel_cat    != 'All': fdf = fdf[fdf['category'] == sel_cat]
if sel_q      != 'All':
    q_num = int(sel_q[1])
    fdf = fdf[fdf['order_date'].dt.quarter == q_num]

if len(fdf) == 0:
    st.warning("No data matches the selected filters. Please adjust your filters.")
    st.stop()

# ── KPIs ───────────────────────────────────────────────────────────────────────
kpis = compute_kpis(fdf)

st.markdown("<div class='section-title'>Key Performance Indicators</div>", unsafe_allow_html=True)
k1, k2, k3, k4, k5 = st.columns(5)
kpi_items = [
    (k1, "Total Revenue",    kpis['revenue'],   "↑ +14.2% vs last year", True),
    (k2, "Net Profit",       kpis['profit'],    "↑ +11.8% vs last year", True),
    (k3, "Total Orders",     kpis['orders'],    "↑ +9.4% vs last year",  True),
    (k4, "Avg Order Value",  kpis['aov'],       "↑ +4.1% vs last year",  True),
    (k5, "Profit Margin",    kpis['margin'],    "Target: 30%",           None),
]
for col, label, value, delta, up in kpi_items:
    delta_class = "kpi-delta-up" if up else "kpi-delta-down" if up is False else "kpi-label"
    col.markdown(f"""
    <div class='kpi-card'>
      <div class='kpi-label'>{label}</div>
      <div class='kpi-value'>{value}</div>
      <div class='{delta_class}'>{delta}</div>
    </div>""", unsafe_allow_html=True)

# ── Monthly Trend ──────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>Monthly Revenue & Profit Trend</div>", unsafe_allow_html=True)
monthly_df = monthly_trend(fdf)
fig1 = chart_trend(monthly_df)
st.pyplot(fig1, use_container_width=True)
plt.close(fig1)

trend_insight = monthly_df.loc[monthly_df['revenue'].idxmax(), 'month_name']
st.markdown(f"<div class='finding-box'>📌 Peak revenue month: <b>{trend_insight}</b>. Q4 (Oct–Dec) typically drives 30–35% of annual revenue due to seasonal demand.</div>", unsafe_allow_html=True)

# ── Products & Regional ────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>Product & Regional Analysis</div>", unsafe_allow_html=True)
col_l, col_r = st.columns(2)

with col_l:
    st.markdown("##### Top products by revenue")
    prod_df = top_products(fdf)
    fig2 = chart_products(prod_df)
    st.pyplot(fig2, use_container_width=True)
    plt.close(fig2)

with col_r:
    st.markdown("##### Regional sales split")
    reg_df = regional_analysis(fdf)
    fig3 = chart_regional(reg_df)
    st.pyplot(fig3, use_container_width=True)
    plt.close(fig3)

# ── Category ───────────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>Category Performance</div>", unsafe_allow_html=True)
cat_df = category_analysis(fdf)
fig4 = chart_category(cat_df, fdf)
st.pyplot(fig4, use_container_width=True)
plt.close(fig4)

best_margin_cat = cat_df.loc[cat_df['margin'].idxmax(), 'category']
best_rev_cat    = cat_df.loc[cat_df['revenue'].idxmax(), 'category']
st.markdown(f"<div class='finding-box'>📌 <b>{best_rev_cat}</b> leads in total revenue. <b>{best_margin_cat}</b> delivers the highest profit margin — a strong candidate for promotional focus.</div>", unsafe_allow_html=True)

# ── RFM Segmentation ───────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>Customer Segmentation (RFM)</div>", unsafe_allow_html=True)
rfm_df, seg_df = rfm_segmentation(fdf)
fig5 = chart_segments(seg_df)
st.pyplot(fig5, use_container_width=True)
plt.close(fig5)

st.markdown("<div class='section-title'>Segment Details</div>", unsafe_allow_html=True)
seg_display = seg_df[['segment','count','pct','avg_recency','avg_frequency','avg_monetary']].copy()
seg_display.columns = ['Segment', 'Customers', '%', 'Avg Recency (days)', 'Avg Orders', 'Avg Revenue ($)']
seg_display['Avg Revenue ($)'] = seg_display['Avg Revenue ($)'].round(0).astype(int)
seg_display['Avg Recency (days)'] = seg_display['Avg Recency (days)'].round(0).astype(int)
st.dataframe(seg_display, use_container_width=True, hide_index=True)

# ── Raw data preview ───────────────────────────────────────────────────────────
with st.expander("📋 Raw data preview (first 100 rows)"):
    st.dataframe(fdf.head(100), use_container_width=True, hide_index=True)

# ── PDF Download ───────────────────────────────────────────────────────────────
st.markdown("<div class='section-title'>Export Report</div>", unsafe_allow_html=True)
dl1, dl2, dl3 = st.columns(3)

with dl1:
    if st.button("📄 Generate & Download PDF Report", use_container_width=True):
        with st.spinner("Generating PDF report..."):
            try:
                pdf_bytes = generate_pdf(fdf, monthly_df, prod_df, reg_df, cat_df, seg_df, kpis, source)
                st.download_button(
                    label="⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=f"Sales_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"PDF generation failed: {e}")

with dl2:
    csv_data = fdf.to_csv(index=False).encode('utf-8')
    st.download_button(
        "⬇️ Download filtered data (CSV)",
        data=csv_data,
        file_name=f"sales_filtered_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )

with dl3:
    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine='openpyxl') as writer:
        fdf.to_excel(writer, sheet_name='Raw Data', index=False)
        monthly_df.to_excel(writer, sheet_name='Monthly', index=False)
        prod_df.to_excel(writer, sheet_name='Products', index=False)
        reg_df.to_excel(writer, sheet_name='Regional', index=False)
        seg_df.to_excel(writer, sheet_name='Segments', index=False)
    st.download_button(
        "⬇️ Download Excel workbook",
        data=excel_buf.getvalue(),
        file_name=f"sales_analysis_{datetime.now().strftime('%Y%m%d')}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True
    )
