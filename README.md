# Housing Growth, Neighborhood Inequality, and Zoning Capacity in San Francisco


# 1\. Research Question

## **Problem Statement**

From 2005 to 2025, how did housing growth vary across San Francisco neighborhoods by income and renter share, and how does the Family Zoning Plan, effective January 12, 2026, allocate additional housing capacity across neighborhoods with different levels of income and historical housing growth?

## **Subaspects of Problem Statement**

1. Which San Francisco neighborhoods experienced the highest and lowest housing growth rates relative to their initial housing stock from 2005–2025?  
2. How did housing growth rates from 2005–2025 vary by neighborhood income and renter share?  
3. How is additional housing capacity under the Family Zoning Plan distributed across neighborhoods with different levels of income and historical housing growth?

# 2\. Data Description

## **1\. [Housing Production \- 2005-present | DataSF](https://data.sfgov.org/widgets/xdht-4php) (Public Domain)**

* **Coverage:** San Francisco housing development data from 2005 to the present, covering building permit applications and housing production across the city.  
* **Granularity:** Project/permit level, with each record corresponding to a building permit application and associated housing project information.  
* **Type:** Structured tabular data, containing categorical, numerical, date, and address/location variables.  
* **Format:** Data is available in a structured, machine-readable format through DataSF, with records organized into rows and variables organized into columns.  
* **Source:** City and County of San Francisco, through DataSF.

**Relevance:** This dataset provides information on housing production over our 2005–2025 time period. The relevant columns include Building Permit Application Number, Address, BlockLot, Affordable Units, Market Rate Units, Issued Date, Zoning District, and Project Affordability Type. We can use the address and permit information to identify where housing was produced, what type of housing was produced, and the number and type of units associated with each project.

## **2\. [San Francisco Land Use | DataSF](https://data.sf.gov/Geographic-Locations-and-Boundaries/San-Francisco-Land-Use/c5ge-t6pj/about_data) (Public Domain)**

* **Coverage:** Land use across San Francisco, including residential, commercial, mixed-use, and other land-use categories.  
* **Granularity:** Parcel level, with individual records representing land parcels within San Francisco.  
* **Type:** Structured geospatial/tabular data, containing land-use classifications and parcel-level geographic information.  
* **Format:** Structured geospatial data that can be joined with other datasets using geographic or parcel information.  
* **Source:** City and County of San Francisco, through DataSF.

**Relevance:** This dataset helps provide geographic context for housing development by identifying the land uses associated with different areas of San Francisco. The relevant columns include mapblklot, residential\_units, residential\_use, and geography\_type. We can use it alongside the housing production data to understand where housing development occurs and connect housing growth to neighborhood characteristics.

## **3\. American Community Survey (ACS) 5-Year Estimates (Public Domain)**

