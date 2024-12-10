import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import time
import seaborn as sns
from pysal.lib import weights


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
start = time.time()

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
w['GM1680']
merged_gdf["woonquote"] = (merged_gdf["Woonquote_5"] - merged_gdf["Woonquote_5"].mean()) / merged_gdf["Woonquote_5"].std()
merged_gdf["w_woonquote"] = weights.lag_spatial(w, merged_gdf["woonquote"])

# Setup the figure and axis
f, ax = plt.subplots(1, figsize=(9, 9))
# Plot values
sns.regplot(x="woonquote", y="w_woonquote", data=merged_gdf, ci=None)
# Add vertical and horizontal lines
plt.axvline(0, c="k", alpha=0.5)
plt.axhline(0, c="k", alpha=0.5)
# Display
plt.show()


# # Save the GeoDataFrame as a GeoPackage
# merged_gdf.to_file('all_data_2021.gpkg', driver='GPKG')

