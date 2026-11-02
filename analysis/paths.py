"""Project-relative paths shared by analysis scripts."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
FIGURES = ROOT / "visualizations"
TABLES = ROOT / "outputs" / "tables"
