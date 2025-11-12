import streamlit as st
import rasterio
import numpy as np
import pandas as pd
import plotly.express as px
import leafmap.foliumap as leafmap
from io import BytesIO
from PIL import Image

# ---------------------------
# DASHBOARD CONFIG
# ---------------------------
st.set_page_config(
    page_title="Landcover Change Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🌍 Landcover Change Dashboard (1993–2000)")
st.markdown("""
This interactive dashboard lets you visualize and compare landcover between **1993** and **2000**.  
Use the maps below to explore the rasters, and scroll down for charts and statistics.
""")

# ---------------------------
# LOAD RASTERS
# ---------------------------
path_1993 = "c:\\Users\\tttajude\\PHDresearch\\GhostForest\\Processed_Image\\pred_Land1985a.tif"
path_2000 = "c:\\Users\\tttajude\\PHDresearch\\GhostForest\\Processed_Image\\pred_Land2010a.tif"

@st.cache_data
def load_raster(path):
    with rasterio.open(path) as src:
        array = src.read(1)
        transform = src.transform
        meta = src.meta
    return array, transform, meta

lc93, transform, meta = load_raster(path_1993)
lc00, _, _ = load_raster(path_2000)

# ---------------------------
# DEFINE CLASSES
# ---------------------------
classes = {
    #-1: "No Data",
    0: "Marsh",
    1: "Shrub",
    2: "Ghost Forest",
    3: "Forest",
    4: "Cultivated Land",
    5: "Water"
}

# ---------------------------
# COUNT PIXELS
# ---------------------------
def count_classes(array, class_map):
    vals, counts = np.unique(array, return_counts=True)
    df = pd.DataFrame({"class_id": vals, "count": counts})
    df["class_name"] = df["class_id"].map(class_map)
    df = df.dropna(subset=["class_name"])
    return df

df93 = count_classes(lc93, classes)
df00 = count_classes(lc00, classes)

# Combine and calculate change
merged = pd.merge(df93, df00, on="class_id", suffixes=("_1993", "_2000"))
merged["class_name"] = merged["class_name_1993"].fillna(merged["class_name_2000"])
merged["change"] = merged["count_2000"] - merged["count_1993"]

st.title("Landcover Change Dashboard 🌿")

# --- Your pixel comparison chart goes here ---
# st.plotly_chart(fig)




# ---------------------------
# MAP VISUALIZATION
# ---------------------------
col1, col2 = st.columns(2)

# ---------------------------
# Define legend for classes
# ---------------------------
legend_dict = {
    #"Class 0": "#ffffff",          # white
    "Marsh": "#8dd3c7",           # light blue from Set3
    "Shrub": "#ffffb3",           # light yellow
    "Ghost Forest": "#bebada",    # lavender
    "Forest": "#fb8072",          # salmon
    "Cultivated": "#80b1d3",      # blue
    "Water": "#fdb462",           # orange
}

# ---------------------------
# 1993 Landcover
# ---------------------------
with col1:
    st.subheader("Landcover 1993")
    m1 = leafmap.Map()
    m1.add_raster(path_1993, layer_name="1993 Landcover", colormap="Set3", nodata=-1)
    m1.add_legend(title="Landcover 1993", legend_dict=legend_dict)
    m1.to_streamlit(height=450)

# ---------------------------
# 2000 Landcover
# ---------------------------
with col2:
    st.subheader("Landcover 2000")
    m2 = leafmap.Map()
    m2.add_raster(path_2000, layer_name="2000 Landcover", colormap="Set3", nodata=-1)
    m2.add_legend(title="Landcover 2000", legend_dict=legend_dict)
    m2.to_streamlit(height=450)


# Optional: synchronize maps
try:
    leafmap.link_maps(m1, m2)
except Exception:
    st.warning("Map synchronization not supported in this mode.")

# ---------------------------
# BAR CHART COMPARISON
# ---------------------------
st.subheader("📊 Landcover Pixel Comparison")

fig = px.bar(
    merged,
    x="class_name",
    y=["count_1993", "count_2000"],
    barmode="group",
    title="Pixel Count per Landcover Class",
    labels={"value": "Pixel Count", "class_name": "Landcover Class"},
)
st.plotly_chart(fig, use_container_width=True)

# ---------------------------
# TRANSITION MATRIX
# ---------------------------
st.subheader("🔁 Landcover Transition Matrix (1993 → 2000)")

# Compute transition
transition = pd.crosstab(lc93.ravel(), lc00.ravel())
transition.index = [classes.get(i, i) for i in transition.index]
transition.columns = [classes.get(i, i) for i in transition.columns]
st.dataframe(transition)

# ---------------------------
# DOWNLOAD SUMMARY
# ---------------------------
st.subheader("📥 Download Summary Data")

csv_buffer = BytesIO()
merged.to_csv(csv_buffer, index=False)
st.download_button(
    label="Download Comparison Table (CSV)",
    data=csv_buffer.getvalue(),
    file_name="landcover_summary_1993_2000.csv",
    mime="text/csv"
)

st.markdown("---")
st.markdown("Built with ❤️ using [Streamlit](https://streamlit.io) and [Leafmap](https://leafmap.org).")
