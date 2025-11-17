# sankey_utils.py
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from matplotlib import colors
import matplotlib.colors as mcolors

def create_sankey(data_path):
    """
    Create a Plotly Sankey diagram from two raster arrays.
    
    Parameters:
    - lc93: np.array, raster for 1993
    - lc00: np.array, raster for 2000
    - class_dict: dict, mapping class IDs to names
    
    Returns:
    - fig: Plotly Figure object (Sankey diagram)
    """
    # Define custom color map and convert to RGBA for Plotly
    
    c_map = colors.ListedColormap(['cornflowerblue', 'limegreen', 'darkred', 'darkgreen', 'goldenrod', 'darkblue']) #(['lightskyblue', 'limegreen', 'darkred', '#4C7300', 'goldenrod', '#002673', 'indianred'])
    class_colors = [c_map(i) for i in range(c_map.N)]
    class_names = ["Marsh", "Shrub", "Ghost Forest", "Forest", "Cultivated", "Water"] #darkred

    # Filter out the boundary class -1
    source_classes = [0, 1, 2, 3, 4, 5]
    target_classes = [0, 1, 2, 3, 4, 5]

    # Prepare flows and labels
    labels = ['0 → 0', '0 → 1', '0 → 2', '0 → 3', '0 → 4', '0 → 5', 
              '1 → 0', '1 → 1', '1 → 2', '1 → 3', '1 → 4', '1 → 5', 
              '2 → 0', '2 → 1', '2 → 2', '2 → 3', '2 → 4', '2 → 5', 
              '3 → 0', '3 → 1', '3 → 2', '3 → 3', '3 → 4', '3 → 5', 
              '4 → 0', '4 → 1', '4 → 2', '4 → 3', '4 → 4', '4 → 5', 
              '5 → 0', '5 → 2', '5 → 3', '5 → 4', '5 → 5']
    # Create a DataFrame with the flow data
    sankey_data = pd.read_csv(data_path)
    flows = sankey_data["flow"]

    # Source totals (so they sum to 100%)
    total_source_flow = sankey_data[sankey_data["source"].isin(source_classes)]["flow"].sum()
    source_labels = [
        f"{sankey_data[sankey_data['source'] == i]['flow'].sum() / total_source_flow * 100:.1f}%"
        for i in source_classes]

    # Target totals (so they sum to 100%)
    total_target_flow = sankey_data[sankey_data["target"].isin([i + len(source_classes) for i in target_classes])]["flow"].sum()
    target_labels = [
        f"{sankey_data[sankey_data['target'] == i + len(source_classes)]['flow'].sum() / total_target_flow * 100:.1f}%"
        for i in target_classes]

    # Final labels
    node_labels = source_labels + target_labels
    link_colors = [
        f"rgba({int(mcolors.to_rgba(color)[0] * 255)}, {int(mcolors.to_rgba(color)[1] * 255)}, {int(mcolors.to_rgba(color)[2] * 255)}, 0.7)"
        for color in [class_colors[source] for source in sankey_data["source"]]]

    node_colors = [
        f"rgba({int(r*255)}, {int(g*255)}, {int(b*255)}, {a})"
        for r, g, b, a in [class_colors[i] for i in source_classes] + [class_colors[i] for i in target_classes]]

    # Create the Sankey diagram with adjusted link colors for transparency
    sankey_fig = go.Figure(data=[go.Sankey(
        arrangement="snap", # prevents reorientation
        orientation="v",
        node=dict(
            pad=40,
            thickness=50,
            line=dict(color="black", width=0.2),
            label=node_labels,
            color=node_colors,
            #x=[0.01, 0.3, 0.7, 0.95],  # lock x positions
            #y=[0.1, 0.4, 0.6, 0.9],    # lock y positions
        ),
        link=dict(
            source=sankey_data["source"],
            target=sankey_data["target"],
            value=sankey_data["flow"],
            color=link_colors  # Apply semi-transparent source-based colors to the links
        ),
    )])

    # Add the legend at the bottom with squares for each class
    patches = [go.Scatter(
        x=[None], y=[None], mode='markers', marker=dict(
            symbol='square',
            color=c_map.colors[i % c_map.N],  # Ensure the index stays within the bounds of the colormap
            size=50
        ), name=class_names[i]) for i in range(len(class_names))]

    # Add the traces for the legend
    sankey_fig.add_traces(patches)
    sankey_fig.update_traces(
        #node_align="center",
        textfont=dict(color='black', family="Impact", size=20, #shadow="none"
                      ),
        hoverinfo='all',
        #textposition="inside",   # or "outside"
        hoverlabel=dict(bgcolor='rgba(0,0,0,0)', font=dict(color="white"), #align="center",
                         #bordercolor="white"
                        )#,
        #selector=dict(type='sankey')  # Change label font color to black
    )

    # Update layout with vertical titles
    sankey_fig.update_layout(
        #title_text="Land Cover Change from 2000 to 2022",
        font_size=15,
        plot_bgcolor='rgba(0,0,0,0)',  # Remove plot background
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=30, t=30, b=30),  # Increase bottom margin for legend
        legend=dict(
            #title="  Landcover type",
            orientation="h",  # Vertical legend
            x=0.5,
            xanchor="center",
            y=0,  # Position it to the right of the plot #0.0
            yanchor="top",
            traceorder="normal",
            font=dict(size=14, color="black", family="Arial Black"),
            bgcolor="rgba(255, 255, 255, 0)",
            borderwidth=0,
            itemwidth=30,  # Adjust width of each legend item
            itemsizing='trace',  # Keep item sizing consistent
            #columnwidth=0.2,  # Adjust the width of the column layout (if needed)
            tracegroupgap=1  # Adjust the gap between groups of traces
        ),
        xaxis=dict(showticklabels=False, ticks="", zeroline=False, visible=False),  # Hide the x-axis
        yaxis=dict(showticklabels=False, ticks="", zeroline=False, visible=False),  # Hide the y-axis
        annotations=[
            # Vertical title for "Land Cover in 1989" at the top-left
            dict(
                x=-0.012,
                y=1,
                xref="paper",
                yref="paper",
                text="<span style='line-height:0.5;'>Landcover<br>in 1985 (%)</span>",
                showarrow=False,
                font=dict(size=18, color="black", family="Franklin Gothic Medium"), #https://jonathansoma.com/lede/data-studio/matplotlib/list-all-fonts-available-in-matplotlib-plus-samples/
                align="center",
                textangle=-90,  # Vertical text
                xanchor="center",
                yanchor="top"
            ),
            # Vertical title for "Land Cover in 2021" at the bottom-left
            dict(
                x=-0.012,
                y=0,
                xref="paper",
                yref="paper",
                text="<span style='line-height:0.5;'>Landcover<br>in 2021 (%)</span>",
                showarrow=False,
                font=dict(size=18, color="black", family="Franklin Gothic Medium"),
                align="center",
                textangle=-90,  # Vertical text
                xanchor="center",
                yanchor="bottom"
            )
        ]
    )
    return sankey_fig
