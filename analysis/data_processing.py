"""Housing analysis from the supplied notebook. Run from the project root.

Only function boundaries, arguments, returns, and shared repeated steps are new.
Source filters, matching rules, calculations, and output paths are retained.
"""

import json
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


def prepare_housing_data(housing_path="data/raw/housing_production.csv"):
    """Step 1a: Read, filter, rename, and save Housing Production."""
    # Read each permit as text, especially BlockLot (leading zeros are meaningful).
    housing = pd.read_csv(housing_path, dtype={"bpa": str, "blocklot": str})
    housing

    # Housing Produciton data cleaning

    # covert to datetime & numeric
    housing["first_completion_date"] = pd.to_datetime(housing["first_completion_date"])
    housing["net_units_completed"] = pd.to_numeric(housing["net_units_completed"])

    # Keep the study period, known nonzero changes, and all housing losses.
    in_period = (housing["first_completion_date"] >= "2005-01-01") & (housing["first_completion_date"] < "2026-01-01")
    valid_units = (~housing["net_units_completed"].isna()) & (housing["net_units_completed"] != 0)

    selected = housing.loc[in_period & valid_units].copy()

    # rename each column
    housing_production_filtered = selected.rename(columns={
        "bpa": "BPA", 
        "address": "Address", 
        "blocklot": "BlockLot",
        "net_units_completed": "Net Units Completed",
        "first_completion_date": "First Completion Date", "latest_completion_date": "Latest Completion Date"
    })

    # save filtered housing production dta as csv file

    housing_production_filtered.to_csv("data/processed/housing_production_filtered.csv", index=False)

    print("Study records:", len(housing_production_filtered))
    print("Source net housing additions:", housing_production_filtered["Net Units Completed"].sum())

    housing_production_filtered

    return housing_production_filtered


def prepare_land_use(land_path="data/raw/San_Francisco_Land_Use.csv"):
    """Step 1b: Keep the original Land Use cleaning and parcel decisions."""
    # Read parcel IDs as strings so the Land Use join keeps leading zeros.
    land = pd.read_csv(land_path,dtype={"mapblklot": str, "residential_units": str}, low_memory=False)
    land

    # Flag missing fields before applying the original cleaning rule.
    land["missing_parcel_id"] = land["mapblklot"].isna()
    land["missing_residential_units"] = land["residential_units"].isna()
    land = land.loc[~land["missing_parcel_id"]].copy()
    land["residential_units"] = land["residential_units"].fillna("0")
    clean_unit_values = []
    for value in land["residential_units"]:
        clean_unit_values.append(int(value.replace(",", "")))
    land["residential_units"] = clean_unit_values

    # Retain the original teammate's parcel-conflict decisions.
    AUDIT_RETAIN = {
        "1761053": 2, "3180214": 71, "6310010": 69, "6310011": 108,
        "6311014": 4, "6311016": 170, "6311026": 4, "7138055": 1,
        "4285B003": 1, "4285B004": 157
    }
    for parcel_id, retained_units in AUDIT_RETAIN.items():
        remove = (land["mapblklot"] == parcel_id) & (land["residential_units"] != retained_units)
        land = land.loc[~remove].copy()
    land = land.drop_duplicates(subset="mapblklot", keep="first")
    land = land[["mapblklot", "centroid_latitude", "centroid_longitude", "residential_units","geography_type", "missing_parcel_id", "missing_residential_units"]]

    # save filtered land as sf_land_use_clean.csv
    land.to_csv("data/processed/sf_land_use_clean.csv", index=False)
    print("Cleaned Land Use records:", len(land))

    land.head()

    return land


