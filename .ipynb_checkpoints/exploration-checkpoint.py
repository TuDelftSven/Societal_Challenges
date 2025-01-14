import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import time
import seaborn as sns
from fontTools.merge.base import merge
from pysal.lib import weights
from pysal.explore import esda
from splot.esda import moran_scatterplot, lisa_cluster, plot_local_autocorrelation


# Load the data CSV and the GeoPackage shapefile
data_file = 'data/85950NED.csv'
shapefile2021 = 'data/geo/buurten_2021_v3.shp'
wijk_file = "data/WijkenBuurt2021.xlsx"

# Read the CSV and shapefile
data_df = pd.read_csv(data_file, sep=";")
geo_df = gpd.read_file(shapefile2021)
wijk_df = pd.read_excel(wijk_file)

# Filter rows where 'gwb_code_10' contains 'GM'
wijk_df = wijk_df[wijk_df["gwb_code_10"].str.contains("GM", na=False)]


# Ensure that both 'RegioS' and 'gemeentecode' are of the same data type (e.g., strings)
data_df['RegioS'] = data_df['RegioS'].astype(str)
geo_df['GM_CODE'] = geo_df['GM_CODE'].astype(str)

data_df_2021 = data_df[data_df['Perioden'] == "2021JJ00"]
data_df_2021.reset_index(inplace=True)

# Replace invalid values ('.', '', ' ') with NaN
data_df_2021.replace(['       .', '', ' '], pd.NA, inplace=True)

# Convert all columns to appropriate data types (numeric where possible)
data_df_2021_numeric = data_df_2021.apply(pd.to_numeric, errors='ignore')

# Group by 'RegioS' and calculate the mean for numeric columns
aggregated_df = data_df_2021_numeric.groupby('RegioS', as_index=False).mean(numeric_only=True)

# Assume the column with the municipality code is 'gemeentecode'
# Dissolve the neighborhoods by 'gemeentecode' to aggregate geometries
gemeente_df = geo_df.dissolve(by='GM_CODE')

# Optional: Reset the index if needed
gemeente_df.reset_index(inplace=True)

# Merge the data with the shapefile on 'RegioS' and 'gemeentecode'
merged_gdf = gemeente_df.merge(aggregated_df, left_on='GM_CODE', right_on='RegioS')
merged_gdf = merged_gdf.merge(wijk_df, left_on='GM_CODE', right_on='gwb_code_10')
merged_gdf = merged_gdf.drop(columns=['gm_naam'])

# Plot the spatial map of 'TotaleWoonlasten_2'
plt.figure(figsize=(12, 8))
merged_gdf.plot(column='TotaleWoonlasten_2',
                cmap='viridis',
                legend=True,
                legend_kwds={'label': "Totale Woonlasten 2", 'orientation': "horizontal"})
plt.title('Spatial Map of Totale Woonlasten 2')
plt.axis('off')
plt.show()

w = weights.Queen.from_dataframe(merged_gdf, idVariable='GM_CODE')
merged_gdf["w_woonquote"] = weights.lag_spatial(w, merged_gdf["Woonquote_5"])
w['GM1680']
merged_gdf["woonquote_std"] = (merged_gdf["Woonquote_5"] - merged_gdf["Woonquote_5"].mean()) / merged_gdf["Woonquote_5"].std()
merged_gdf["w_woonquote_std"] = weights.lag_spatial(w, merged_gdf["woonquote_std"])

# Setup the figure and axis
f, ax = plt.subplots(1, figsize=(9, 9))
# Plot values
sns.regplot(x="woonquote_std", y="w_woonquote_std", data=merged_gdf, ci=None)
# Add vertical and horizontal lines
plt.axvline(0, c="k", alpha=0.5)
plt.axhline(0, c="k", alpha=0.5)
# Display
plt.show()

mi = esda.Moran(merged_gdf["Woonquote_5"], w)

mi.I

mi.p_sim

moran_scatterplot(mi)

# Setup the figure and axis
f, ax = plt.subplots(1, figsize=(9, 9))
# Plot values
sns.regplot(x="woonquote_std", y="w_woonquote_std", data=merged_gdf, ci=None)
# Add vertical and horizontal lines
plt.axvline(0, c="k", alpha=0.5)
plt.axhline(0, c="k", alpha=0.5)
plt.text(1.75, 0.5, "HH", fontsize=25)
plt.text(1.5, -1.5, "HL", fontsize=25)
plt.text(-2, 1, "LH", fontsize=25)
plt.text(-1.5, -2.5, "LL", fontsize=25)
# Display
plt.show()

lisa = esda.Moran_Local(merged_gdf["Woonquote_5"], w)

# Break observations into significant or not
merged_gdf["significant"] = lisa.p_sim < 0.05
# Store the quadrant they belong to
merged_gdf["quadrant"] = lisa.q



lisa_cluster(lisa,merged_gdf)

# Setup the figure and axis
f, ax = plt.subplots(1, figsize=(9, 9))
# Plot insignificant clusters
ns = merged_gdf.loc[merged_gdf["significant"] == False, "geometry"]
ns.plot(ax=ax, color="k")
# Plot HH clusters
hh = merged_gdf.loc[(merged_gdf["quadrant"] == 1) & (merged_gdf["significant"] == True), "geometry"]
hh.plot(ax=ax, color="red")
# Plot LL clusters
ll = merged_gdf.loc[(merged_gdf["quadrant"] == 3) & (merged_gdf["significant"] == True), "geometry"]
ll.plot(ax=ax, color="blue")
# Plot LH clusters
lh = merged_gdf.loc[(merged_gdf["quadrant"] == 2) & (merged_gdf["significant"] == True), "geometry"]
lh.plot(ax=ax, color="#83cef4")
# Plot HL clusters
hl = merged_gdf.loc[(merged_gdf["quadrant"] == 4) & (merged_gdf["significant"] == True), "geometry"]
hl.plot(ax=ax, color="#e59696")
# Style and draw
f.suptitle("LISA for Brexit vote", size=30)
f.set_facecolor("0.75")
ax.set_axis_off()
plt.show()

# Save the GeoDataFrame as a GeoPackage
# merged_gdf.to_file('all_data_2021.gpkg', driver='GPKG')

