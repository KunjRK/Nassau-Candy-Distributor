import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. Page Configuration
st.set_page_config(page_title="Nassau Candy Logistics Dashboard", layout="wide")
st.title("📊 Logistics KPI Dashboard | Nassau Candy")

# 2. Data Loading & Factory Coordinates
@st.cache_data
def load_data():
    df = pd.read_csv('Nassau Candy Distributor.csv')
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
    df['Ship Date'] = pd.to_datetime(df['Ship Date'], dayfirst=True)
    df['Lead Time'] = (df['Ship Date'] - df['Order Date']).dt.days
    return df

# Factory Data
factories = pd.DataFrame([
    {"Factory": "Lot's O' Nuts", "lat": 32.881893, "lon": -111.768036},
    {"Factory": "Wicked Choccy's", "lat": 32.076176, "lon": -81.088371},
    {"Factory": "Sugar Shack", "lat": 48.11914, "lon": -96.18115},
    {"Factory": "Secret Factory", "lat": 41.446333, "lon": -90.565487},
    {"Factory": "The Other Factory", "lat": 35.1175, "lon": -89.971107}
])

df = load_data()

# 3. Sidebar Filters
st.sidebar.header("Filter Controls")
date_range = st.sidebar.date_input("Date Range", [df['Order Date'].min(), df['Order Date'].max()])
regions = st.sidebar.multiselect("Regions", df['Region'].unique(), default=df['Region'].unique())
modes = st.sidebar.multiselect("Ship Modes", df['Ship Mode'].unique(), default=df['Ship Mode'].unique())
threshold = st.sidebar.slider("Lead-Time Threshold (Days)", 0, 2000, 1500)

# Filter Logic
mask = (df['Order Date'].dt.date >= date_range[0]) & (df['Order Date'].dt.date <= date_range[1]) & \
       (df['Region'].isin(regions)) & (df['Ship Mode'].isin(modes)) & (df['Lead Time'] <= threshold)
filtered_df = df[mask]

# 4. KPI Header
c1, c2, c3 = st.columns(3)
c1.metric("Avg Lead Time", f"{filtered_df['Lead Time'].mean():.1f} Days")
c2.metric("Orders Processed", f"{len(filtered_df):,}")
c3.metric("Factory Network", f"{len(factories)} Hubs")

st.divider()

# 5. Module: Geographic Shipping Map (US Heatmap + Factory Locations)
st.subheader("🌎 Geographic Shipping Map & Bottleneck Visualization")

# Aggregate Lead Time by State for Heatmap
state_map_df = filtered_df.groupby('State/Province')['Lead Time'].mean().reset_index()

# Map Implementation
fig_map = px.choropleth(
    state_map_df,
    locations='State/Province',
    locationmode="USA-states",
    color='Lead Time',
    scope="usa",
    color_continuous_scale="Reds",
    title="Shipping Efficiency Heatmap (Darker = Slower)",
    labels={'Lead Time': 'Avg Days'}
)

# Add Factory Markers
fig_map.add_trace(go.Scattergeo(
    lat=factories['lat'],
    lon=factories['lon'],
    text=factories['Factory'],
    mode='markers+text',
    marker=dict(size=12, color='blue', symbol='star'),
    name="Factories",
    textposition="top center"
))

st.plotly_chart(fig_map, use_container_width=True)

# 6. Secondary Modules (Efficiency & Ship Mode)
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    st.subheader("Route Efficiency")
    route_stats = filtered_df.groupby('State/Province').size().reset_index(name='Volume')
    fig_bar = px.bar(route_stats.sort_values('Volume', ascending=False).head(10), 
                     x='State/Province', y='Volume', title="Top 10 High-Volume Routes")
    st.plotly_chart(fig_bar, use_container_width=True)

with row2_col2:
    st.subheader("Lead Time by Ship Mode")
    mode_avg = filtered_df.groupby('Ship Mode')['Lead Time'].mean().reset_index()
    fig_mode = px.pie(mode_avg, values='Lead Time', names='Ship Mode', title="Lead Time Distribution")
    st.plotly_chart(fig_mode, use_container_width=True)

# 7. Order Drill-Down
st.subheader("📋 Order-level shipment timelines")
st.dataframe(filtered_df[['Order ID', 'Order Date', 'State/Province', 'Lead Time', 'Ship Mode']].tail(100))