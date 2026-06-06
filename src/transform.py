"""
Transform module for province-capital data.
"""
import logging
from pathlib import Path
from typing import Dict

import pandas as pd

logger = logging.getLogger(__name__)


def parse_province_capital_table(raw_text: str) -> pd.DataFrame:
    """
    Parse a tab-separated table of province and capital names.

    Expected format:
        Province1\tCapital1
        Province2\tCapital2

    Args:
        raw_text: Multi-line string with tab-separated pairs.

    Returns:
        DataFrame with columns ['province', 'capital'].
    """
    province_capital: Dict[str, str] = {}
    lines = raw_text.strip().splitlines()

    for line in lines:
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) != 2:
            logger.warning(f"Skipping malformed line: {line}")
            continue
        province, capital = parts[0].strip(), parts[1].strip()
        province_capital[province] = capital

    df = pd.DataFrame(
        province_capital.items(), columns=["province", "capital"]
    )
    logger.info(f"Parsed {len(df)} province-capital pairs.")
    return df


def save_to_csv(df: pd.DataFrame, output_path: Path) -> None:
    """
    Save DataFrame to CSV, creating parent directories if needed.

    Args:
        df: DataFrame to save.
        output_path: Path object for the output CSV file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    logger.info(f"Saved CSV to {output_path}")