def match_land_use(housing_production_filtered, land):
    """Step 2a-b: Match individual parcels first, then eligible parcel groups."""
    # Join Housing Production to single-parcel Land Use centroids by BlockLot.
    single = land.loc[land["geography_type"] == "parcel", ["mapblklot", "centroid_latitude", "centroid_longitude"]].rename(columns={"centroid_latitude": "latitude", "centroid_longitude": "longitude"})

    located = housing_production_filtered.merge(single, left_on="BlockLot", right_on="mapblklot", how="left")
    located = located.drop(columns="mapblklot")
    single_match = (~located["latitude"].isna()) & (~located["longitude"].isna())
    located["match_status"] = "unmatched"
    located["match_note"] = "no_parcel_match"
    located.loc[single_match, "match_status"] = "matched_single"
    located.loc[single_match, "match_note"] = "parcel_centroid"

    multi = land.loc[land["geography_type"] == "multiple_parcels"].copy()
    rows = []

    for raw, lat, lon in zip(multi["mapblklot"], multi["centroid_latitude"], multi["centroid_longitude"]):
        if pd.isna(lat) or pd.isna(lon):
            continue

        parts = str(raw).split(",")
        parcel_ids = []
        complete_list = True
        for part in parts:
            part = part.strip()
            if len(part) >= 3 and part[0] == "'" and part[-1] == "'":
                parcel_ids.append(part[1:-1])
            else:
                complete_list = False

        if complete_list and len(parcel_ids) >= 2:
            for parcel_id in parcel_ids:
                rows.append([parcel_id, lat, lon])

    multi_candidates = pd.DataFrame(rows, columns=["BlockLot", "multi_latitude", "multi_longitude"])
    multi_candidates = multi_candidates.drop_duplicates()

    # One BlockLot may appear at more than one location: do not guess which is right.
    counts = multi_candidates.groupby("BlockLot").size().reset_index(name="locations")
    multi_candidates = multi_candidates.merge(counts, on="BlockLot", how="left")
    multi_candidates = multi_candidates.loc[multi_candidates["locations"] == 1].copy()

    # A left merge keeps every housing record.
    located = located.merge(
        multi_candidates[["BlockLot", "multi_latitude", "multi_longitude"]],
        on="BlockLot", how="left"
    )
    fill = (located["match_status"] == "unmatched") & located["multi_latitude"].notna() & located["multi_longitude"].notna()
    located.loc[fill, "latitude"] = located.loc[fill, "multi_latitude"]
    located.loc[fill, "longitude"] = located.loc[fill, "multi_longitude"]
    located.loc[fill, "match_status"] = "matched_multi_centroid"
    located.loc[fill, "match_note"] = "Land Use group centroid"
    located = located.drop(columns=["multi_latitude", "multi_longitude"])

    print("Multi-parcel matches:", fill.sum())
    print("Housing records still unmatched:", (located["match_status"] == "unmatched").sum())

    # Save the initial Land Use matches before supplemental DBI coordinates.
    located.to_csv("data/processed/housing_production_located.csv", index=False)

    print(located["match_status"].value_counts())
    located.head()

    return located


def prepare_dbi_coordinates(dbi_path="data/raw/dbi_all_study_permit_coordinates.json"):
    """Step 2c: Read primary-address coordinates and keep unambiguous permits."""
    # Step 2c: Get permit coordinates from DBI

    # Read DBI data
    with open(dbi_path, encoding="utf-8") as file:
        dbi_records = json.load(file)

    # Keep primary-address records with coordinates
    rows = []

    for record in dbi_records:

        if record.get("primary_address_flag") == "Y" and record.get("location") is not None:
            coordinates = record["location"].get("coordinates")
        
            if coordinates is not None and len(coordinates) >= 2:
                rows.append([
                    str(record["permit_number"]),  # Building Permit Application number (BPA)
                    coordinates[1],               # Latitude (second value)
                    coordinates[0]                # Longitude (first value)
                ])


    # Create a DataFrame
    dbi = pd.DataFrame(rows, columns=["BPA", "dbi_latitude", "dbi_longitude"])

    # Remove identical records
    dbi = dbi.drop_duplicates()

    # Remove permits with multiple different locations
    dbi = dbi.drop_duplicates(subset="BPA", keep=False)

    print("Unique DBI permit coordinates:", len(dbi))

    return dbi


