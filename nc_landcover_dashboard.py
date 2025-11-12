# ------------------------------------------------------------
import streamlit as st
import leafmap.foliumap as leafmap

# ---------------------------
# DASHBOARD CONFIG
# ---------------------------
st.set_page_config(
    page_title="Landcover Change Dashboard",
    layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown("<h1 style='text-align: center; color: black;'>🌍 Landcover Change Dashboard (1985–2021)</h1>", unsafe_allow_html=True)

# ---------------------------
# DEFINE RASTER COLORS
# ---------------------------
raster_color_map = {
    -1: "#FFFFFF00",  # NoData transparent
    0: "#6495ED",     # Marsh
    1: "#32CD32",     # Shrub
    2: "#8B0000",     # Ghost Forest
    3: "#006400",     # Forest
    4: "#DAA520",     # Cultivated Land
    5: "#00008B",     # Water
}

# ---------------------------
# RASTER FILES (GitHub Raw URLs)
# ---------------------------
url_1985 = "https://raw.githubusercontent.com/Titilayor547/Forest_Loss-n-GhostForest-dashboard/main/pred_Land1985a.tif"
url_2021 = "https://raw.githubusercontent.com/Titilayor547/Forest_Loss-n-GhostForest-dashboard/main/pred_Land2021a.tif"

# ---------------------------
# MAP SELECTION
# ---------------------------
selected_year = st.radio(
    "Select Map View:",
    ('1985', '2021'),
    index=0,
    horizontal=True
)

m = leafmap.Map(center=(35.5, -75.5), zoom=9, tiles="OpenStreetMap")

if selected_year == '1985':
    m.add_raster(url_1985, layer_name="1985 Landcover", colormap=raster_color_map, nodata=-1)
else:
    m.add_raster(url_2021, layer_name="2021 Landcover", colormap=raster_color_map, nodata=-1)

m.to_streamlit(height=500)


st.markdown("---")
st.markdown("Built with ❤️ using [Streamlit](https://streamlit.io) and [Leafmap](https://leafmap.org).")
