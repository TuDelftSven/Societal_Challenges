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
geo_df = gpd.read_file(shapefile)
geo_df2021 = gpd.read_file(shapefile2021)

# Ensure that both 'RegioS' and 'gemeentecode' are of the same data type (e.g., strings)
data_df['RegioS'] = data_df['RegioS'].astype(str)
geo_df['gemeentecode'] = geo_df['gemeentecode'].astype(str)
for c in geo_df2021.columns:
    print(c)
print(geo_df2021['GM_CODE'])

# Merge the data with the shapefile on 'RegioS' and 'gemeentecode'
merged_gdf = geo_df.merge(data_df, left_on='gemeentecode', right_on='RegioS')
start = time.time()

#
# print(f'now bebfore start {time.time() - start}')
# # Plot the spatial map of 'TotaleWoonlasten_2'
# plt.figure(figsize=(12, 8))
# print(f'now after figure {time.time() - start}')
# merged_gdf.plot(column='TotaleWoonlasten_2',
#                 cmap='viridis',
#                 legend=True,
#                 legend_kwds={'label': "Totale Woonlasten 2", 'orientation': "horizontal"})
# print(f'now after plot {time.time() - start}')
# plt.title('Spatial Map of Totale Woonlasten 2')
# plt.axis('off')
# print(f'now before show {time.time() - start}')
# plt.show()