* **Coverage**: Socioeconomic and housing characteristics for census tracts in San Francisco County. Two tables are used: [Median Household Income in the Past 12 Months](https://data.census.gov/table/ACSDT5Y2020.B19013?q=B19013&g=040XX00US06_050XX00US06075,06075$1400000) (referred to as B19013) and [Tenure: Owner-Occupied vs. Renter-Occupied Units](https://data.census.gov/table?q=B25003+&g=040XX00US06,06$1400000_050XX00US06075,06075$1400000) (referred to as B25003).  
* **Granularity**: Census tract level, with one record per tract.  
* **Type**: Structured tabular data. B19013 provides a single median income estimate per tract. B25003 provides counts of total occupied units, owner-occupied units, and renter-occupied units per tract, from which we calculate renter share.  
* **Format**: Downloadable CSV   
* **Source**: U.S. Census Bureau, American Community Survey, 2024 5-Year Estimates (covering 2020–2024).

**Relevance**: These two tables supply the neighborhood-level socioeconomic characteristics that are central to our research questions. B19013 allows us to classify tracts by income level, and B25003 allows us to classify tracts by renter share. Using these datasets, we can compare whether historically lower-income or higher-renter-share neighborhoods experienced different levels of housing growth and whether the Family Zoning Plan allocates future capacity differently across these groups.

## 4. [Census 2020: Tracts for San Francisco | DataSF](https://data.sf.gov/Geographic-Locations-and-Boundaries/Census-2020-Tracts-for-San-Francisco/tmph-tgz9/about_data) (Public Domain)

- **Coverage:** Geographic boundaries of the 244 census tracts in San Francisco, based on the 2020 U.S. Census.
- **Granularity:** Census tract level, with one record representing each tract.
- **Type:** Structured geospatial data containing tract identifiers and polygon geometries.
- **Format:** Downloadable CSV containing geographic boundaries in WKT format.
- **Source:** City and County of San Francisco, through DataSF, based on U.S. Census Bureau 2020 boundaries.

**Relevance:** This dataset provides consistent geographic boundaries for our neighborhood-level analysis. The relevant columns include `GEOID` and `the_geom`. We use spatial joins to assign housing production records and land-use parcels to census tracts, allowing us to aggregate housing units by tract and connect housing growth with ACS income and renter-share data.

# 3\. Methods & Techniques

## **Method**

Our goal is to measure how many housing units each census tract gained from 2005 to 2025, compare the growth rates across tracts grouped by income and renter share, and examine whether the Family Zoning Plan allocates future capacity differently. We chose census tracts to serve as the geographic unit because they align with ACS socioeconomic data.

**Step 1: Clean and filter the data**. In the Housing Production dataset, filter records to only those with a First Completion Date between 2005 and 2025\. Remove records with missing or zero Net Units Completed. In the San Francisco Land Use table, check for parcels with missing values in the “residential\_units” or “mapblklot” columns and drop or flag them. We will identify permits with a missing or unmatched BlockLot during the join in Step 2 and report them in the validation checks.

**Step 2: Give each permit a location (Tabular** **join)**. The Housing Production dataset tells how many units each permit added(“Net Units Completed”), and it only has an address and a parcel ID but no coordinates. The Land Use dataset has parcel shapes and the same parcel ID (“BlockLot” in Housing Production, “mapblklot” in Land Use). We match the 2 tables on this shared column, so every permit gets a location on the map. 

**Step 3: Add up units by tract**. Group permits by tract and sum their “Net Units Completed” column. Now each tract has one number: how many net housing units it gained over 20 years, which answers our question of which tracts gained the most and least housing.

**Step 4: Figure out the starting point**. The Land Use table has a column “residential\_units.” We add those up by tract to get each tract’s baseline housing stock. Since the Land Use data starts from 2008, we subtract units built between 2005 and 2008 to get the 2005 starting count.

**Step 5: Calculate the growth rate**.  $Growth\ Rate\ =\ (Net\ Units\ Added\ from\ 2005\ to\ 2025\div Baseline\ Housing\ Stock)\ ×\ 100$

**Step 6: Classify tracts**. Our 2 datasets from ACS: Median Household Income in the Past 12 Months and Tenure: Owner-Occupied vs. Renter-Occupied Units. We are going to split all tracts into 3 equal-sized groups(“low,””medium,” and “high”) by income and by renter share *(renter share \= renter-occupied units ÷ total occupied units)*.

**Step 7: Compare shares**. For each group we separated above, we are going to compare the percentage belonging to tracts for the housing units that existed in San Francisco in 2005 (before any new building) with the percentage for the net new housing units built citywide 2005-2025.

**Step 8: Do the same for the Family Zoning Plan**. The Family Zoning Plan was effective in January 2026\. It changes zoning rules across San Francisco County, allowing some areas to build more housing than they were allowed to before. We filter the data from January 2026 to the present day to see how many additional units each parcel or zoning district can now support under the new rules, and then add it up by tract and do the same step from Step 7\. Using this information, we will then model the redistribution of San Francisco’s family housing capacity after the plan using an interactive map using Plotly.

## **Validation**

1. **Are our numbers right?** Before calculating renter share and growth rates, check whether any tract has a denominator of zero. We flag these tracts with denominator zero, exclude them from the grouped comparisons, and report how many were removed.  
2. **Is our data clean?**   
   1. We may have duplicate records: a large project might be split across multiple permits, all sharing the same BlockLot.   
   2. We may have unmatched permits: some permits' BlockLot might not match any parcel in the Land Use table. These permits have no location and can't enter any tract. We flag them and check how many there are and whether they're big enough to matter.  
3.  **Do our results hold up if we make different choices?**   
   1. Change the grouping: re-run with four groups (quartiles) instead of three (terciles). If the results flip completely, our conclusions depend too much on how we drew the lines.   
   2. Remove extreme cases: some tracts started with very few units (under 50). One additional unit there can significantly increase the growth rate, which skews the whole group. We pull these tracts out and check separately.

## **Visualization**

1. **Choropleth map** of tract-level growth rates (GeoPandas / Matplotlib): Shows whether high-growth tracts cluster along the eastern waterfront or scatter citywide.  
2. **Paired bar chart** (using Seaborn): each group's share of initial stock VS. share of new housing. Two bars side by side for each income or renter-share group make any proportional gap immediately visible.   
3. **Grouped bar chart** of Family Zoning Plan capacity by income group and historical-growth level (using Seaborn). Shows whether the plan redirects capacity toward higher-income, low-growth tracts. Labeled clearly as projected capacity and uses a different color scheme from the historical charts so the reader never confuses planned capacity with completed housing. 

# 4\. Timeline & Milestones

* **By September 30:** Collect and inspect the Housing Production, ACS, census tract, and Family Zoning Plan datasets; confirm that usable pre- and post-plan zoning data are available (All).  
* **By October 15:** Clean the datasets (Tanushri), standardize geographic boundaries (Colton), and spatially join housing projects to census tracts (Luoqi).  
* **By October 31:** Complete the preliminary historical housing-growth analysis and prepare initial results (Tanushri), maps (Luoqi), and methodology (Colton) for the midterm submission.  
* **By November 2:** Submit the midterm project update and use feedback to refine the analysis plan (All).  
* **By November 15:** Complete the socioeconomic analysis by comparing housing growth across income (Tanushri) and renter-share groups (Luoqi).  
* **By November 30:** Complete the Family Zoning Plan analysis (Tanushri), sensitivity checks (Luoqi), and final maps and visualizations (Colton).  
* **By December 7:** Complete the full analysis and final report, including revisions, figures, citations, and proofreading; reserve December 8–15 only as a buffer before final submission (All).

# 5\. Potential Challenges & Mitigation Plan

| Potential Challenge | Mitigation Plan |
| ----- | ----- |
| **Geographic consistency:** Census tract boundaries may change over time, which can create inconsistent comparisons across years. | Use one consistent census tract throughout the project and spatially join all housing records to the same tract boundaries. |
| **Small baseline housing stocks:** Tracts with very little housing at the beginning of the study period may show unusually large percentage growth. | Report both absolute housing additions and percentage growth rates, and examine extreme outliers separately. |
| **ACS uncertainty:** Income and renter-share estimates contain sampling uncertainty, especially at the census tract level. | Use ACS five-year estimates and consider margins of error when classifying and comparing tracts. |
| **Zoning data availability and interpretation:** Directly comparable estimates of housing capacity before and after the Family Zoning Plan may not be available. In addition, added zoning capacity does not necessarily result in actual housing construction. | Verify that pre- and post-plan capacity data are comparable before using them. If necessary, limit the analysis to rezoning coverage and clearly distinguish zoning capacity from completed housing. |
| **Interpretation and ethical framing:** Housing growth should not automatically be interpreted as beneficial (for example, housing growth in one area could result in displacement and resource depletion). | Use neutral language, distinguish observed development patterns from causal claims, and avoid treating housing growth itself as inherently positive. |
| **Limited post-policy data:** The Family Zoning Plan only took effect in January 2026, so there may not be enough post-implementation data to observe meaningful changes in actual housing development. | Focus the analysis on changes in zoning capacity and geographic allocation rather than short-term construction outcomes, and clearly state that longer-term effects cannot yet be measured. |
