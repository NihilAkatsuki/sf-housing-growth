"""Repeated group-comparison calculations from the analysis notebook."""

import pandas as pd


def summarize_group(master, group_column, dimension):
    """Apply the original aggregation to either income or renter-share groups."""
    summary = master.groupby(group_column, as_index=False).agg(
        tracts=("GEOID", "size"),
        production_records=("production_records", "sum"),
        net_units=("net_units_added_2005_2025", "sum")
    ).rename(columns={group_column: "group"})
    summary["dimension"] = dimension
    return summary
