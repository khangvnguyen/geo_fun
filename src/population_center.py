"""
Population center calculation for provinces using commune-level population data.
"""
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from typing import Tuple, Dict, Optional


def calculate_population_centers(communes_gdf: gpd.GeoDataFrame, 
                                  population_col: str = 'dan_so',
                                  group_col: str = 'ten_tinh') -> gpd.GeoDataFrame:
    """
    Calculate population-weighted centroids for each province.
    
    Args:
        communes_gdf: GeoDataFrame with commune geometries and population data.
        population_col: Column name containing population numbers.
        group_col: Column name to group by (usually province name).
    
    Returns:
        GeoDataFrame with columns: [group_col, total_population, geometry]
    """
    # Ensure projected CRS for accurate centroid calculations
    if communes_gdf.crs.is_geographic:
        # Use UTM zone 48N for Vietnam (adjust if needed)
        communes_gdf = communes_gdf.to_crs("EPSG:32648")
    
    # Calculate centroids and weighted coordinates
    gdf = communes_gdf.copy()
    gdf['centroid_x'] = gdf['geometry'].centroid.x
    gdf['centroid_y'] = gdf['geometry'].centroid.y
    gdf['weighted_x'] = gdf['centroid_x'] * gdf[population_col]
    gdf['weighted_y'] = gdf['centroid_y'] * gdf[population_col]
    
    # Aggregate by province
    aggregated = gdf.groupby(group_col).agg(
        total_population=(population_col, 'sum'),
        sum_weighted_x=('weighted_x', 'sum'),
        sum_weighted_y=('weighted_y', 'sum')
    ).reset_index()
    
    # Calculate population center coordinates
    aggregated['center_x'] = aggregated['sum_weighted_x'] / aggregated['total_population']
    aggregated['center_y'] = aggregated['sum_weighted_y'] / aggregated['total_population']
    
    # Create GeoDataFrame
    center_geometry = [Point(xy) for xy in zip(aggregated['center_x'], aggregated['center_y'])]
    pop_centers = gpd.GeoDataFrame(
        aggregated[[group_col, 'total_population']],
        geometry=center_geometry,
        crs=communes_gdf.crs
    )
    
    return pop_centers


def extract_capitals(communes_gdf: gpd.GeoDataFrame, 
                     capital_col: str = 'thu_phu',
                     name_col: str = 'ten_xa',
                     group_col: str = 'ten_tinh') -> Dict[str, Tuple[float, float, str]]:
    """
    Extract capital locations from communes GeoDataFrame.
    
    Returns:
        Dictionary: province_name -> (longitude, latitude, capital_name)
    """
    capitals = {}
    
    for province in communes_gdf[group_col].unique():
        capital_row = communes_gdf[(communes_gdf[group_col] == province) & 
                                    (communes_gdf[capital_col] == True)]
        if not capital_row.empty:
            cap_geom = capital_row.iloc[0]['geometry'].centroid
            cap_name = capital_row.iloc[0][name_col]
            capitals[province] = (cap_geom.x, cap_geom.y, cap_name)
        else:
            capitals[province] = (None, None, None)
    
    return capitals


def find_commune_for_point(point: Point, 
                           gdf: gpd.GeoDataFrame, 
                           province_name: Optional[str] = None) -> Tuple[str, str]:
    """
    Find which commune contains a given point.
    
    Args:
        point: Shapely Point geometry.
        gdf: GeoDataFrame of communes.
        province_name: Optional province to restrict search.
    
    Returns:
        Tuple of (commune_name, actual_province_name)
    """
    point_gdf = gpd.GeoDataFrame(geometry=[point], crs=gdf.crs)
    
    # Try within specific province first
    if province_name:
        communes_in_prov = gdf[gdf['ten_tinh'] == province_name]
        joined = gpd.sjoin(point_gdf, communes_in_prov, how='left', predicate='within')
        if not joined.empty and pd.notna(joined.iloc[0]['index_right']):
            return joined.iloc[0]['ten_xa'], province_name
    
    # Try anywhere in the country
    joined_all = gpd.sjoin(point_gdf, gdf, how='left', predicate='within')
    if not joined_all.empty and pd.notna(joined_all.iloc[0]['index_right']):
        return joined_all.iloc[0]['ten_xa'], joined_all.iloc[0]['ten_tinh']
    
    # Fallback: nearest commune
    sindex = gdf.sindex
    nearest_idx = sindex.nearest(point, return_distance=False)[0]
    nearest_commune = gdf.iloc[nearest_idx]
    return nearest_commune['ten_xa'], nearest_commune['ten_tinh']


def map_population_centers_to_communes(pop_centers: gpd.GeoDataFrame, 
                                        communes_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Add commune information for each population center.
    
    Returns:
        GeoDataFrame with added columns: 'commune_of_pop_center', 'actual_province_of_center'
    """
    pop_centers = pop_centers.copy()
    clean_commune_names = []
    actual_provinces = []
    
    for _, row in pop_centers.iterrows():
        prov_name = row['ten_tinh']
        pop_point = row['geometry']
        commune_name, actual_prov = find_commune_for_point(pop_point, communes_gdf, prov_name)
        
        clean_commune_names.append(commune_name)
        actual_provinces.append(actual_prov)
    
    pop_centers['commune_of_pop_center'] = clean_commune_names
    pop_centers['actual_province_of_center'] = actual_provinces
    
    return pop_centers


def get_commune_geometry_dict(communes_gdf: gpd.GeoDataFrame) -> Dict[Tuple[str, str], any]:
    """
    Create dictionary mapping (commune_name, province_name) -> geometry.
    """
    geom_dict = {}
    for _, row in communes_gdf.iterrows():
        geom_dict[(row['ten_xa'], row['ten_tinh'])] = row['geometry']
    return geom_dict