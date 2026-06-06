#!/usr/bin/env python3
"""
Generate province_capital.csv from a hardcoded table (or external file).
"""
import logging
import sys
from pathlib import Path

# Add project root to Python path if needed
sys.path.append(str(Path(__file__).parent.parent))

from src.transform import parse_province_capital_table, save_to_csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def load_raw_text(file_path: Path) -> str:
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

def main():
    # Define output path relative to project root
    project_root = Path(__file__).parent.parent
    output_path = project_root / "data" / "processed" / "province_capital.csv"

    logger.info("Starting province-capital transformation")
    # In main:
    raw_text_path = project_root / "data" / "raw" / "province_capital.txt"
    raw_text = load_raw_text(raw_text_path)
    df = parse_province_capital_table(raw_text)
    save_to_csv(df, output_path)
    logger.info("Done.")

if __name__ == "__main__":
    main()