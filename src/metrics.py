"""
Geometric metrics for spatial data.
"""
import geopandas as gpd
import numpy as np
import pandas as pd

def add_circleness(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """
    Add a 'circleness' column to a GeoDataFrame.
    
    Circleness = (4 * pi * area) / (perimeter^2)
    A perfect circle has value 1.0; degenerate polygons approach 0.
    
    Args:
        gdf: GeoDataFrame with a valid geometry column (projected CRS).
    
    Returns:
        GeoDataFrame with new column 'circleness'.
    """
    # Avoid division by zero: perimeter might be extremely small for invalid geometries
    perimeter = gdf.geometry.length
    area = gdf.geometry.area
    
    # Use numpy.where to handle zero-length perimeters gracefully
    with np.errstate(divide='ignore', invalid='ignore'):
        circleness = (4 * np.pi * area) / (perimeter ** 2)
    circleness = np.where(np.isfinite(circleness), circleness, 0.0)
    
    gdf = gdf.copy()
    gdf['circleness'] = circleness
    return gdf


def add_thu_phu_column(gdf: gpd.GeoDataFrame, capital_df: pd.DataFrame) -> gpd.GeoDataFrame:
    """
    Add a boolean column 'thu_phu' indicating whether the commune (ten_xa) is the capital
    of its province (ten_tinh).
    
    Args:
        gdf: GeoDataFrame with columns 'ten_xa' and 'ten_tinh'.
        capital_df: DataFrame with columns 'province' and 'capital'.
    
    Returns:
        GeoDataFrame with added boolean column 'thu_phu'.
    """
    # Create a dictionary for fast lookup: province -> capital name
    capital_dict = dict(zip(capital_df['province'], capital_df['capital']))
    
    def is_capital(row):
        province = row['ten_tinh']
        capital_name = capital_dict.get(province)
        if capital_name is None:
            return False
        return row['ten_xa'] == capital_name
    
    gdf = gdf.copy()
    gdf['thu_phu'] = gdf.apply(is_capital, axis=1)
    return gdf