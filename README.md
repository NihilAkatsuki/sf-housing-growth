# San Francisco Housing Growth — Midterm

**Project:** Housing Growth, Neighborhood Inequality, and Zoning Capacity in San Francisco

## Project Structure

- `data/raw/` — Original, unmodified datasets used in the analysis.
- `data/processed/` — Cleaned, filtered, joined, and tract-level datasets generated during analysis.
- `analysis/` — Reusable Python files containing:
  - `data_processing.py` — Data cleaning and processing functions.
  - `visualize.py` — Functions for generating maps, charts, and other visualizations.
  - `comparisons.py` — Functions for summarizing and comparing housing production across income and renter-share groups.
- `notebooks/` — Contains `SF_Housing_Analysis_TrackB.ipynb`, the main notebook that runs the analysis.
- `visualizations/` — Generated figures and maps referenced in the Midterm PDF.

## Setup

### 1. Clone the repository

Clone the repository and navigate to its root directory:

```bash
git clone https://github.com/NihilAkatsuki/sf-housing-growth.git
cd sf-housing-growth
```

### 2. Install dependencies

Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Download the raw datasets
Download the raw datasets using the link below. These datasets are in `data/raw/`.

[Download Raw Data (ZIP)](https://pub-7accb6becb5d446e8d98976537649e3e.r2.dev/raw_data.zip)

## Running the Analysis

### 1. Run the analysis notebook

Open Jupyter Notebook from the project root:

```bash
jupyter notebook
```

Open `notebooks/SF_Housing_Analysis_TrackB.ipynb` and run all cells sequentially from top to bottom.

The notebook imports and calls functions from the Python modules in `analysis/` to perform the full analysis.

### 2. View the outputs

The processed datasets are available in `data/processed/`, and the generated figures are saved in `visualizations/`.

## Outputs

### Processed datasets

- `housing_production_filtered.csv`
- `sf_land_use_clean.csv`
- `housing_production_located_recovered.csv`
- `housing_production_with_tract.csv`
- `tract_housing_production.csv`
- `tract_acs_groups.csv`
- `group_housing_comparisons.csv`

### Generated visualizations

- `historical_net_additions_map.png`
- `housing_additions_by_acs_groups.png`
- `net_housing_additions_distribution.png`
- `top_10_net_housing_additions_tracts.png`
