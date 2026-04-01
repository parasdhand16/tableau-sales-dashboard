import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import warnings
import pydeck as pdk

warnings.filterwarnings('ignore')

st.set_page_config(page_title="Global Sales Command Center", page_icon="🌎", layout="wide")

# =======================================================
# 1. GENERATE SYNTHETIC GLOBAL DATASET WITH LAT/LONG
# =======================================================
@st.cache_data
def generate_sales():
    np.random.seed(42)
    n_records = 20000
    
    cities = {
        'New York': (40.7128, -74.0060, 'USA'),
        'London': (51.5074, -0.1278, 'UK'),
        'Tokyo': (35.6895, 139.6917, 'Japan'),
        'Sydney': (-33.8688, 151.2093, 'Australia'),
        'San Francisco': (37.7749, -122.4194, 'USA'),
        'Berlin': (52.5200, 13.4050, 'Germany'),
        'Singapore': (1.3521, 103.8198, 'Singapore')
    }
    
    city_names = list(cities.keys())
    sampled_cities = np.random.choice(city_names, size=n_records)
    
    lats = [cities[c][0] + np.random.normal(0, 0.5) for c in sampled_cities] # Slight radius variation
    longs = [cities[c][1] + np.random.normal(0, 0.5) for c in sampled_cities]
    countries = [cities[c][2] for c in sampled_cities]
    
    categories = ['Electronics', 'Home Goods', 'Apparel', 'Automotive', 'Software']
    prices = {'Electronics': 800, 'Home Goods': 150, 'Apparel': 50, 'Automotive': 4000, 'Software': 200}
    
    sampled_cats = np.random.choice(categories, size=n_records)
    base_cost = np.array([prices[c] for c in sampled_cats])
    actual_sales = base_cost * np.random.normal(1, 0.2, size=n_records)
    
    dates = pd.date_range(start="2023-01-01", end="2024-01-01", freq='h')
    sampled_dates = np.random.choice(dates, size=n_records)
    
    df = pd.DataFrame({
        'Date': sampled_dates,
        'City': sampled_cities,
        'Country': countries,
        'lat': lats,
        'lon': longs,
        'Category': sampled_cats,
        'Revenue': actual_sales.round(2)
    })
    
    # Introduce regional underperformance to be "caught"
    df.loc[(df['City'] == 'London') & (df['Category'] == 'Electronics'), 'Revenue'] *= 0.4
    
    return df

df = generate_sales()

st.title("🌎 Global Sales Command & Supply Chain Monitor")
st.markdown("Business Intelligence application displaying real-time geographic revenue mapping, cross-category performance tables, and predictive supply chain bottlenecks.")

# =======================================================
# 2. EXECUTIVE FILTERS (SIDEBAR)
# =======================================================
st.sidebar.header("🕹️ Global Controls")
selected_cats = st.sidebar.multiselect("Filter by Product Category", options=df['Category'].unique(), default=df['Category'].unique())

filtered = df[df['Category'].isin(selected_cats)]

# =======================================================
# 3. STORYLINE TABS
# =======================================================
tab1, tab2, tab3 = st.tabs(["🗺️ Global Heatmap", "📈 Category Matrix", "⚠️ Supply Chain Outliers"])

# --- TAB 1: GEOGRAPHIC HEATMAP ---
with tab1:
    st.header("Executive Geographic Performance")
    col1, col2, col3 = st.columns(3)
    col1.metric("Global Revenue Selected", f"${filtered['Revenue'].sum():,.0f}")
    col2.metric("Total Transactions", f"{len(filtered):,}")
    top_country = filtered.groupby('Country')['Revenue'].sum().idxmax()
    col3.metric("Leading Regional Market", top_country)
    
    st.markdown("Interactive PyDeck visualization plotting thousands of global transactions instantly. Red indicates high-density multi-category hotspots.")
    
    view_state = pdk.ViewState(latitude=30, longitude=10, zoom=1, pitch=30)
    layer = pdk.Layer(
        "HexagonLayer",
        data=filtered,
        get_position="[lon, lat]",
        radius=40000,
        elevation_scale=5000,
        elevation_range=[0, 3000],
        extrapolate=True,
        pickable=True,
        get_weight="Revenue"
    )
    
    st.pydeck_chart(pdk.Deck(
        map_style="mapbox://styles/mapbox/dark-v10",
        initial_view_state=view_state,
        layers=[layer],
        tooltip={"text": "Geographic Revenue Hotspot\nTransactions: {count}"}
    ))

# --- TAB 2: CATEGORY MATRIX ---
with tab2:
    st.header("Product Category Breakdown")
    
    c_df = filtered.groupby('Category')['Revenue'].agg(['sum', 'count', 'mean']).reset_index()
    c_df.rename(columns={'sum': 'Total Revenue', 'count': 'Units Moved', 'mean': 'Average Trans. Value'}, inplace=True)
    c_df = c_df.sort_values(by='Total Revenue', ascending=False)
    
    st.dataframe(c_df.style.format({'Total Revenue': '${:,.0f}', 'Average Trans. Value': '${:,.2f}'}), use_container_width=True)
    
    fig_bar = px.bar(c_df, x='Category', y='Total Revenue', color='Category', title="Absolute Revenue by Product Category Ecosystem")
    st.plotly_chart(fig_bar, use_container_width=True)

# --- TAB 3: DRILL-DOWN ALERTING ---
with tab3:
    st.header("Supply Chain Exception Monitoring")
    st.markdown("Automated algorithmic detection of regionally underperforming product categories across the globe.")
    
    matrix = pd.pivot_table(filtered, values='Revenue', index='City', columns='Category', aggfunc=np.mean).fillna(0)
    
    fig_heat = px.imshow(matrix, text_auto='.0f', color_continuous_scale='rdbu', aspect="auto", 
                        labels=dict(x="Product Line", y="Distribution Hub", color="Avg Rev. ($)"),
                        title="Distribution Hub Matrix (Blue = Strong, Red = Flagged Danger Zone)")
    st.plotly_chart(fig_heat, use_container_width=True)
    
    st.error("🚨 ALERT: Analysis indicates systematic underperformance (price erosion or severe discounting) of 'Electronics' originating from the London Hub.")

st.markdown("---")
st.markdown("Built by **Paras Dhand** — Advanced Analytics Portfolio")