def recover_dbi_locations(located, dbi):
    """Step 2c: Fill only missing locations, retain records, and save summaries."""
    # Remember original Land Use matching results before DBI fills missing points.
    located["land_use_match_status"] = located["match_status"]

    original_unmatched = located.loc[located["match_status"] == "unmatched"].copy()
    print("Before DBI - unmatched records:", len(original_unmatched))
    print("Before DBI - unmatched net units:", original_unmatched["Net Units Completed"].sum())

    # Step 2c: Fill missing housing coordinates using DBI

    # Join DBI coordinates to Housing Production using BPA.
    located = located.merge(dbi, on="BPA", how="left")

    # Find records with missing coordinates that DBI can provide.
    dbi_fill = ((located["latitude"].isna() | located["longitude"].isna()) & located["dbi_latitude"].notna()& located["dbi_longitude"].notna())

    # Fill missing housing locations with DBI coordinates.
    located.loc[dbi_fill, "latitude"] = located.loc[dbi_fill, "dbi_latitude"]
    located.loc[dbi_fill, "longitude"] = located.loc[dbi_fill, "dbi_longitude"]

    # Update the matching results.
    located.loc[dbi_fill, "match_status"] = "matched_dbi"
    located.loc[dbi_fill, "match_note"] = "DBI primary address; one unique coordinate"

    # Remove temporary DBI columns.
    located = located.drop(columns=["dbi_latitude", "dbi_longitude"])

    # Record the final location source based on match_status.
    located["location_source"] = located["match_status"].replace({
        "matched_single": "land_use_single",
        "matched_multi_centroid": "land_use_group_centroid",
        "matched_dbi": "dbi_primary",
        "unmatched": "unlocated"
    })

    # Check the final matching results.
    print("Records recovered using DBI:", dbi_fill.sum())
    print("Total housing records:", len(located))
    print(located["location_source"].value_counts())

    print("Net units still unmatched:", located.loc[located["match_status"] == "unmatched", "Net Units Completed"].sum())

    # Preserve unmatched records for the professor's validation checks.
    unmatched = located.loc[located["match_status"] == "unmatched"].copy()
    unmatched.to_csv("data/processed/unmatched_housing_records.csv", index=False)
    located.to_csv("data/processed/housing_production_located_recovered.csv", index=False)

    location_summary = located.groupby("location_source")["Net Units Completed"].agg(["count", "sum"])
    location_summary.to_csv("data/processed/location_source_summary.csv")
    location_summary

    return located, location_summary


