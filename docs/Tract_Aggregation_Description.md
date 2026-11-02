# Step 3: Census Tract Aggregation

**Script:** `tract_aggregation.py`

**Inputs:** `housing_production_located.csv`, `Census_2020__Tracts_for_San_Francisco.csv`

**Data Source:** [DataSF — Census 2020: Tracts for San Francisco](https://data.sf.gov/Geographic-Locations-and-Boundaries/Census-2020-Tracts-for-San-Francisco/tmph-tgz9) (CSV download)

**Outputs:** `housing_production_with_tract.csv`, `tract_housing_growth.csv`

## Method

1. **Spatial Join:** Convert housing coordinates into points and Census Tract WKT geometries into polygons (EPSG:4326). Use GeoPandas spatial join (`within`) to assign each located housing record a Census Tract `GEOID`.

2. **Aggregation:** Group housing records by `GEOID` and sum `Net Units Completed`. Include all 244 Census Tracts, assigning zero to tracts without matched housing records.

3. **Validation:** Verify that original housing records are preserved, each record is assigned to at most one tract, and aggregation does not change the total number of assigned housing units.

## Results

| Metric | Result |
|---|---:|
| Total Housing Records | 4,818 |
| Assigned to Census Tracts | 3,239 |
| Unassigned Records | 1,579 |
| Net Units Aggregated | 20,310 |
| Total Census Tracts | 244 |

The output provides tract-level net housing additions for 2005–2025. Results include only successfully geolocated housing records; unassigned records are retained separately.


We aggregated net housing units completed between 2005 and 2025 across 244 San Francisco census tracts. Among successfully geolocated records, Tract 176.04 gained the most housing units (1,942), followed by Tract 226.00 (1,618) and Tract 607.02 (1,319). Fourteen tracts had no geolocated housing additions. These results are based on 33.35% of total net housing units due to unmatched records.
