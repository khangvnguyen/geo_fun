"""
Plotting and HTML export for shape comparison.
"""
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon as MPLPolygon
from matplotlib.collections import PatchCollection
from shapely import affinity
import mpld3
import geopandas as gpd
from typing import List, Tuple

ShapeData = Tuple[gpd.GeoSeries, str, float]


def extract_extreme_shapes(gdf: gpd.GeoDataFrame, n: int = 5) -> Tuple[List[ShapeData], List[ShapeData]]:
    """Extract n least and n most circular shapes."""
    gdf_sorted = gdf.sort_values('circleness')
    least = gdf_sorted.head(n)
    most = gdf_sorted.tail(n)
    # avoid overlap if total rows < 2n
    most = most[~most.index.isin(least.index)]
    least_shapes = [(row.geometry, row['ten_xa'], row['circleness']) for _, row in least.iterrows()]
    most_shapes = [(row.geometry, row['ten_xa'], row['circleness']) for _, row in most.iterrows()]
    return least_shapes, most_shapes


def normalize_geometry(geom, target_scale: float = 1.0, simplify_tolerance: float = 0.0):
    """
    Translate geometry to origin, scale to fit inside [-target_scale, target_scale],
    then optionally simplify using a relative tolerance (in the scaled coordinate system).
    """
    centroid = geom.centroid
    geom_trans = affinity.translate(geom, xoff=-centroid.x, yoff=-centroid.y)
    minx, miny, maxx, maxy = geom_trans.bounds
    width = maxx - minx
    height = maxy - miny
    scale = (2 * target_scale) / max(width, height)
    geom_scaled = affinity.scale(geom_trans, xfact=scale, yfact=scale, origin=(0, 0))
    
    if simplify_tolerance > 0:
        # Simplify using a small relative value (e.g., 0.005 = 0.5% of bounding box)
        geom_scaled = geom_scaled.simplify(simplify_tolerance, preserve_topology=True)
    return geom_scaled

def create_shape_figure(least_shapes: List[ShapeData], most_shapes: List[ShapeData],
                        title: str = "Province shapes – least vs most circular",
                        simplify_relative: float = 0.0) -> plt.Figure:
    """
    Create a 2×N grid of normalized shape plots optimized for laptop screens.
    """
    n = max(len(least_shapes), len(most_shapes))
    # Build list with None placeholders for missing shapes
    all_shapes = []
    for i in range(n):
        if i < len(least_shapes):
            all_shapes.append(least_shapes[i])
        else:
            all_shapes.append((None, None, None))
    for i in range(n):
        if i < len(most_shapes):
            all_shapes.append(most_shapes[i])
        else:
            all_shapes.append((None, None, None))
    
    fig, axes = plt.subplots(2, n, figsize=(4 * n, 8))
    fig.subplots_adjust(hspace=0.25, wspace=0.15)
    fig.suptitle(title, fontsize=18, y=0.98)
    
    for idx, (geom, name, circ) in enumerate(all_shapes):
        if geom is None:
            continue
        row = 0 if idx < n else 1
        col = idx % n
        ax = axes[row, col]
        
        norm_geom = normalize_geometry(geom, target_scale=1.0, simplify_tolerance=simplify_relative)
        
        patches = []
        if norm_geom.geom_type == 'Polygon':
            patches.append(MPLPolygon(list(norm_geom.exterior.coords), closed=True))
        elif norm_geom.geom_type == 'MultiPolygon':
            for poly in norm_geom.geoms:
                patches.append(MPLPolygon(list(poly.exterior.coords), closed=True))
        else:
            continue
        
        collection = PatchCollection(patches, facecolor='lightblue', edgecolor='black', linewidth=1.5)
        ax.add_collection(collection)
        
        # Disable autoscaling to keep our manual limits
        ax.autoscale(False)
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-1.2, 1.2)
        ax.set_aspect('equal')
        
        # Completely hide the axis – works even with mpld3
        ax.set_axis_off()          # removes axis lines, ticks, labels
        ax.set_frame_on(False)     # removes the frame
        # Additional safety: make spines and ticks invisible
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.set_xticks([])
        ax.set_yticks([])
        # Optional: remove the background patch (makes it fully transparent)
        ax.patch.set_visible(False)
        
        ax.set_title(f"{name}\n({circ:.3f})", fontsize=28, pad=8)
        
        if col == 0:
            label = "Least circular" if row == 0 else "Most circular"
            ax.text(0, 1.08, label, transform=ax.transAxes, ha='center', va='bottom',
                    fontsize=28, weight='bold')
    
    # Hide any unused subplots
    for i in range(len(all_shapes), 2 * n):
        row = i // n
        col = i % n
        if row < 2 and col < n:
            axes[row, col].set_visible(False)
    
    return fig

def save_figure_as_html(fig: plt.Figure, output_path: str) -> None:
    """Save matplotlib figure as interactive HTML."""
    html_str = mpld3.fig_to_html(fig)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_str)
    print(f"HTML saved to {output_path}")