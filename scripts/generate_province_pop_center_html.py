#!/usr/bin/env python3
"""
Generate interactive HTML map showing province capitals vs population centers.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import geopandas as gpd
import pandas as pd

from src.population_center import (
    calculate_population_centers,
    extract_capitals,
    map_population_centers_to_communes,
    get_commune_geometry_dict
)
from src.visualize_population import (
    create_province_comparison_figure,
    add_dropdown_menu,
    configure_layout
)


def main():
    # 1. Configuration
    DATA_COMMUNES = Path("data/raw/vn_phuong_xa_34.geojson")
    DATA_PROVINCES = Path("data/raw/vn_tinh_thanh_34.geojson")
    DATA_CAPITAL_CSV = Path("data/processed/province_capital.csv")
    OUTPUT_HTML = Path("output/capitals_vs_population_centers.html")
    
    # 2. Load data
    print("Loading commune data...")
    communes_gdf = gpd.read_file(DATA_COMMUNES)
    
    print("Loading province boundaries...")
    provinces_gdf = gpd.read_file(DATA_PROVINCES)
    
    print("Loading capital mapping...")
    capital_df = pd.read_csv(DATA_CAPITAL_CSV)
    
    # 3. Add thu_phu flag to communes
    capital_dict = dict(zip(capital_df['province'], capital_df['capital']))
    communes_gdf['thu_phu'] = communes_gdf.apply(
        lambda row: row['ten_xa'] == capital_dict.get(row['ten_tinh']), axis=1
    )
    
    # 4. Calculate population centers
    print("Calculating population centers...")
    pop_centers = calculate_population_centers(communes_gdf, population_col='dan_so')
    
    # 5. Convert to WGS84 for visualization
    communes_gdf = communes_gdf.to_crs("EPSG:4326")
    provinces_gdf = provinces_gdf.to_crs("EPSG:4326")
    pop_centers = pop_centers.to_crs("EPSG:4326")
    
    # 6. Map population centers to communes
    print("Mapping population centers to communes...")
    pop_centers = map_population_centers_to_communes(pop_centers, communes_gdf)
    
    # 7. Extract capitals
    capitals = extract_capitals(communes_gdf)
    
    # 8. Get commune geometries for display
    print("Building geometry dictionaries...")
    commune_geom_dict = get_commune_geometry_dict(communes_gdf)
    
    # Population center commune geometries
    pop_commune_geoms = {}
    for _, row in pop_centers.iterrows():
        prov_key = row['ten_tinh']
        com_name = row['commune_of_pop_center']
        actual_prov = row['actual_province_of_center']
        key = (com_name, actual_prov)
        pop_commune_geoms[prov_key] = commune_geom_dict.get(key)
    
    # Capital commune geometries
    capital_commune_geoms = {}
    for prov_name in provinces_gdf['ten_tinh'].unique():
        cap_info = capitals.get(prov_name)
        if cap_info and cap_info[2]:
            key = (cap_info[2], prov_name)
            capital_commune_geoms[prov_name] = commune_geom_dict.get(key)
    
    # 9. Create visualization
    print("Creating Plotly figure...")
    fig = create_province_comparison_figure(
        provinces_gdf, communes_gdf, pop_centers, capitals,
        pop_commune_geoms, capital_commune_geoms
    )
    
    # 10. Add interactivity and styling
    provinces = sorted(provinces_gdf['ten_tinh'].unique())
    fig = add_dropdown_menu(fig, provinces, provinces_gdf)
    fig = configure_layout(fig)
    
    # --- ADD THIS: Set initial view to first province (An Giang) ---
    first_province = provinces[0]  # This should be "An Giang"
    first_geom = provinces_gdf[provinces_gdf['ten_tinh'] == first_province].iloc[0]['geometry']
    bounds = first_geom.bounds
    padding_x = (bounds[2] - bounds[0]) * 0.1
    padding_y = (bounds[3] - bounds[1]) * 0.1
    
    # Update the figure's initial geo ranges
    fig.update_geos(
        lonaxis_range=[bounds[0] - padding_x, bounds[2] + padding_x],
        lataxis_range=[bounds[1] - padding_y, bounds[3] + padding_y]
    )
    
    # Also update the title to show the first province
    fig.update_layout(title=f"Province: {first_province}")
    
    # 11. Save to HTML
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(str(OUTPUT_HTML))
    print(f"Saved interactive map to {OUTPUT_HTML}")
    print("Open in browser to explore!")


if __name__ == "__main__":
    main()