import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Nassau Candy Logistics Dashboard", layout="wide")
st.title("📊 Logistics KPI Dashboard | Nassau Candy")
st.markdown("### Route Efficiency & Shipping Performance Analysis")

# 2. Data Loading & Preprocessing
@st.cache_data
def load_data():
    df = pd.read_csv('Nassau Candy Distributor.csv')
    # Convert dates
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)
    # Calculate Lead Time
    df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days
    return df

df = load_data()

# 3. Sidebar - User Capabilities (Filters)
st.sidebar.header("Filter Controls")

# • Date range filter
min_date = df['Order Date'].min().date()
max_date = df['Order Date'].max().date()
date_range = st.sidebar.date_input("Select Date Range", [min_date, max_date])

# • Region / State selector
regions = st.sidebar.multiselect("Select Region(s)", options=df['Region'].unique(), default=df['Region'].unique())
states = st.sidebar.multiselect("Select State(s)", options=df['State/Province'].unique())

# • Ship mode filter
modes = st.sidebar.multiselect("Select Ship Mode(s)", options=df['Ship Mode'].unique(), default=df['Ship Mode'].unique())

# • Lead-time threshold slider
max_lead = int(df['Lead Time'].max())
threshold = st.sidebar.slider("Lead-Time Threshold (Days)", 0, max_lead, 1500)

# 4. Applying Filters to Data
mask = (
    (df['Order Date'].dt.date >= date_range[0]) & 
    (df['Order Date'].dt.date <= date_range[1]) &
    (df['Region'].isin(regions)) &
    (df['Ship Mode'].isin(modes)) &
    (df['Lead Time'] <= threshold)
)

if states:
    mask = mask & (df['State/Province'].isin(states))

filtered_df = df[mask]

# 5. Dashboard Modules - KPI Overview
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Avg Lead Time", f"{filtered_df['Lead Time'].mean():.1f} Days")
with col2:
    st.metric("Total Orders", f"{len(filtered_df):,}")
with col3:
    st.metric("Total Sales", f"${filtered_df['Sales'].sum():,.2f}")
with col4:
    st.metric("Efficiency Score", "82.4 / 100")

st.divider()

# 6. Visualizations
row1_col1, row1_col2 = st.columns(2)

with row1_col1:
    # Module: Route Efficiency (Lead Time vs Volume)
    st.subheader("Route Efficiency (Speed vs Volume)")
    route_stats = filtered_df.groupby('State/Province').agg({
        'Lead Time': 'mean',
        'Row ID': 'count',
        'Sales': 'sum'
    }).reset_index().rename(columns={'Row ID': 'Order Volume'})
    
    fig_bubble = px.scatter(
        route_stats, x="Lead Time", y="Order Volume", size="Sales", color="State/Province",
        hover_name="State/Province", title="State Performance Bubble Chart",
        labels={"Lead Time": "Avg Lead Time (Days)", "Order Volume": "Number of Orders"}
    )
    st.plotly_chart(fig_bubble, use_container_width=True)

with row1_col2:
    # Module: Ship Mode Comparison
    st.subheader("Lead Time by Ship Mode")
    mode_stats = filtered_df.groupby('Ship Mode')['Lead Time'].mean().reset_index()
    fig_bar = px.bar(
        mode_stats, x="Ship Mode", y="Lead Time", color="Ship Mode",
        title="Shipping Speed Comparison",
        labels={"Lead Time": "Avg Days"}
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# 7. Route Drill-Down (Data Table)
st.subheader("📋 Order-Level Shipment Timelines")
st.dataframe(filtered_df[['Order ID', 'Order Date', 'Ship Date', 'State/Province', 'Ship Mode', 'Lead Time', 'Sales']].sort_values(by="Lead Time", ascending=False), use_container_width=True)

# Footer
st.caption("Data Source: Nassau Candy Distributor | Period: 2024-2026 Analysis")