def assign_census_tracts(located, tract_path="data/raw/census_2020_tracts_raw.geojson"):
    """Step 3: Assign points to 2020 tracts using the original within join."""
    # Step 3: Assign Housing Production Records to 2020 Census Tracts(spatial join)

    # Import Point to create geographic points from coordinates.

    # Load the 2020 Census Tract 
    tracts = gpd.read_file(tract_path)

    # Rename the columns to match the names used in our project.
    tracts = tracts.rename(columns={"geoid": "GEOID", "name": "NAME"})

    # Convert tract geometries to EPSG:4326 (longitude and latitude).
    tracts = tracts.to_crs("EPSG:4326")

    # Give each housing record a unique ID for the tract join.
    located["source_row_id"] = range(len(located))
    has_coordinates = located["latitude"].notna() & located["longitude"].notna()

    # Keep the source_row_id of records with valid coordinates.
    # source_row_id identifies each original Housing Production row.
    point_rows = located.loc[located["latitude"].notna() & located["longitude"].notna(), ["source_row_id"]].copy()

    # Create an empty list to store geographic Point objects.
    points = []

    # Loop through the longitude and latitude of each located housing record.
    # zip() pairs each longitude with its corresponding latitude.
    for lon, lat in zip(located.loc[has_coordinates, "longitude"], located.loc[has_coordinates, "latitude"]):

        # Create a geographic point and add it to the list.
        # Point() takes longitude first, then latitude.
        points.append(Point(lon, lat))

    # Create a GeoDataFrame containing the housing points.
    # Each row has a source_row_id and a Point geometry.
    housing_points = gpd.GeoDataFrame(
        point_rows,
        geometry=points,
        crs="EPSG:4326"
    )

    # Spatial Join: assign each housing point to a Census Tract.
    # "within" checks whether the point falls inside a tract polygon.
    # how="left" keeps all housing points, even if no tract is matched.
    housing_joined = gpd.sjoin(
        housing_points,
        tracts[["GEOID", "geometry"]],
        how="left",
        predicate="within"
    )

    # Count the number of housing records with coordinates.
    print("Housing points:", len(housing_points))

    # Check the number of rows after the Spatial Join.
    # This helps identify whether any housing points matched multiple tracts.
    print("Rows after spatial join:", len(housing_joined))

    # Check whether source_row_id is duplicated in the original located DataFrame.
    # Each source_row_id should identify one Housing Production record.
    print("Repeated source IDs after spatial join:", housing_joined["source_row_id"].duplicated().sum())

    # Join the Census Tract GEOID back to the original Housing Production records.
    # Match using source_row_id, keeps all original records, including those without a GEOID.
    detailed = located.merge(housing_joined[["source_row_id", "GEOID"]], on="source_row_id",how="left")

    # Save the Housing Production records with their assigned Census Tract GEOIDs.
    detailed.to_csv("data/processed/housing_production_with_tract.csv",index=False)

    # Compare Land Use matching and final DBI + Spatial Join
    # Identify matched records at each stage
    land_match = detailed["land_use_match_status"] != "unmatched"
    final_match = detailed["GEOID"].notna()

    # Housing units
    units = detailed["Net Units Completed"]

    # Create a summary table
    join_summary = pd.DataFrame({
        "stage": ["Land Use only", "After DBI + tract join"],
        "assigned_records": [land_match.sum(), final_match.sum()],
        "unassigned_records": [(~land_match).sum(), (~final_match).sum()],
        "assigned_net_units": [units[land_match].sum(), units[final_match].sum()],
        "unassigned_net_units": [units[~land_match].sum(), units[~final_match].sum()]
    })

    # Save and display results
    join_summary.to_csv("data/processed/housing_join_summary.csv", index=False)
    join_summary

    return detailed, tracts, join_summary


def aggregate_by_tract(detailed, tracts):
    """Step 4: Sum signed housing changes and retain all 244 tracts."""
    # Step 4: Aggregate housing production by Census Tract

    # Keep only housing records that have been assigned a Census Tract GEOID.
    # .copy() creates a separate DataFrame without changing detailed.
    assigned = detailed.loc[~detailed["GEOID"].isna()].copy()

    # Create two new columns to separately track housing additions and losses.
    # Start both columns at zero for every housing record.
    assigned["positive_net_units"] = 0
    assigned["negative_net_units_abs"] = 0

    # For records with positive Net Units Completed, record the units added.
    assigned.loc[assigned["Net Units Completed"] > 0,"positive_net_units"] = assigned["Net Units Completed"]

    # For records with negative Net Units Completed, record the housing losses.
    # Multiply by -1 so losses are stored as positive numbers.
    assigned.loc[assigned["Net Units Completed"] < 0,"negative_net_units_abs"] = -assigned["Net Units Completed"]

    # Group housing records by GEOID and sum three columns:
    # 1. Total positive housing additions
    # 2. Total housing losses (as positive numbers)
    # 3. Signed net housing additions (additions minus losses)
    tract_sums = assigned.groupby("GEOID")[["positive_net_units", "negative_net_units_abs", "Net Units Completed"]].sum().reset_index()

    # Rename the net housing column to describe the 2005-2025 study period.
    tract_sums = tract_sums.rename(columns={"Net Units Completed": "net_units_added_2005_2025"})

    # Count how many Housing Production records belong to each Census Tract.
    tract_records = assigned.groupby("GEOID").size().to_frame(name="production_records")

    # Join the record counts to the housing unit totals using GEOID.
    tract_sums = tract_sums.merge(tract_records, on="GEOID", how="left")

    # Join housing production totals to the Census Tract GeoDataFrame.
    # Use a left join to keep all Census Tracts, including those with no
    # assigned housing production records.
    tract_production = tracts.merge(tract_sums, on="GEOID", how="left")

    # List the four columns that contain housing counts and record counts.
    count_columns = [
        "positive_net_units",
        "negative_net_units_abs",
        "net_units_added_2005_2025",
        "production_records"
    ]

    # Replace missing values with 0 for tracts with no matched records.
    # Convert these columns to integers because they represent unit counts.
    tract_production[count_columns] = (tract_production[count_columns].fillna(0).astype(int))

    # Rename NAME to tract_name.
    tract_production = tract_production.rename(columns={"NAME": "tract_name"})

    return tract_production


