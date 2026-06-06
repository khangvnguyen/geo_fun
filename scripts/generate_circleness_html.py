#!/usr/bin/env python3
"""
Generate an HTML file comparing the 5 least circular and 5 most circular communes.
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

import geopandas as gpd
import pandas as pd
import numpy as np

from src.metrics import add_circleness, add_thu_phu_column
from src.visualize import extract_extreme_shapes, create_shape_figure, save_figure_as_html


def main():
    # --- 1. Configuration ---
    DATA_RAW_GEOJSON = Path("data/raw/vn_phuong_xa_34.geojson")
    DATA_CAPITAL_CSV = Path("data/processed/province_capital.csv")
    OUTPUT_HTML = Path("output/province_circleness.html")
    
    # --- 2. Load data ---
    print("Loading GeoJSON...")
    gdf = gpd.read_file(DATA_RAW_GEOJSON)
    print(f"Loaded {len(gdf)} communes.")
    
    print("Loading province-capital mapping...")
    capital_df = pd.read_csv(DATA_CAPITAL_CSV)
    
    # --- 3. Enrich data ---
    print("Adding 'thu_phu' column...")
    gdf = add_thu_phu_column(gdf, capital_df)
    
    print("Computing circleness...")
    gdf = add_circleness(gdf)
    
    # Filter out invalid geometries
    gdf = gdf[gdf['circleness'] > 0].copy()
    print(f"Valid communes after filtering: {len(gdf)}")
    
    # --- 4. Extract extreme shapes ---
    least, most = extract_extreme_shapes(gdf, n=5)
    print(f"Selected {len(least)} least circular and {len(most)} most circular.")
    
    # --- 5. Create figure ---
    # Set simplify_relative = 0 to keep original shapes (no triangle distortion)
    # If you want minor smoothing, use 0.005 (0.5% of bounding box)
    fig = create_shape_figure(least, most,
                              title="Top 5 least vs most circular communes (normalised size)",
                              simplify_relative=0.0)   # ← FIX: no simplification
    
    # --- 6. Save as interactive HTML ---
    OUTPUT_HTML.parent.mkdir(parents=True, exist_ok=True)
    save_figure_as_html(fig, str(OUTPUT_HTML))
    print(f"Done. Open {OUTPUT_HTML} in your browser.")


if __name__ == "__main__":
    main()