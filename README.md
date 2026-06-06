# Vietnam Geography Data Visualization

An interactive data visualization project for exploring Vietnam's administrative geography, including commune-level shape analysis, population centers, and capital city comparisons.

## 📊 Features

- **Shape Circularity Analysis**: Calculate and visualize the "circleness" of commune boundaries, identifying the most and least circular shapes
- **Population Centers**: Compute population-weighted centers for each province using commune-level demographic data
- **Capital vs. Population Center**: Interactive maps comparing provincial capitals with actual population centers
- **Interactive Visualizations**: HTML-based maps with dropdown menus for province selection
- **Modular Pipeline**: Reusable data transformation and visualization modules

## 🗂️ Project Structure

```
geography-project/
├── data/
│   ├── raw/                    # Original immutable data
│   │   ├── vn_phuong_xa_34.geojson      # Commune boundaries
│   │   └── vn_tinh_thanh_34.geojson     # Province boundaries
│   └── processed/              # Cleaned/transformed outputs
│       └── province_capital.csv         # Province-capital mapping
├── src/
│   ├── metrics.py              # Geometric metrics (circleness calculation)
│   ├── visualize.py            # Matplotlib shape visualization
│   ├── population_center.py    # Population center calculations
│   └── visualize_population.py # Plotly population map visualization
├── scripts/
│   ├── generate_capital_csv.py           # Generate province-capital CSV
│   ├── generate_circleness_html.py       # Generate shape comparison HTML
│   └── generate_capital_population_map.py # Generate population center map
├── output/                     # Generated HTML outputs
├── requirements.txt
└── README.md
```

## 🚀 Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download the repository**

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Verify data files**  
Ensure the following files exist in `data/raw/`:
- `vn_phuong_xa_34.geojson` (Commune boundaries with population data)
- `vn_tinh_thanh_34.geojson` (Province boundaries)
You can download these data at https://gis.vn/ban-do-hanh-chinh-viet-nam

## 📖 Usage

### 1. Generate Province-Capital Mapping

First, create the province-capital lookup table:

```bash
python scripts/generate_capital_csv.py
```

This creates `data/processed/province_capital.csv` with columns: `province`, `capital`

### 2. Generate Shape Circularity Visualization

Create an interactive HTML comparing the most and least circular communes:

```bash
python scripts/generate_circleness_html.py
```

**Output**: `output/province_circleness.html`

**What it shows**:
- Top 5 least circular communes (least circle-like shapes)
- Top 5 most circular communes (most circle-like shapes)
- Normalized shapes for direct comparison
- Circleness score (1.0 = perfect circle)

### 3. Generate Capital vs. Population Center Map

Create an interactive map comparing provincial capitals with population centers:

```bash
python scripts/generate_capital_population_map.py
```

**Output**: `output/capitals_vs_population_centers.html`

**What it shows**:
- Province boundaries (light blue fill)
- Capital locations (green stars) with commune boundaries (green dotted line)
- Population centers (red circles) with commune boundaries (orange dotted line)
- Dropdown menu to select provinces
- Automatic zoom to selected province

## 🎨 Customization

### Adjusting Shape Circularity Plot

Edit `src/visualize.py`:

```python
# Change figure size (line ~45)
fig, axes = plt.subplots(2, n, figsize=(2.5 * n, 5))
# Adjust 2.5 and 5 for width/height per subplot

# Change simplification tolerance (line ~12)
simplify_relative: float = 0.0  # 0 = no smoothing, 0.005 = light smoothing
```

### Adjusting Population Map

Edit `scripts/generate_capital_population_map.py`:

```python
# Change window size (line ~120)
width=1100,   # Figure width in pixels
height=750,   # Figure height in pixels

# Change zoom level (in src/visualize_population.py, line ~75)
padding_x = (bounds[2] - bounds[0]) * 0.1  # 0.1 = 10% padding around province
# Smaller padding = tighter zoom (0.05), larger padding = more context (0.2)
```

### Color Scheme Customization

In `src/visualize_population.py`:

```python
# Province fill color (line ~35)
fillcolor='rgba(173,216,230,0.4)'  # RGB + opacity

# Population center marker (line ~58)
marker=dict(size=10, color='red', symbol='circle')

# Capital marker (line ~77)
marker=dict(size=12, color='green', symbol='star')
```

## 📊 Data Requirements

### Commune GeoJSON (`vn_phuong_xa_34.geojson`)
Required attributes:
- `ten_tinh`: Province name
- `ten_xa`: Commune name
- `dan_so`: Population
- `geometry`: Polygon/MultiPolygon geometry

### Province GeoJSON (`vn_tinh_thanh_34.geojson`)
Required attributes:
- `ten_tinh`: Province name
- `geometry`: Polygon/MultiPolygon geometry

### CRS Information
- Calculations use projected CRS (EPSG:32648 or EPSG:3405)
- Visualization converts to WGS84 (EPSG:4326)

## 🧪 Methodology

### Circularity Metric (Circleness)

```
circleness = (4 * π * area) / (perimeter²)
```

- Value = 1.0 for perfect circle
- Value < 1.0 for irregular shapes
- Value → 0 for highly elongated shapes

### Population Center Calculation

1. Calculate centroid of each commune
2. Weight centroid coordinates by commune population
3. Aggregate by province: `(Σ(population × x) / Σ(population), Σ(population × y) / Σ(population))`
4. Result is population-weighted center of mass

## 🐛 Troubleshooting

### "No module named 'src'"
```bash
# Run scripts from project root directory
cd /path/to/geography-project
python scripts/script_name.py
```

### Missing provinces in output
- Verify `thu_phu` flag is properly set in commune data
- Check province-capital CSV for correct name matching

### Map shows blank/white screen
- Ensure GeoJSON files have valid geometries
- Check that CRS conversion to EPSG:4326 succeeded
- Verify data contains the expected province names

### Shapes appear as triangles
- Remove or reduce simplification tolerance (set to 0)
- Check original geometry vertex count

## 📝 Dependencies

- **geopandas** ≥ 0.14.0: Spatial data handling
- **pandas** ≥ 2.0.0: Data manipulation
- **numpy** ≥ 1.24.0: Numerical operations
- **matplotlib** ≥ 3.7.0: Static visualizations
- **shapely** ≥ 2.0.0: Geometric operations
- **plotly** ≥ 5.0.0: Interactive maps
- **mpld3** ≥ 0.5.0: Matplotlib to HTML export

## 🔄 Workflow Example

Complete pipeline to generate all visualizations:

```bash
# 1. Generate capital mapping
python scripts/generate_capital_csv.py

# 2. Generate shape circularity comparison
python scripts/generate_circleness_html.py

# 3. Generate population center map
python scripts/generate_capital_population_map.py

# 4. Open outputs in browser
open output/province_circleness.html
open output/capitals_vs_population_centers.html
```

## 📄 License

This project is for educational and research purposes.

## 👥 Contributing

Feel free to fork and adapt for your own geography projects. Suggested improvements:
- Add time-series population data
- Include additional shape metrics (compactness, convexity)
- Add 3D terrain visualization
- Export data to other formats (GeoPackage, Shapefile)

## 📧 Support

For issues or questions:
1. Check the Troubleshooting section
2. Verify data file paths and formats
3. Ensure all dependencies are installed correctly

---

**Happy mapping! 🗺️**