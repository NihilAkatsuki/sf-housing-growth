# Step 2: Tabular Join — Assigning Permit Locations

**Script:** `step2_tabular_join.py`

**Input:** `housing_production_filtered.csv`, `sf_land_use_clean.csv`

**Output:** `housing_production_located.csv`

## Method

1. **Single-Parcel Matching:** Perform a left join using Housing Production's `BlockLot` and Land Use's `mapblklot`, preserving parcel IDs as strings. Assign parcel centroid coordinates to matched housing records.

2. **Multi-Parcel Matching:** For remaining unmatched records, extract individual Parcel IDs from the 77 `multiple_parcels` entries and assign their shared group centroids. Use complete IDs even in truncated lists, while excluding incomplete fragments and conflicting locations.

3. **Unmatched Records:** Preserve records without valid matches and label each record as `matched_single`, `matched_multi_centroid`, or `unmatched`.

4. **Validation:** Verify that the join preserves the original Housing Production row count, order, and `Net Units Completed` values.

## Results

| Match Status | Records |
|---|---:|
| Matched (Single Parcel) | 3,204 |
| Matched (Multiple Parcels) | 35 |
| Unmatched | 1,579 |
| **Total** | **4,818** |

**Location Coverage: 67.23%**

The output preserves all 4,818 housing records, adds `latitude`, `longitude`, `match_status`, and `match_note`, and retains unmatched records with missing coordinates. Multi-parcel coordinates represent shared group centroids rather than individual parcel centroids.