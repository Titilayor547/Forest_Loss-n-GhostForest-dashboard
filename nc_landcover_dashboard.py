# ------------------------------------------------------------
import streamlit as st
import numpy as np
import pandas as pd
import rasterio
import leafmap.foliumap as leafmap
import plotly.express as px
import plotly.graph_objects as go
import tempfile

# NOTE: Ensure sankey_utils.py is in your directory and create_sankey is defined.
from sankey_utils import create_sankey 

# ---------------------------
# DASHBOARD CONFIG
# ---------------------------
st.set_page_config(
    page_title="Landcover Change Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown("<h1 style='text-align: center; color: black;'>🌍 Landcover Change Dashboard (1985–2021)</h1>", unsafe_allow_html=True)
st.markdown("""
This interactive dashboard for the North Carolina Eastern Coast Plain**.
""")

# ---------------------------
# DEFINE CLASSES and LEGEND
# ---------------------------
classes = {
    0: "Marsh",
    1: "Shrub",
    2: "Ghost Forest",
    3: "Forest",
    4: "Cultivated Land",
    5: "Water"
}

# 1. Dictionary for Leafmap Raster (Numerical ID to Hex, including -1)
# This ensures -1 (NoData) is correctly displayed as white/transparent on the map
raster_color_map = {
    -1: "#FFFFFF00",  # Use transparent white for NoData (-1)
    0: "#6495ED",     # Marsh
    1: "#32CD32",     # Shrub
    2: "#8B0000",     # Ghost Forest
    3: "#006400",     # Forest
    4: "#DAA520",     # Cultivated Land
    5: "#00008B",     # Water
}

# 2. Dictionary for Plotly/Streamlit Legend (Class Name to Hex, excluding -1)
# This is used for your pie charts, Sankey diagram, and the map legend text.
legend_dict = {
    "Marsh": "#6495ED",
    "Shrub": "#32CD32",
    "Ghost Forest": "#8B0000",
    "Forest": "#006400",
    "Cultivated Land": "#DAA520",
    "Water": "#00008B",
}
cmap_colors = list(legend_dict.values()) # Colormap list for Leafmap
raster_color_map = list(raster_color_map.values())

# ---------------------------
# LOAD RASTERS
# ---------------------------
#path_1993 = "c:\\Users\\tttajude\\PHDresearch\\GhostForest\\Processed_Image\\pred_Land1985a.tif"
#path_2000 = "c:\\Users\\tttajude\\PHDresearch\\GhostForest\\Processed_Image\\pred_Land2021check.tif"

def download_tif(url, filename):
    r = requests.get(url, stream=True)
    r.raise_for_status()
    with open(filename, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

# Download the rasters first
download_tif("https://raw.githubusercontent.com/Titilayor547/Forest_Loss-n-GhostForest-dashboard/main/pred_Land1985a.tif",
             "pred_Land1985a.tif")
download_tif("https://raw.githubusercontent.com/Titilayor547/Forest_Loss-n-GhostForest-dashboard/main/pred_Land2021a.tif",
             "pred_Land2021a.tif")

df_1993 = pd.DataFrame({'Landcover': [], 'Area_Pixels': []})
df_2000 = pd.DataFrame({'Landcover': [], 'Area_Pixels': []})
df_change = pd.DataFrame({'From_ID': [], 'To_ID': [], 'Area_Pixels': []})
array_1993 = None
array_2000 = None

try:
    # --- Load 1993 Data ---
    with rasterio.open("pred_Land1985a.tif") as src:
        array_1993 = src.read(1)
        values_1993, counts_1993 = np.unique(array_1993, return_counts=True)
        valid_indices_1993 = values_1993 != -1
        df_1993 = pd.DataFrame({
            'Class_ID': values_1993[valid_indices_1993],
            'Area_Pixels': counts_1993[valid_indices_1993]
        })
        df_1993['Landcover'] = df_1993['Class_ID'].map(classes)

    # --- Load 2000 Data ---
    with rasterio.open("pred_Land2021a.tif") as src:
        array_2000 = src.read(1)
        values_2000, counts_2000 = np.unique(array_2000, return_counts=True)
        valid_indices_2000 = values_2000 != -1
        df_2000 = pd.DataFrame({
            'Class_ID': values_2000[valid_indices_2000],
            'Area_Pixels': counts_2000[valid_indices_2000]
        })
        df_2000['Landcover'] = df_2000['Class_ID'].map(classes)
        
    # --- Calculate Change Matrix for Sankey ---
    if array_1993 is not None and array_2000 is not None:
        if array_1993.shape == array_2000.shape:
            df_change_raw = pd.DataFrame({
                'From_ID': array_1993.flatten(),
                'To_ID': array_2000.flatten()
            })
            # Filter out nodata (assuming -1 is nodata)
            df_change_filtered = df_change_raw[
                (df_change_raw['From_ID'] != -1) & (df_change_raw['To_ID'] != -1)
            ]
            df_change = df_change_filtered.groupby(['From_ID', 'To_ID']).size().reset_index(name='Area_Pixels')
            df_change['From_Landcover'] = df_change['From_ID'].map(classes)
            df_change['To_Landcover'] = df_change['To_ID'].map(classes)
        else:
            st.warning("Raster arrays have different shapes. Cannot calculate change matrix.")
            
except Exception as e:
    st.error(f"Error loading raster files: {e}. Please check file paths and ensure required files are present.")


# --- Layout based on the image: Two columns for Map/Chart, one row for Sankey ---
col1_map, col2_chart = st.columns([6, 4]) 

# =========================================================
# 1. MAP SELECTION & COMPARISON (Left Panel)
# =========================================================
with col1_map:
    st.markdown("### Maps such that I can select either 1993 or 2000")
    
    # Selection for Map and Chart
    selected_year = st.radio(
        "Select Map View:",
        ('1985', '2021', #'Compare (Slider)'
         ),
        index=0, # if compare slider, it will be 2 
        horizontal=True,
        key='map_selector'
    )
    
    m = leafmap.Map(
        center=(35.5, -75.5), # Example center
        zoom=9,
        tiles="OpenStreetMap"
    )

    if array_1993 is not None:
        m.add_raster(path_1993, layer_name="1993 Landcover", colormap=raster_color_map, nodata=-1, visible=(selected_year=='1993'))
    
    if array_2000 is not None:
        m.add_raster(path_2000, layer_name="2000 Landcover", colormap=raster_color_map, nodata=-1, visible=(selected_year=='2000'))
    
    # Splitter for comparison view
    #if selected_year == 'Compare (Slider)' and array_1993 is not None and array_2000 is not None:
    #    # We need to re-add layers to the map object for the splitter to work best
    #    m_splitter = leafmap.Map(center=(35.5, -75.5), zoom=9, tiles="OpenStreetMap")
    #    m_splitter.add_raster(path_1993, layer_name="1993 Landcover", colormap=cmap_colors, nodata=-1, visible=True)
    #    m_splitter.add_raster(path_2000, layer_name="2000 Landcover", colormap=cmap_colors, nodata=-1, visible=True)
    #    m_splitter.add_splitter(left_layer='1993 Landcover', right_layer='2000 Landcover')
    #    m_splitter.add_legend(title="Landcover Classes", legend_dict=legend_dict)
    #    st_map = m_splitter.to_streamlit(height=450)
    #else:
    
    # Single map view
    m.add_legend(title="Landcover Classes", legend_dict=legend_dict)
    st_map = m.to_streamlit(height=450)


# =========================================================
# 2. DYNAMIC PIE CHART (Right Panel)
# =========================================================
with col2_chart:
    st.markdown("### For each selected map, here the pie chart of class composition is displayed automatically.")
    
    # Determine the DataFrame to use for the pie chart
    year_to_chart = selected_year if selected_year != 'Compare (Slider)' else '1993'
    
    if year_to_chart == '1985':
        df_pie = df_1993
        chart_title = "1985 Landcover Composition"
    elif year_to_chart == '2021':
        df_pie = df_2000
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
        sankey_fig = create_sankey(array_1993, array_2000) 
        st.plotly_chart(sankey_fig, use_container_width=True)
    except Exception as e:
        st.error(f"Could not generate Sankey diagram. Please check your `create_sankey` function. Error: {e}")
else:
    st.warning("Change matrix data (df_change) is empty. Cannot generate the Sankey diagram.")

st.markdown("---")
st.markdown("Built with ❤️ using [Streamlit](https://streamlit.io) and [Leafmap](https://leafmap.org).")
