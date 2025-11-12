# sankey_utils.py
import numpy as np
import pandas as pd
import plotly.graph_objects as go

def create_sankey(lc93, lc00, class_dict):
    """
    Create a Plotly Sankey diagram from two raster arrays.
    
    Parameters:
    - lc93: np.array, raster for 1993
    - lc00: np.array, raster for 2000
    - class_dict: dict, mapping class IDs to names
    
    Returns:
    - fig: Plotly Figure object (Sankey diagram)
    """
    # Flatten and mask nodata
    lc93_flat = lc93.ravel()
    lc00_flat = lc00.ravel()
    mask = (lc93_flat != -1) & (lc00_flat != -1)
    lc93_flat = lc93_flat[mask]
    lc00_flat = lc00_flat[mask]

    # Transition counts
    df = pd.DataFrame({"source": lc93_flat, "target": lc00_flat})
    transition_counts = df.groupby(["source", "target"]).size().reset_index(name="count")

    # Map to class names
    transition_counts["source_name"] = transition_counts["source"].map(class_dict)
    transition_counts["target_name"] = transition_counts["target"].map(class_dict)

    # Unique nodes
    all_nodes = list(pd.concat([transition_counts["source_name"], transition_counts["target_name"]]).unique())
    node_indices = {name: i for i, name in enumerate(all_nodes)}

    # Build Sankey
    source_indices = transition_counts["source_name"].map(node_indices)
    target_indices = transition_counts["target_name"].map(node_indices)
    values = transition_counts["count"]

    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            label=all_nodes,
            color="lightblue"
        ),
        link=dict(
            source=source_indices,
            target=target_indices,
            value=values
        )
    )])
    fig.update_layout(title_text="Landcover Transitions 1993 → 2000", font_size=12)
    return fig
