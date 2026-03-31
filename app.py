import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings("ignore")

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Superstore Sales Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');
  html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

  .kpi {
    background: var(--background-color);
    border: 1px solid rgba(128,128,128,0.2);
    border-radius: 14px; padding: 18px 22px;
    text-align: center;
  }
  .kpi-label { font-size: 11px; font-weight: 600; text-transform: uppercase;
    letter-spacing: .08em; color: #888; margin-bottom: 6px; }
  .kpi-value { font-size: 28px; font-weight: 700; }
  .kpi-sub   { font-size: 12px; color: #888; margin-top: 3px; }
  .kpi-green  { color: #16a34a; }
  .kpi-red    { color: #dc2626; }
  .kpi-blue   { color: #2563eb; }
  .kpi-amber  { color: #d97706; }

  .section {
    font-size: 12px; font-weight: 600; text-transform: uppercase;
    letter-spacing: .1em; color: #888;
    border-bottom: 1px solid rgba(128,128,128,0.2);
    padding-bottom: 6px; margin: 24px 0 14px;
  }
  .insight {
    background: rgba(99,102,241,0.08);
    border-left: 3px solid #6366f1;
    border-radius: 0 8px 8px 0;
    padding: 9px 14px; font-size: 13px;
    color: inherit; margin: 5px 0; line-height: 1.6;
  }
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding-top: 1.5rem; }
  [data-testid="stSidebar"] { border-right: 1px solid rgba(128,128,128,0.15); }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load():
    df = pd.read_csv("superstore_clean.csv")
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    df["Ship_Date"]  = pd.to_datetime(df["Ship_Date"])
    return df

df_all = load()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 Superstore")
    st.markdown("<div style='color:#888;font-size:12px;margin-bottom:1rem'>Sales Intelligence Dashboard</div>", unsafe_allow_html=True)

    years = ["All"] + sorted(df_all["Order_Year"].unique().tolist(), reverse=True)
    sel_year = st.selectbox("📅 Year", years)

    regions = ["All"] + sorted(df_all["Region"].unique().tolist())
    sel_region = st.selectbox("🌍 Region", regions)

    segments = ["All"] + sorted(df_all["Segment"].unique().tolist())
    sel_segment = st.selectbox("👥 Segment", segments)

    categories = ["All"] + sorted(df_all["Category"].unique().tolist())
    sel_category = st.selectbox("📦 Category", categories)

    st.markdown("---")
    st.markdown("<div style='color:#888;font-size:11px'>9,994 orders · 2014–2017<br>United States · 49 states</div>", unsafe_allow_html=True)

# ── Filter ────────────────────────────────────────────────────────────────────
df = df_all.copy()
if sel_year     != "All": df = df[df["Order_Year"]  == int(sel_year)]
if sel_region   != "All": df = df[df["Region"]      == sel_region]
if sel_segment  != "All": df = df[df["Segment"]     == sel_segment]
if sel_category != "All": df = df[df["Category"]    == sel_category]

# ── Metrics ───────────────────────────────────────────────────────────────────
total_sales    = df["Sales"].sum()
total_profit   = df["Profit"].sum()
avg_margin     = df["Profit_Margin_%"].mean()
total_orders   = df["Order_ID"].nunique()
total_customers= df["Customer_ID"].nunique()
avg_order_val  = total_sales / total_orders if total_orders > 0 else 0
loss_orders    = (df["Is_Profitable"] == "Loss").sum()
avg_ship_days  = df["Days_to_Ship"].mean()

def fmt(v):
    if abs(v) >= 1e6: return f"${v/1e6:.2f}M"
    if abs(v) >= 1e3: return f"${v/1e3:.1f}K"
    return f"${v:.0f}"

# ── Header ────────────────────────────────────────────────────────────────────
period = str(sel_year) if sel_year != "All" else "2014 – 2017"
st.markdown(f"## 🛒 Superstore Sales Dashboard")
st.markdown(f"<div style='color:#888;font-size:13px;margin-bottom:1.5rem'>Period: {period} &nbsp;·&nbsp; {len(df):,} transactions &nbsp;·&nbsp; {total_customers:,} customers</div>", unsafe_allow_html=True)

# ── KPI Row ───────────────────────────────────────────────────────────────────
c1,c2,c3,c4,c5,c6 = st.columns(6)
kpis = [
    (c1, "Total Sales",    fmt(total_sales),          "All revenue",          "kpi-blue"),
    (c2, "Total Profit",   fmt(total_profit),          "Net profit",           "kpi-green" if total_profit>0 else "kpi-red"),
    (c3, "Avg Margin",     f"{avg_margin:.1f}%",       "Profit margin %",      "kpi-green" if avg_margin>10 else "kpi-red"),
    (c4, "Total Orders",   f"{total_orders:,}",        "Unique orders",        "kpi-blue"),
    (c5, "Avg Order Value",fmt(avg_order_val),         "Per order",            "kpi-amber"),
    (c6, "Avg Ship Days",  f"{avg_ship_days:.1f}d",    "Order to delivery",    "kpi-amber"),
]
for col, label, val, sub, color in kpis:
    with col:
        st.markdown(f"""<div class="kpi">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value {color}">{val}</div>
          <div class="kpi-sub">{sub}</div>
        </div>""", unsafe_allow_html=True)

# ── Page tabs ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Overview", "📦 Products", "👥 Customers & Shipping"])

# ════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ════════════════════════════════════════════════════════════
with tab1:
    # Monthly trend
    st.markdown("<div class='section'>Monthly Sales & Profit Trend</div>", unsafe_allow_html=True)
    monthly = df.groupby("Order_YearMonth").agg(
        Sales=("Sales","sum"), Profit=("Profit","sum")
    ).reset_index().sort_values("Order_YearMonth")

    fig_trend = go.Figure()
    fig_trend.add_trace(go.Scatter(
        x=monthly["Order_YearMonth"], y=monthly["Sales"],
        name="Sales", line=dict(color="#2563eb", width=2.5),
        fill="tozeroy", fillcolor="rgba(37,99,235,0.07)",
        mode="lines+markers", marker=dict(size=5)
    ))
    fig_trend.add_trace(go.Scatter(
        x=monthly["Order_YearMonth"], y=monthly["Profit"],
        name="Profit", line=dict(color="#16a34a", width=2.5),
        fill="tozeroy", fillcolor="rgba(22,163,74,0.07)",
        mode="lines+markers", marker=dict(size=5)
    ))
    fig_trend.update_layout(
        height=300, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=12), hovermode="x unified",
        legend=dict(orientation="h", y=1.1, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=False, tickangle=45),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
        margin=dict(l=10,r=10,t=30,b=10),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

    # Category + Region row
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("<div class='section'>Sales by Category</div>", unsafe_allow_html=True)
        cat = df.groupby("Category").agg(Sales=("Sales","sum"), Profit=("Profit","sum")).reset_index()
        cat["Margin"] = (cat["Profit"]/cat["Sales"]*100).round(1)
        fig_cat = go.Figure()
        fig_cat.add_trace(go.Bar(name="Sales",  x=cat["Category"], y=cat["Sales"],  marker_color="#2563eb", opacity=0.85))
        fig_cat.add_trace(go.Bar(name="Profit", x=cat["Category"], y=cat["Profit"], marker_color="#16a34a", opacity=0.85))
        fig_cat.update_layout(
            height=280, barmode="group",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(size=12), legend=dict(orientation="h", y=1.1, bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
            margin=dict(l=10,r=10,t=30,b=10),
        )
        st.plotly_chart(fig_cat, use_container_width=True)

    with col_r:
        st.markdown("<div class='section'>Sales & Profit by Region</div>", unsafe_allow_html=True)
        reg = df.groupby("Region").agg(Sales=("Sales","sum"), Profit=("Profit","sum")).reset_index().sort_values("Sales")
        fig_reg = go.Figure()
        fig_reg.add_trace(go.Bar(name="Sales",  y=reg["Region"], x=reg["Sales"],  orientation="h", marker_color="#6366f1", opacity=0.85))
        fig_reg.add_trace(go.Bar(name="Profit", y=reg["Region"], x=reg["Profit"], orientation="h", marker_color="#f59e0b", opacity=0.85))
        fig_reg.update_layout(
            height=280, barmode="group",
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(size=12), legend=dict(orientation="h", y=1.1, bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
            yaxis=dict(showgrid=False),
            margin=dict(l=10,r=10,t=30,b=10),
        )
        st.plotly_chart(fig_reg, use_container_width=True)

    # Quarterly bar + Segment donut
    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("<div class='section'>Quarterly Performance</div>", unsafe_allow_html=True)
        qtr = df.groupby(["Order_Year","Order_Quarter"]).agg(Sales=("Sales","sum"), Profit=("Profit","sum")).reset_index()
        qtr["Label"] = qtr["Order_Year"].astype(str) + " " + qtr["Order_Quarter"]
        fig_qtr = px.bar(qtr, x="Label", y="Sales", color="Order_Quarter",
                         color_discrete_sequence=["#2563eb","#16a34a","#f59e0b","#dc2626"],
                         text=qtr["Sales"].apply(lambda x: f"${x/1000:.0f}K"))
        fig_qtr.update_traces(textposition="outside", textfont_size=10)
        fig_qtr.update_layout(
            height=280, showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(size=11), xaxis=dict(showgrid=False, tickangle=45),
            yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", visible=False),
            margin=dict(l=10,r=10,t=30,b=10),
        )
        st.plotly_chart(fig_qtr, use_container_width=True)

    with col_b:
        st.markdown("<div class='section'>Sales by Segment</div>", unsafe_allow_html=True)
        seg = df.groupby("Segment")["Sales"].sum().reset_index()
        fig_seg = go.Figure(go.Pie(
            labels=seg["Segment"], values=seg["Sales"], hole=0.55,
            marker_colors=["#2563eb","#16a34a","#f59e0b"],
            textinfo="label+percent", textfont_size=12,
        ))
        fig_seg.update_layout(
            height=280, paper_bgcolor="rgba(0,0,0,0)",
            font=dict(size=12), showlegend=False,
            margin=dict(l=10,r=10,t=30,b=10),
            annotations=[dict(text=fmt(total_sales), x=0.5, y=0.5,
                              font_size=14, showarrow=False)]
        )
        st.plotly_chart(fig_seg, use_container_width=True)

    # Insights
    st.markdown("<div class='section'>Smart Insights</div>", unsafe_allow_html=True)
    top_region = df.groupby("Region")["Sales"].sum().idxmax()
    top_cat    = df.groupby("Category")["Profit"].sum().idxmax()
    loss_pct   = loss_orders / len(df) * 100
    best_seg   = df.groupby("Segment")["Profit"].sum().idxmax()

    insights = [
        f"📍 <b>{top_region}</b> is the top performing region by total sales.",
        f"💰 <b>{top_cat}</b> generates the highest profit across all categories.",
        f"⚠️ <b>{loss_orders:,} orders ({loss_pct:.1f}%)</b> are loss-making — likely due to heavy discounting.",
        f"👥 <b>{best_seg}</b> is the most profitable customer segment.",
        f"🚚 Average delivery takes <b>{avg_ship_days:.1f} days</b> from order to shipment.",
    ]
    for ins in insights:
        st.markdown(f'<div class="insight">{ins}</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# TAB 2 — PRODUCTS
# ════════════════════════════════════════════════════════════
with tab2:
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("<div class='section'>Profit vs Sales by Sub-Category</div>", unsafe_allow_html=True)
        sub = df.groupby("Sub_Category").agg(
            Sales=("Sales","sum"), Profit=("Profit","sum"), Qty=("Quantity","sum")
        ).reset_index()
        sub["Margin"] = (sub["Profit"]/sub["Sales"]*100).round(1)
        sub["Color"]  = sub["Profit"].apply(lambda x: "Profitable" if x > 0 else "Loss")

        fig_scatter = px.scatter(
            sub, x="Sales", y="Profit", size="Qty", color="Color",
            color_discrete_map={"Profitable":"#16a34a","Loss":"#dc2626"},
            text="Sub_Category", size_max=50,
            hover_data={"Margin":True,"Qty":True}
        )
        fig_scatter.update_traces(textposition="top center", textfont_size=10)
        fig_scatter.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig_scatter.update_layout(
            height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(size=11), legend=dict(orientation="h", y=1.05, bgcolor="rgba(0,0,0,0)"),
            xaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
            yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)"),
            margin=dict(l=10,r=10,t=30,b=10),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_r:
        st.markdown("<div class='section'>Discount Impact on Profit</div>", unsafe_allow_html=True)
        disc = df.groupby("Discount_Band").agg(
            Avg_Profit=("Profit","mean"), Orders=("Order_ID","count")
        ).reset_index()
        order_map = ["No Discount","Low (1–20%)","Mid (21–40%)","High (41%+)"]
        disc["Discount_Band"] = pd.Categorical(disc["Discount_Band"], categories=order_map, ordered=True)
        disc = disc.sort_values("Discount_Band")
        colors = ["#16a34a" if v > 0 else "#dc2626" for v in disc["Avg_Profit"]]

        fig_disc = go.Figure(go.Bar(
            x=disc["Discount_Band"], y=disc["Avg_Profit"],
            marker_color=colors,
            text=[f"${v:.0f}" for v in disc["Avg_Profit"]],
            textposition="outside"
        ))
        fig_disc.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
        fig_disc.update_layout(
            height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(size=12), showlegend=False,
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", title="Avg Profit per Order ($)"),
            margin=dict(l=10,r=10,t=30,b=10),
        )
        st.plotly_chart(fig_disc, use_container_width=True)

    # Top & Bottom products
    st.markdown("<div class='section'>Top 10 Products by Sales</div>", unsafe_allow_html=True)
    top_prod = df.groupby("Product_Name").agg(
        Sales=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order_ID","count")
    ).reset_index().sort_values("Sales", ascending=False).head(10)
    top_prod["Margin %"] = (top_prod["Profit"]/top_prod["Sales"]*100).round(1)
    top_prod["Sales"]    = top_prod["Sales"].round(0)
    top_prod["Profit"]   = top_prod["Profit"].round(0)

    fig_top = px.bar(
        top_prod, x="Sales", y="Product_Name", orientation="h",
        color="Profit", color_continuous_scale=["#dc2626","#f59e0b","#16a34a"],
        text=top_prod["Sales"].apply(lambda x: f"${x:,.0f}")
    )
    fig_top.update_traces(textposition="outside")
    fig_top.update_layout(
        height=380, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=11), coloraxis_showscale=True,
        xaxis=dict(showgrid=False, visible=False),
        yaxis=dict(showgrid=False, categoryorder="total ascending"),
        margin=dict(l=10,r=80,t=10,b=10),
    )
    st.plotly_chart(fig_top, use_container_width=True)

    # Loss-making products table
    st.markdown("<div class='section'>⚠️ Loss-Making Orders (Top 10 by Loss)</div>", unsafe_allow_html=True)
    loss_df = df[df["Is_Profitable"]=="Loss"][
        ["Product_Name","Category","Sub_Category","Sales","Profit","Discount","Region"]
    ].sort_values("Profit").head(10).round(2)
    st.dataframe(loss_df, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════════════
# TAB 3 — CUSTOMERS & SHIPPING
# ════════════════════════════════════════════════════════════
with tab3:
    col_l, col_r = st.columns(2)

    with col_l:
        st.markdown("<div class='section'>Ship Mode Breakdown</div>", unsafe_allow_html=True)
        ship = df.groupby("Ship_Mode").agg(
            Orders=("Order_ID","count"), Avg_Days=("Days_to_Ship","mean")
        ).reset_index().sort_values("Orders", ascending=True)
        fig_ship = px.bar(
            ship, x="Orders", y="Ship_Mode", orientation="h",
            color="Avg_Days", color_continuous_scale=["#16a34a","#f59e0b","#dc2626"],
            text="Orders"
        )
        fig_ship.update_traces(textposition="outside")
        fig_ship.update_layout(
            height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(size=12), coloraxis_colorbar=dict(title="Avg Days"),
            xaxis=dict(showgrid=False, visible=False),
            yaxis=dict(showgrid=False),
            margin=dict(l=10,r=10,t=10,b=10),
        )
        st.plotly_chart(fig_ship, use_container_width=True)

    with col_r:
        st.markdown("<div class='section'>Days to Ship Distribution</div>", unsafe_allow_html=True)
        fig_days = px.histogram(
            df, x="Days_to_Ship", nbins=15,
            color_discrete_sequence=["#6366f1"]
        )
        fig_days.update_layout(
            height=280, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(size=12), showlegend=False,
            xaxis=dict(showgrid=False, title="Days to Ship"),
            yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", title="Orders"),
            margin=dict(l=10,r=10,t=10,b=10),
            bargap=0.05,
        )
        st.plotly_chart(fig_days, use_container_width=True)

    # Top customers
    st.markdown("<div class='section'>Top 15 Customers by Sales</div>", unsafe_allow_html=True)
    top_cust = df.groupby("Customer_Name").agg(
        Sales=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order_ID","count")
    ).reset_index().sort_values("Sales", ascending=False).head(15)
    top_cust["Margin %"] = (top_cust["Profit"]/top_cust["Sales"]*100).round(1)

    fig_cust = px.bar(
        top_cust, x="Customer_Name", y="Sales",
        color="Profit", color_continuous_scale=["#dc2626","#f59e0b","#16a34a"],
        text=top_cust["Sales"].apply(lambda x: f"${x:,.0f}")
    )
    fig_cust.update_traces(textposition="outside", textfont_size=10)
    fig_cust.update_layout(
        height=320, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(size=11),
        xaxis=dict(showgrid=False, tickangle=45),
        yaxis=dict(showgrid=True, gridcolor="rgba(128,128,128,0.15)", visible=False),
        margin=dict(l=10,r=10,t=10,b=10),
    )
    st.plotly_chart(fig_cust, use_container_width=True)

    # State-level table
    st.markdown("<div class='section'>Sales by State (Top 10)</div>", unsafe_allow_html=True)
    state_df = df.groupby("State").agg(
        Sales=("Sales","sum"), Profit=("Profit","sum"), Orders=("Order_ID","count")
    ).reset_index().sort_values("Sales", ascending=False).head(10)
    state_df["Margin %"] = (state_df["Profit"]/state_df["Sales"]*100).round(1)
    state_df["Sales"]    = state_df["Sales"].round(0)
    state_df["Profit"]   = state_df["Profit"].round(0)
    st.dataframe(state_df, use_container_width=True, hide_index=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align:center;color:#888;font-size:12px'>"
    "Superstore Sales Dashboard · Built with Python & Streamlit · "
    "Data: Kaggle Superstore Dataset 2014–2017"
    "</div>",
    unsafe_allow_html=True
)
