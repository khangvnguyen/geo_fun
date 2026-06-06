"""
Visualization for population centers vs capitals using Plotly.
"""
import plotly.graph_objects as go
import geopandas as gpd
from typing import Dict, Tuple, List


def extract_polygon_coords(geom):
    """Extract exterior coordinates from Polygon or MultiPolygon."""
    coords_list = []
    if geom.geom_type == 'Polygon':
        coords_list.append(list(geom.exterior.coords))
    elif geom.geom_type == 'MultiPolygon':
        for poly in geom.geoms:
            coords_list.append(list(poly.exterior.coords))
    return coords_list


def create_province_comparison_figure(provinces_gdf: gpd.GeoDataFrame,
                                       communes_gdf: gpd.GeoDataFrame,
                                       pop_centers: gpd.GeoDataFrame,
                                       capitals: Dict[str, Tuple[float, float, str]],
                                       pop_commune_geoms: Dict[str, any],
                                       capital_commune_geoms: Dict[str, any]) -> go.Figure:
    """
    Create interactive Plotly figure comparing population centers and capitals.
    
    Args:
        provinces_gdf: GeoDataFrame of province boundaries.
        communes_gdf: GeoDataFrame of commune boundaries (for centroid extraction).
        pop_centers: GeoDataFrame with population center points.
        capitals: Dictionary mapping province -> (lon, lat, name).
        pop_commune_geoms: Dictionary mapping province -> population center commune geometry.
        capital_commune_geoms: Dictionary mapping province -> capital commune geometry.
    """
    provinces = sorted(provinces_gdf['ten_tinh'].unique())
    fig = go.Figure()
    
    # Build traces for each province
    for prov_name in provinces:
        # 1. Province boundary
        prov_geom = provinces_gdf[provinces_gdf['ten_tinh'] == prov_name].iloc[0]['geometry']
        rings = extract_polygon_coords(prov_geom)
        for ring in rings:
            fig.add_trace(go.Scattergeo(
                lon=[c[0] for c in ring],
                lat=[c[1] for c in ring],
                mode='lines',
                fill='toself',
                fillcolor='rgba(173,216,230,0.4)',
                line=dict(color='black', width=1),
                name=f"{prov_name} boundary",
                showlegend=False,
                visible=(prov_name == provinces[0])
            ))
        
        # 2. Population center point
        pop_row = pop_centers[pop_centers['ten_tinh'] == prov_name]
        if not pop_row.empty:
            pop_lon = pop_row.iloc[0]['geometry'].x
            pop_lat = pop_row.iloc[0]['geometry'].y
            pop_commune = pop_row.iloc[0]['commune_of_pop_center']
            fig.add_trace(go.Scattergeo(
                lon=[pop_lon],
                lat=[pop_lat],
                mode='markers+text',
                marker=dict(size=10, color='red', symbol='circle', line=dict(width=1, color='darkred')),
                text=[pop_commune],
                textposition='top right',
                textfont=dict(size=10, color='red'),
                name=f"{prov_name} pop center",
                showlegend=False,
                visible=(prov_name == provinces[0])
            ))
        
        # 3. Capital point
        cap_info = capitals.get(prov_name)
        if cap_info and cap_info[2] is not None:
            cap_lon, cap_lat, cap_name = cap_info
            fig.add_trace(go.Scattergeo(
                lon=[cap_lon],
                lat=[cap_lat],
                mode='markers+text',
                marker=dict(size=12, color='green', symbol='star', line=dict(width=1, color='darkgreen')),
                text=[cap_name],
                textposition='top right',
                textfont=dict(size=10, color='green'),
                name=f"{prov_name} capital",
                showlegend=False,
                visible=(prov_name == provinces[0])
            ))
        
        # 4. Population center commune boundary
        pop_com_geom = pop_commune_geoms.get(prov_name)
        if pop_com_geom:
            rings = extract_polygon_coords(pop_com_geom)
            for ring in rings:
                fig.add_trace(go.Scattergeo(
                    lon=[c[0] for c in ring],
                    lat=[c[1] for c in ring],
                    mode='lines',
                    fill='none',
                    line=dict(color='orange', width=1.5, dash='dot'),
                    name=f"{prov_name} pop commune",
                    showlegend=False,
                    visible=(prov_name == provinces[0])
                ))
        
        # 5. Capital commune boundary
        cap_com_geom = capital_commune_geoms.get(prov_name)
        if cap_com_geom:
            rings = extract_polygon_coords(cap_com_geom)
            for ring in rings:
                fig.add_trace(go.Scattergeo(
                    lon=[c[0] for c in ring],
                    lat=[c[1] for c in ring],
                    mode='lines',
                    fill='none',
                    line=dict(color='green', width=1.5, dash='dot'),
                    name=f"{prov_name} capital commune",
                    showlegend=False,
                    visible=(prov_name == provinces[0])
                ))
    
    return fig


