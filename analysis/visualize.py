"""The notebook's original plot code, enclosed in functions without new plotting rules."""

import matplotlib.pyplot as plt
import seaborn as sns


def plot_housing_map(tract_production):
    """Figure 1: Original net housing additions map."""
    # Visualization 1: Net Housing Additions by Census Tract (2005-2025)

    # Create the map
    fig, ax = plt.subplots(figsize=(9, 10))

    # Plot net housing additions
    tract_production.plot(
        column="net_units_added_2005_2025",
        cmap="Blues",
        vmin=0,
        legend=True,
        legend_kwds={"shrink": 0.6, "label": "Net Housing Units"},
        ax=ax,
        edgecolor="lightgray",
        linewidth=0.4
    )

    # Highlight tracts with negative net housing changes
    tract_production[tract_production["net_units_added_2005_2025"] < 0 ].plot(ax=ax, color="indianred", edgecolor="lightgray")

    # Focus on mainland San Francisco
    ax.set_xlim(-122.53, -122.34)
    ax.set_ylim(37.69, 37.84)

    # Add title and remove axes
    ax.set_title("Net Housing Additions by Census Tract (2005-2025)\nRed = Net Housing Losses",fontsize=14)
    ax.set_axis_off()

    # Save and display
    plt.figtext(0.5, -0.02, "Figure 1. Net housing additions were concentrated in eastern San Francisco during 2005–2025. Darker blue represents larger net increases in housing units, while red identifies census tracts with net housing losses.",
                ha="center", fontsize=9)
    plt.tight_layout()
    plt.savefig("historical_net_additions_map.png", dpi=300, bbox_inches="tight")
    plt.show()


def plot_group_comparison(group_comparison, unassigned_net_units):
    """Figure 2: Original group comparison."""
    # Figure 2: Net housing additions by recent income and renter-share groups.
    fig, axes = plt.subplots(1, 2, figsize=(13, 6), sharey=True)

    for ax, dimension, order, title in [
        (axes[0], "income", ["low", "middle", "high", "unclassified"], "By income"),
        (axes[1], "renter", ["low_renter", "middle_renter", "high_renter", "unclassified"], "By renter share")
    ]:
        # Put categories in the same order on both charts.
        subset = group_comparison.loc[group_comparison["dimension"] == dimension].set_index("group").reindex(order)
        bars = ax.bar([0, 1, 2, 3], subset["net_units"], color=["lightgray", "lightgray", "steelblue", "whitesmoke"], edgecolor="gray")
        ax.set_xticks([0, 1, 2, 3], ["Low", "Middle", "High", "Unclassified"])
        ax.set_title(title)
        ax.set_ylabel("Net housing units" if dimension == "income" else "")

        # Label each bar with net units and its share of the citywide net total.
        for bar, units, share in zip(bars, subset["net_units"], subset["share_city_net_pct"]):
            ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                    f"{units:,.0f}\n{share:.1f}%", ha="center", va="bottom", fontsize=9)

    fig.suptitle("Net Housing Additions by 2020-2024 ACS Groups (2005-2025)", fontsize=14)
    fig.text(0.5, 0.01, f"Figure 2.Net housing additions during 2005–2025 were highest in the highest-income and highest-renter-share tract groups, classified using 2020–2024 ACS estimates.\nUnassigned to any tract: {unassigned_net_units:,.0f} signed net units (not shown in bars).", ha="center", fontsize=9)
    plt.tight_layout(rect=[0, 0.05, 1, 0.94])
    plt.savefig("housing_additions_by_acs_groups.png", dpi=300, bbox_inches="tight")
    plt.show()


def plot_net_additions_distribution(tract_production):
    """Figure 3: Original histogram and KDE."""
    # Histogram: distribution of 2005-2025 net housing additions across tracts
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(10, 6))
    sns.histplot(tract_production["net_units_added_2005_2025"],bins=30, kde=True, color="steelblue", edgecolor="black")

    plt.title("Distribution of Net Housing Additions Across SF Census Tracts (2005-2025)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Net Housing Additions per Tract (Units)", fontsize=12)
    plt.ylabel("Number of Census Tracts (Count)", fontsize=12)

    plt.figtext(0.5, -0.03,
        "Figure 3. Net housing additions across San Francisco census tracts, 2005–2025, were strongly right-skewed: most tracts recorded small increases, while a few experienced much larger additions.",
        wrap=True, horizontalalignment="center", fontsize=10, fontstyle="italic")

    plt.tight_layout()
    plt.savefig("net_housing_additions_distribution.png", dpi=300, bbox_inches="tight")
    plt.show()


def plot_top_tracts(tract_production):
    """Figure 4: Original top-ten chart."""
    # Horizontal bars: top 10 tracts by net housing additions, not growth rates
    top_growth = tract_production.nlargest(10, "net_units_added_2005_2025")
    plt.figure(figsize=(11, 6))
    plt.barh(
        y=top_growth["GEOID"].astype(str),
        width=top_growth["net_units_added_2005_2025"],
        color="darkorange", edgecolor="black"
    )
    plt.gca().invert_yaxis()
    plt.title("Top 10 San Francisco Census Tracts by Net Housing Additions (2005-2025)", fontsize=14, fontweight="bold", pad=15)
    plt.xlabel("Net Housing Additions (Units)", fontsize=12)
    plt.ylabel("Census Tract GEOID", fontsize=12)
    plt.figtext(0.5, -0.04,
        "Figure 4. Top ten San Francisco census tracts by net housing additions, 2005–2025. Tract 06075060701 recorded the largest net increase, with 4,251 units.",
        wrap=True, horizontalalignment="center", fontsize=10, fontstyle="italic")
    plt.tight_layout()
    plt.savefig("top_10_net_housing_additions_tracts.png", dpi=300, bbox_inches="tight")
    plt.show()