def save_production_totals(tract_production, detailed):
    """Step 5: Save tract results and calculate full-source and unassigned totals."""
    # Keep full-source and unassigned units separate; the tract table excludes unlocated records.
    tract_production.drop(columns="geometry").to_csv("data/processed/tract_housing_production.csv", index=False)
    city_net_units = detailed["Net Units Completed"].sum()
    unassigned_net_units = detailed.loc[detailed["GEOID"].isna(), "Net Units Completed"].sum()


    print("Full-source net additions:", city_net_units)
    print("Net additions assigned to tracts:", tract_production["net_units_added_2005_2025"].sum())
    print("Net additions without a tract:", unassigned_net_units)

    return city_net_units, unassigned_net_units


def select_sf_tracts(table):
    """Shared ACS operation: select SF tracts, extract GEOID, and keep one row per tract."""
    table = table.loc[table["GEO_ID"].str.startswith("1400000US06075")].copy()
    table["GEOID"] = table["GEO_ID"].str[-11:]
    table = table.drop_duplicates(subset="GEOID")

    return table


def prepare_tenure_data(tenure_path="B25003/ACSDT5Y2024.B25003-Data.csv"):
    """Step 6a: Read tenure, retain the original valid counts, and compute renter share."""
    # Step 6a: Read 2020-2024 ACS tenure (B25003).
    tenure = pd.read_csv(tenure_path, skiprows=[1])
    tenure = select_sf_tracts(tenure)

    # convert to numeric
    tenure["total"] = pd.to_numeric(tenure["B25003_001E"], errors="coerce")
    tenure["renter"] = pd.to_numeric(tenure["B25003_003E"], errors="coerce")

    # filter
    tenure = tenure.loc[(tenure["total"] > 0) & tenure["renter"].between(0, tenure["total"])].copy()

    # Renter share = renter-occupied units / total occupied units.
    tenure["renter_share"] = tenure["renter"] / tenure["total"]

    tenure = tenure[["GEOID", "renter_share"]]

    print("Valid tenure tracts:", len(tenure))

    return tenure


def prepare_income_data(income_path="data/raw/ACSDT5Y2024.B19013-Data.csv"):
    """Step 6b: Read and clean income using the original string and numeric rules."""
    # Step 6b: Read 2020-2024 ACS median income (B19013).
    income = pd.read_csv(income_path, skiprows=[1])
    income

    income = select_sf_tracts(income)


    # Clean income values and convert to numbers.
    income["median_income"] = pd.to_numeric(income["B19013_001E"].str.replace(",", "", regex=False).str.replace("+", "", regex=False),errors="coerce")

    # Keep tracts with valid income estimates.
    income_clean = income.loc[income["median_income"].notna(),["GEOID", "median_income"]].copy()

    print("Valid income tracts:", len(income_clean))
    income_clean.head()

    return income_clean