def add_dropdown_menu(fig: go.Figure, 
                      provinces: List[str], 
                      provinces_gdf: gpd.GeoDataFrame) -> go.Figure:
    """
    Add dropdown menu for province selection with auto-zoom.
    """
    buttons = []
    
    for prov in provinces:
        visible_flags = []
        for trace in fig.data:
            if prov in trace.name:
                visible_flags.append(True)
            else:
                visible_flags.append(False)
        
        geom = provinces_gdf[provinces_gdf['ten_tinh'] == prov].iloc[0]['geometry']
        bounds = geom.bounds
        padding_x = (bounds[2] - bounds[0]) * 0.1
        padding_y = (bounds[3] - bounds[1]) * 0.1
        
        # Create a custom JavaScript callback using plotly.js
        buttons.append(dict(
            label=prov,
            method="update",
            args=[
                {"visible": visible_flags},
                {
                    "title": f"Province: {prov}",
                    "geo.lonaxis.range": [bounds[0] - padding_x, bounds[2] + padding_x],
                    "geo.lataxis.range": [bounds[1] - padding_y, bounds[3] + padding_y],
                    "geo.projection.scale": 1  # Reset scale
                }
            ]
        ))
    
    # Add a "Reset All" button (optional)
    all_visible = [True for _ in range(len(fig.data))]
    buttons.append(dict(
        label="Show All",
        method="update",
        args=[
            {"visible": all_visible},
            {
                "title": "All Provinces",
                "geo.lonaxis.range": [102, 110],
                "geo.lataxis.range": [8, 24],
                "geo.projection.scale": 1
            }
        ]
    ))
    
    fig.update_layout(
        updatemenus=[dict(
            active=0,
            buttons=buttons,
            direction="down",
            showactive=True,
            x=0.02,
            y=1.02,
            xanchor="left",
            yanchor="top",
            font=dict(size=12)
        )]
    )
    
    return fig


def configure_layout(fig: go.Figure, title: str = "Province Capitals vs Population Centers") -> go.Figure:
    """Apply consistent layout styling."""
    fig.update_layout(
        title=title,
        geo=dict(
            scope='asia',
            projection_type='equirectangular',
            showland=True,
            landcolor='white',
            coastlinecolor='gray',
            showcountries=False,
            showsubunits=False,
            showframe=False,
            resolution=50,
            lonaxis_range=[102, 110], # Vietnam approximate bounds
            lataxis_range=[8, 24], # Vietnam approximate bounds
            # Disable zoom/pan
            bgcolor='rgba(0,0,0,0)'
        ),
        width=1100,
        height=750,
        margin=dict(l=10, r=10, t=80, b=10),
        # Disable drag mode
        dragmode=False
    )
    
    # Disable zoom controls
    fig.update_layout(
        modebar=dict(
            remove=['zoom', 'pan', 'select', 'lasso', 'zoomIn', 'zoomOut', 'autoScale'],
            add=[]
        )
    )
    
    return fig