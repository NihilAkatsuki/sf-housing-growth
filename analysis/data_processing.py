"""Repeated processing steps from the supplied notebook. No automatic execution."""

import pandas as pd


def read_tenure_data():
    """Read the same B25003 CSV wherever the notebook reads it."""
    tenure = pd.read_csv("B25003/ACSDT5Y2024.B25003-Data.csv", skiprows=[1])
    return tenure


def select_sf_tracts(table):
    """Select SF Census Tracts, extract GEOID, and keep one row per GEOID."""
    table = table.loc[table["GEO_ID"].str.startswith("1400000US06075")].copy()
    table["GEOID"] = table["GEO_ID"].str[-11:]
    table = table.drop_duplicates(subset="GEOID")
    return table


def summarize_group(master, group_column, dimension):
    """Use the original aggregation for either income or renter-share groups."""
    summary = master.groupby(group_column, as_index=False).agg(
        tracts=("GEOID", "size"),
        production_records=("production_records", "sum"),
        net_units=("net_units_added_2005_2025", "sum")
    ).rename(columns={group_column: "group"})
    summary["dimension"] = dimension
    return summary