def classify_tracts(tract_production, tenure, income_clean):
    """Step 6c: Keep the original common sample, qcut labels, and unclassified tracts."""
    # Step 6c: Merge the two ACS tables by tract GEOID.
    merged = tenure.merge(income_clean, on="GEOID", how="inner")

    # Divide the same tracts into three equal-sized income and renter-share groups.
    merged["income_group"] = pd.qcut(merged["median_income"], 3, labels=["low", "middle", "high"])
    merged["renter_group"] = pd.qcut(merged["renter_share"], 3, labels=["low_renter", "middle_renter", "high_renter"])

    print("Tracts with both ACS measures:", len(merged))
    print("Income groups:\n", merged["income_group"].value_counts().sort_index())
    print("Renter groups:\n", merged["renter_group"].value_counts().sort_index())

    # Join ACS groups with Housing Production data

    # Merge ACS income and renter groups with housing production by GEOID.
    # Keep all Census Tracts using a left join.
    master = tract_production.merge(merged[["GEOID", "median_income", "renter_share", "income_group", "renter_group"]], on="GEOID",how="left")

    # Replace missing ACS groups with "unclassified".
    for column in ["income_group", "renter_group"]:
        groups = []
        for group in master[column]:
            if pd.isna(group):
                groups.append("unclassified")
            else:
                groups.append(group)

        master[column] = groups

    # Save the results without the geometry column.
    master.drop(columns="geometry").to_csv("data/processed/tract_acs_groups.csv", index=False)

    # Check the number of Census Tracts.
    print("Total tracts:", len(master))
    print("Tracts with ACS groups:", len(merged))

    # Display the first five rows.
    master[["GEOID", "median_income", "renter_share", "income_group", "renter_group"]].head()

    return merged, master


def summarize_group(master, group_column, dimension):
    """Shared Step 7 operation: calculate the same totals for either grouping column."""
    summary = master.groupby(group_column, as_index=False).agg(
        tracts=("GEOID", "size"),
        production_records=("production_records", "sum"),
        net_units=("net_units_added_2005_2025", "sum")
    ).rename(columns={group_column: "group"})
    summary["dimension"] = dimension

    return summary


def compare_groups(master, detailed, city_net_units, unassigned_net_units):
    """Step 7: Keep the original group totals, denominator, and unassigned rows."""
    # Use the same summary function for income and renter share.
    income_summary = summarize_group(master, "income_group", "income")
    renter_summary = summarize_group(master, "renter_group", "renter")

    # Housing records without GEOID are outside both group comparisons.
    unassigned = pd.DataFrame({
        "group": ["unassigned_to_tract", "unassigned_to_tract"],
        "tracts": [0, 0],
        "production_records": [detailed["GEOID"].isna().sum()] * 2,
        "net_units": [unassigned_net_units] * 2,
        "dimension": ["income", "renter"]
    })

    group_comparison = pd.concat([income_summary, renter_summary, unassigned], ignore_index=True)
    group_comparison["share_city_net_pct"] = group_comparison["net_units"] / city_net_units * 100

    group_comparison.to_csv("data/processed/group_housing_comparisons.csv", index=False)
    group_comparison

    return group_comparison


def run_processing():
    """Run the complete original data workflow from the project root."""
    # Step 1: Prepare the same input tables.
    housing_production_filtered = prepare_housing_data()
    land = prepare_land_use()

    # Step 2: Keep Land Use first, with DBI filling only missing locations.
    located = match_land_use(housing_production_filtered, land)
    dbi = prepare_dbi_coordinates()
    located, location_summary = recover_dbi_locations(located, dbi)

    # Steps 3-5: Assign tracts and calculate the same production totals.
    detailed, tracts, join_summary = assign_census_tracts(located)
    tract_production = aggregate_by_tract(detailed, tracts)
    city_net_units, unassigned_net_units = save_production_totals(tract_production, detailed)

    # Step 6: Use the same 2020-2024 ACS classifications.
    tenure = prepare_tenure_data()
    income_clean = prepare_income_data()
    merged, master = classify_tracts(tract_production, tenure, income_clean)

    # Step 7: Compare the same groups and retain the full-source denominator.
    group_comparison = compare_groups(master, detailed, city_net_units, unassigned_net_units)

    return tract_production, group_comparison, unassigned_net_units


if __name__ == "__main__":
    run_processing()
