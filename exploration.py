import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import time

# Load the data CSV and the GeoPackage shapefile
data_file = 'data/85950NED.csv'
shapefile = 'data/wijkenbuurten_2023_v2.gpkg'
shapefile2021 = 'data/geo/buurten_2021_v3.shp'

# Read the CSV and shapefile
data_df = pd.read_csv(data_file, sep=";")
geo_df = gpd.read_file(shapefile2021)

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


