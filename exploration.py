import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

# Load the data CSV and the GeoPackage shapefile
data_file = 'data/85950NED.csv'
shapefile = 'data/wijkenbuurten_2023_v2.gpkg'

# Read the CSV and shapefile
data_df = pd.read_csv(data_file)
geo_df = gpd.read_file(shapefile)

# Ensure that both 'RegioS' and 'gemeentecode' are of the same data type (e.g., strings)
data_df['RegioS'] = data_df['RegioS'].astype(str)
geo_df['gemeentecode'] = geo_df['gemeentecode'].astype(str)

# Merge the data with the shapefile on 'RegioS' and 'gemeentecode'
merged_gdf = geo_df.merge(data_df, left_on='gemeentecode', right_on='RegioS')

# Plot the spatial map of 'TotaleWoonlasten_2'
plt.figure(figsize=(12, 8))
merged_gdf.plot(column='TotaleWoonlasten_2',
                cmap='viridis',
                legend=True,
                legend_kwds={'label': "Totale Woonlasten 2", 'orientation': "horizontal"})
plt.title('Spatial Map of Totale Woonlasten 2')
plt.axis('off')
plt.show()
