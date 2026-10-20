# Data Cleaning Documentation: San Francisco Land Use Pipeline

**Script:** `clean_sf_land_use.py`  
**Purpose:** Prepares an audited, topologically valid baseline of San Francisco parcels for longitudinal housing analysis (2005–2025) and Family Zoning Plan capacity modeling.  
**Deliverables:** `sf_land_use_clean.gpkg` (Spatial GIS) & `sf_land_use_clean.csv` (Tabular Analysis).

---

### 1. Ingestion Integrity & Key Preservation
* **Leading-Zero Protection**: Parcel identifiers (`mapblklot`) are strictly ingested as strings. This prevents Python from stripping leading zeros (e.g., `'0792033'`), ensuring seamless 1:1 tabular joins with DBI Housing Production records.
* **Numeric Parsing**: Cleaned thousands-separator commas from `residential_units` (e.g., `"1,900"` $\rightarrow$ `1900`) and cast to integers, preventing silent coercion to `NaN` and null-addition calculation failures.

### 2. Variable Selection & Urban Planning Rationales
Out of 23 original fields, 14 non-residential or operational columns were discarded to optimize performance and prevent analytical confusion:
* **Excluded**: Static timestamps (`data_as_of`, `data_loaded_at`), internal database indices (`LUDB_id`), and non-housing commercial/open space metrics (`cie`, `retail`, `pdr`, `parking_lot`, etc.).
* **Retained Core Policy Variables**:
  * `major_multiphase_project`: Essential control variable marking mega-projects governed by binding Development Agreements (e.g., Mission Bay, Treasure Island). Isolates projects unaffected by citywide zoning amendments.
  * `special_jurisdiction`: Flags state/federal entities (e.g., Presidio, UCSF, SFSU) with statutory immunity (State/Federal Preemption) from municipal zoning.
  * `residential_use`: Diagnostic marker identifying non-standard accommodations (SRO hotels, student housing, senior group quarters) for neighborhood inequality and sensitivity analysis.
* **Preserving Zero-Unit Parcels (`residential_units == 0`)**: 14,278 parcels with zero baseline units were deliberately **retained**. Deleting them would erase commercial corridors and low-density lots that are the primary targets of the 2026 Family Zoning Plan's upzoning capacity.

### 3. Defensive Schema Transformation: Special Units
* **The Dilemma**: 46 parcels contain `residential_units_special` (4,631 total beds/dorm units), while their standard `residential_units` is 0. 
* **The Solution**: Merging special units into conventional stock would violate Census ACS definitions (Group Quarters vs. Housing Units). To prevent team members from accidentally summing beds and family apartments, the numeric column was transformed into a boolean flag:
  $$\text{has\_special\_residential\_units} = (\text{residential\_units\_special} > 0)$$
  The raw numeric column was safely retired while preserving all 46 parcel geometries and baseline zero counts.

### 4. Topological Geometry Repair
GEOS validation detected **5 topologically invalid geometries** (4 self-intersections, 1 collapsed sliver). Rather than naive row deletion—which would have erroneously erased **182 legally occupied housing units** (62 units in Visitacion Valley; 120 units in Hayes Valley)—the pipeline applied `shapely.validation.make_valid`:
* Resolved sub-millimeter self-intersections caused by multi-parcel CAD-to-GIS spatial dissolves.
* Preserved 100% of the parcels' centroids and physical dwelling counts without spatial drift.

### 5. Ground-Truth Audit Deduplication
To resolve 11 conflicting duplicate parcel identifiers (22 records), the pipeline rejected arbitrary algorithmic heuristics (e.g., blanket `max()`). Instead, it executes an empirical lookup grounded in DBI Certificates of Final Completion (CFC) and Assessor tax rolls:
* Resolved phase mismatches in HOPE SF public housing redevelopments (Sunnydale & Potrero Hill), preserving verified replacement additions while retiring obsolete demolition placeholders.
* Corrected administrative overcounting (e.g., rectory church lot `7138055` calibrated to 1 legal unit instead of 4).
* Achieved exact, net deduplication of 11 rows ($153,765 \rightarrow 153,754$).

### 6. Feature Engineering (Policy & Inequality Controls)
Three boolean indicators were generated to support downstream econometric modeling and sensitivity testing:
1. `is_megaproject`: Distinguishes master-planned agreement sites from standard market-rate infill.
2. `is_special_housing`: Flags SROs, dormitories, and senior living for vulnerable population analyses.
3. `is_special_jurisdiction`: Identifies jurisdictional enclaves outside municipal planning control.

### 7. Quality Assurance (Triple Assertions) & Export
Before writing deliverables, the script enforces three hard runtime assertions:
1. **Uniqueness**: `mapblklot` is 100% unique (Primary Key verified).
2. **Topology**: `gdf.geometry.is_valid.all() == True` (Zero invalid geometries).
3. **Completeness**: `residential_units` contains zero null values.

**Dual Outputs**:
* **`sf_land_use_clean.gpkg`**: High-performance spatial layer preserving full MultiPolygons for tract-level spatial joins and Midterm choropleth maps.
* **`sf_land_use_clean.csv`**: Lightweight tabular file (polygons stripped, centroids retained) for instant tabular merges with DBI housing permit datasets.