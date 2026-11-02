import pandas as pd


def clean_housing_data(housing):
    """Step 1a: Keep the original dates, signed nonzero changes, and column names."""
    def clean_housing_data(housing):
    """Filter housing production records completed from 2005 through 2025."""
    housing = housing.copy()

    housing["First Completion Date"] = pd.to_datetime(housing["First Completion Date"], errors="coerce",)
    housing["Net Units Completed"] = pd.to_numeric(housing["Net Units Completed"], errors="coerce",)

    in_period = (housing["First Completion Date"] >= "2005-01-01") & (housing["First Completion Date"] < "2026-01-01")

    valid_units = (housing["Net Units Completed"].notna()) & (housing["Net Units Completed"] != 0)

    return housing.loc[in_period & valid_units].copy()


def clean_land_use(land):
    """Step 1b: Keep the original missing-value and parcel-conflict rules."""
    land["missing_parcel_id"] = land["mapblklot"].isna()
    land["missing_residential_units"] = land["residential_units"].isna()
    land = land.loc[~land["missing_parcel_id"]].copy()
    land["residential_units"] = land["residential_units"].fillna("0")
    
    clean_unit_values = []
    
    for value in land["residential_units"]:
        clean_unit_values.append(int(value.replace(",", "")))
    land["residential_units"] = clean_unit_values

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
    return land


def clean_dbi_coordinates(dbi_records):
    """Step 2c: Keep primary located records and remove duplicate or ambiguous points."""
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

    dbi = pd.DataFrame(rows, columns=["BPA", "dbi_latitude", "dbi_longitude"])
    dbi = dbi.drop_duplicates()
    dbi = dbi.drop_duplicates(subset="BPA", keep=False)
    print("Unique DBI permit coordinates:", len(dbi))
    return dbi


def select_sf_tracts(table):
    """Shared ACS cleaning: select SF tracts, extract GEOID, and deduplicate."""
    table = table.loc[table["GEO_ID"].str.startswith("1400000US06075")].copy()
    table["GEOID"] = table["GEO_ID"].str[-11:]
    table = table.drop_duplicates(subset="GEOID")
    return table


def clean_tenure_data(tenure):
    """Step 6a: Clean ACS IDs and numeric counts and keep valid occupied/renter totals."""
    tenure = select_sf_tracts(tenure)
    tenure["total"] = pd.to_numeric(tenure["B25003_001E"], errors="coerce")
    tenure["renter"] = pd.to_numeric(tenure["B25003_003E"], errors="coerce")
    tenure = tenure.loc[(tenure["total"] > 0) & tenure["renter"].between(0, tenure["total"])].copy()
    return tenure


def clean_income_data(income):
    """Step 6b: Clean ACS IDs and income strings and retain usable estimates."""
    income = select_sf_tracts(income)
    income["median_income"] = pd.to_numeric(income["B19013_001E"].str.replace(",", "", regex=False).str.replace("+", "", regex=False),errors="coerce")
    income_clean = income.loc[income["median_income"].notna(),["GEOID", "median_income"]].copy()
    print("Valid income tracts:", len(income_clean))
    return income_clean


