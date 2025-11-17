# ------------------------------------------------------------
import streamlit as st
import numpy as np
import pandas as pd
import geopandas as gpd
import leafmap.foliumap as leafmap
import plotly.graph_objects as go
import plotly.express as px

from sankey_utils import create_sankey 

# ------------------------------------------------------------
# DASHBOARD CONFIG
# ------------------------------------------------------------
st.set_page_config(
    page_title="Landcover Change Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("<h1 style='text-align: center; color: black;'>🌍 Landcover Change Dashboard (1985–2021)</h1>", unsafe_allow_html=True)
st.markdown("""
This interactive dashboard visualizes landcover change in the North Carolina Eastern Coastal Plain.
""")

# ------------------------------------------------------------
# LANDCOVER CLASSES AND COLOR MAPS
# ------------------------------------------------------------

classes = {
    0: "Marsh",
    1: "Shrub",
    2: "Ghost Forest",
    3: "Forest",
    4: "Cultivated Land",
    5: "Water"
}

# ID → HEX color (for polygons)
color_map = {
    0: "#6495ED",     # Marsh
    1: "#32CD32",     # Shrub
    2: "#8B0000",     # Ghost Forest
    3: "#006400",     # Forest
    4: "#DAA520",     # Cultivated Land
    5: "#00008B",     # Water
}

# Class Name → HEX color (for legend, charts)
legend_dict = {classes[i]: color_map[i] for i in classes}

# Optional: color list for charts
cmap_colors = list(legend_dict.values())

# ------------------------------------------------------------
# LOAD SHAPEFILES
# ------------------------------------------------------------
path_1985 = r"landcover_polygon/pred_seg1985_polygons_dissolved.shp"
path_2021 = r"landcover_polygon/pred_seg2021_polygons_dissolved.shp"

gdf_1985 = gpd.read_file(path_1985)
gdf_2021 = gpd.read_file(path_2021)
print(gdf_2021)
#gdf_1985 = gdf_1985.to_crs(epsg=4326)
#gdf_2021 = gdf_2021.to_crs(epsg=4326)

# Add color column based on class_code
gdf_1985["class_code"] = gdf_1985["class_code"].astype(int)
gdf_2021["class_code"] = gdf_2021["class_code"].astype(int)
gdf_1985["colorr"] = gdf_1985["class_code"].map(color_map)
gdf_2021["colorr"] = gdf_2021["class_code"].map(color_map)
print(gdf_1985)
# ------------------------------------------------------------
# LOAD TABLES
# ------------------------------------------------------------
df_1985 = pd.read_csv(r"table/df_1985.csv")
df_2021 = pd.read_csv(r"table/df_2021.csv")
df_change = pd.read_csv(r"table/df_change.csv")
sankey_path = r"table/sankey_data.csv"

# ------------------------------------------------------------
# LAYOUT: MAP (LEFT) — CHARTS (RIGHT)
# ------------------------------------------------------------
col1_map, col2_chart = st.columns([6, 4])

with col1_map:
    st.markdown("### Landcover Map Viewer (Select Year)")

    selected_year = st.radio(
        "Select Map View:",
        ('1985', '2021'),
        index=0,
        horizontal=True,
        key='map_selector'
    )

    m = leafmap.Map(
        center=(35.5, -75.5),
        zoom=9,
        tiles="OpenStreetMap"
    )
#streamlit run app.py
    # Add 1985 layer
    m.add_gdf(
        gdf_1985,
        layer_name="1985 Landcover",
        fill_color="colorr", # Uses the 'color' column for polygon fill
            style={
                "weight": 0,           # Thickness of the stroke (outline) set to 0
                "fill": True,          # Ensures the polygon fill remains
                "fillOpacity": 0.95    # Sets the fill transparency
            },
        visible=(selected_year == '1985'),
    )

    # Add 2021 layer
    m.add_gdf(
        gdf_2021,
        layer_name="2021 Landcover",
        fill_color="colorr",
        style={"weight": 0, "fill": True, "fillOpacity": 1},
        visible=(selected_year == '2021'),
    )
    # Add legend
    m.add_legend(title="Landcover Classes", legend_dict=legend_dict)
    st_map = m.to_streamlit(height=500)


# =========================================================
# 2. DYNAMIC PIE CHART (Right Panel)
# =========================================================
with col2_chart:
    st.markdown("### For each selected map, here the pie chart of class composition is displayed automatically.")
    # Determine the DataFrame to use for the pie chart
    year_to_chart = selected_year if selected_year != 'Compare (Slider)' else '1993'
    
    if year_to_chart == '1985':
        df_pie = df_1985
        chart_title = "1985 Landcover Composition"
    elif year_to_chart == '2021':
        df_pie = df_2021
        chart_title = "2021 Landcover Composition"
    
    # Generate the Pie Chart
    if not df_pie.empty:
        color_map_pie = {name: color for name, color in legend_dict.items() if name in df_pie['Landcover'].unique()}
        fig_pie = px.pie(
            df_pie,
            values='Area_Pixels',
            names='Landcover',
            title=chart_title,
            color='Landcover',
            color_discrete_map=color_map_pie 
        )
        fig_pie.update_traces(textposition='inside', textinfo='percent+label')
        fig_pie.update_layout(height=450)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("Landcover data is not available to generate the pie chart.")

# ---------------------------
st.markdown("---")
# ---------------------------


# =========================================================
# 3. SANKEY DIAGRAM (Full Width Panel)
# =========================================================
st.markdown("## The Sankey diagram showing the flow of change over time")

# Generate Sankey diagram
if not df_change.empty:
    try:
        # Pass the calculated change DataFrame to your function
        # NOTE: Your create_sankey function must be able to process df_change
        sankey_fig = create_sankey(sankey_path) 
        st.plotly_chart(sankey_fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not generate Sankey diagram. Please check your `create_sankey` function. Error: {e}")
else:
    st.warning("Change matrix data (df_change) is empty. Cannot generate the Sankey diagram.")

st.markdown("---")
st.markdown("Built with ❤️ using [Streamlit](https://streamlit.io) and [Leafmap](https://leafmap.org).")
