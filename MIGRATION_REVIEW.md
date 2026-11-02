# Migration review (read before submitting)

- Original repo: `/Users/apple/Downloads/city建项目/sf-housing-growth` (unchanged)
- New repo: `/Users/apple/Downloads/city建项目/sf-housing-growth_midterm`
- Copied 36 files.

## Items to resolve

1. Update paths in scripts and notebooks to `data/raw/` and `data/processed/` (use `analysis/paths.py`).
2. Ensure notebooks run after Restart & Run All, and add one tested pipeline entrypoint for Track B.
3. Add figures to `visualizations/` and the midterm PDF to the root.
4. Verify historical 2008 housing-stock sources before treating the 2005 baseline as valid.
5. Check `requirements.txt` for exact packages and versions actually used.

## Source files not found (not copied)
- None

## Duplicate file comparisons

- **identical**: `tasks/1_SF_Land_Use_Clean/processed_data/sf_land_use_clean.csv` vs `tasks/2_Tabular_Join/raw_data/sf_land_use_clean.csv`
- **identical**: `tasks/2_Tabular_Join/processed_data/housing_production_located.csv` vs `tasks/3_Tract_Aggregation/raw_data/housing_production_located.csv`
- **DIFFERENT — review before deleting either version**: `Unofficial-CYPLAN-Project-main/data/raw/housing_production.csv` vs `Unofficial-CYPLAN-Project-main/housing_production.csv`
- **DIFFERENT — review before deleting either version**: `Unofficial-CYPLAN-Project-main/data/raw/dbi_all_study_permit_coordinates.json` vs `Unofficial-CYPLAN-Project-main/dbi_all_study_permit_coordinates.json`
- **identical**: `tasks/1_SF_Land_Use_Clean/scripts/clean_sf_land_use.py` vs `Unofficial-CYPLAN-Project-main/clean_sf_land_use.py`
- **identical**: `tasks/2_Tabular_Join/scripts/tabular_join.py` vs `Unofficial-CYPLAN-Project-main/tabular_join.py`
- **identical**: `tasks/3_Tract_Aggregation/scripts/tract_aggregation.py` vs `Unofficial-CYPLAN-Project-main/tract_aggregation.py`

## Large files

- No individual files over 98 MiB.
