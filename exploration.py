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
data_file = 'data/85950NED_woonquote.csv'
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

# Convert all columns to appropriate data types (numeric where possible)
data_df = data_df.apply(pd.to_numeric, errors='ignore')
# Convert to numeric, coercing errors to NaN
data_df['TotaleWoonlasten_2'] = pd.to_numeric(data_df['TotaleWoonlasten_2'], errors='coerce')
data_df['Woonquote_5'] = pd.to_numeric(data_df['Woonquote_5'], errors='coerce')
data_df['Saving potential'] = data_df['TotaleWoonlasten_2'] / (data_df['Woonquote_5'] / 100 ) - data_df['TotaleWoonlasten_2']

data_df_2021 = data_df[data_df['Perioden'] == "2021JJ00"]
data_df_2021.reset_index(inplace=True)

# Replace invalid values ('.', '', ' ') with NaN
data_df_2021.replace(['       .', '', ' '], pd.NA, inplace=True)

# Group by 'RegioS' and calculate the mean for numeric columns
aggregated_df = data_df_2021.groupby('RegioS', as_index=False).mean(numeric_only=True)

non_nan_count = aggregated_df['Woonquote_5'].count()
print(f'for 2021 the amount of municipalities with available data is {non_nan_count}')

# Assume the column with the municipality code is 'gemeentecode'
# Dissolve the neighborhoods by 'gemeentecode' to aggregate geometries
gemeente_df = geo_df.dissolve(by='GM_CODE')

# Optional: Reset the index if needed
gemeente_df.reset_index(inplace=True)

# Merge the data with the shapefile on 'RegioS' and 'gemeentecode'
merged_gdf = gemeente_df.merge(aggregated_df, left_on='GM_CODE', right_on='RegioS')
merged_gdf = merged_gdf.merge(wijk_df, left_on='GM_CODE', right_on='gwb_code_10')
merged_gdf = merged_gdf.drop(columns=['gm_naam'])

# Plot the map with NaN values shown as gray
merged_gdf.plot(column="Woonquote_5",
                cmap='viridis',
                legend=True,
                legend_kwds={'label': "Woonquote in %", 'orientation': "horizontal"},
                missing_kwds={
                    'color': 'gray',  # Color for NaN values
                    'label': 'Missing values',  # Label for NaN values in the legend
                    'hatch': '///'  # Optional: add a hatch pattern to distinguish NaN areas
                })

plt.title('Living ratio of renters in the private sector 2021')
plt.axis('off')

# Set the path to save the figure
save_path = 'figures/woonquote_2021.png'
# Save the figure to the specified path
plt.savefig(save_path, bbox_inches='tight', dpi=300)
plt.show()

# Plot the map with NaN values shown as gray for "Saving potential" column
merged_gdf.plot(column="Saving potential",
                cmap='viridis_r',
                legend=True,
                legend_kwds={'label': "Saving Potential", 'orientation': "horizontal"},
                missing_kwds={
                    'color': 'gray',  # Color for NaN values
                    'label': 'Missing values',  # Label for NaN values in the legend
                    'hatch': '///'  # Optional: add a hatch pattern to distinguish NaN areas
                })

plt.title('Saving Potential of Renters in the Private Sector 2021')
plt.axis('off')

# Set the path to save the figure
save_path2 = 'figures/saving_potential_2021.png'
# Save the figure to the specified path
plt.savefig(save_path2, bbox_inches='tight', dpi=300)

# Display the plot
plt.show()

# Set the path to save the CSV file
csv_save_path = 'cleaned/cleaned_2021.csv'

# Save the GeoDataFrame as a CSV
merged_gdf.to_csv(csv_save_path, index=False)  # index=False avoids saving the index as a column

data_df_2018 = data_df[data_df['Perioden'] == "2018JJ00"]
data_df_2018.reset_index(inplace=True)

# Replace invalid values ('.', '', ' ') with NaN
data_df_2018.replace(['       .', '', ' '], pd.NA, inplace=True)

# Convert all columns to appropriate data types (numeric where possible)
data_df_2018_numeric = data_df_2018.apply(pd.to_numeric, errors='ignore')

# Group by 'RegioS' and calculate the mean for numeric columns
aggregated_df2 = data_df_2018_numeric.groupby('RegioS', as_index=False).mean(numeric_only=True)

non_nan_count2 = aggregated_df2['Woonquote_5'].count()
print(f'for 2018 the amount of municipalities with available data is {non_nan_count2}')

# Merge the data with the shapefile on 'RegioS' and 'gemeentecode'
merged_gdf2 = gemeente_df.merge(aggregated_df2, left_on='GM_CODE', right_on='RegioS')
merged_gdf2 = merged_gdf2.merge(wijk_df, left_on='GM_CODE', right_on='gwb_code_10')
merged_gdf2 = merged_gdf2.drop(columns=['gm_naam'])

# Plot the map with NaN values shown as gray
merged_gdf2.plot(column="Woonquote_5",
                cmap='viridis',
                legend=True,
                legend_kwds={'label': "Woonquote in %", 'orientation': "horizontal"},
                missing_kwds={
                    'color': 'gray',  # Color for NaN values
                    'label': 'Missing values',  # Label for NaN values in the legend
                    'hatch': '///'  # Optional: add a hatch pattern to distinguish NaN areas
                })

plt.title('Living ratio of renters in the private sector 2018')
plt.axis('off')

# Set the path to save the figure
save_path3 = 'figures/woonquote_2018.png'
# Save the figure to the specified path
plt.savefig(save_path3, bbox_inches='tight', dpi=300)
plt.show()

# Plot the map with NaN values shown as gray for "Saving potential" column
merged_gdf2.plot(column="Saving potential",
                cmap='viridis_r',
                legend=True,
                legend_kwds={'label': "Saving Potential", 'orientation': "horizontal"},
                missing_kwds={
                    'color': 'gray',  # Color for NaN values
                    'label': 'Missing values',  # Label for NaN values in the legend
                    'hatch': '///'  # Optional: add a hatch pattern to distinguish NaN areas
                })

plt.title('Saving Potential of Renters in the Private Sector 2018')
plt.axis('off')

# Set the path to save the figure
save_path4 = 'figures/saving_potential_2018.png'
# Save the figure to the specified path
plt.savefig(save_path4, bbox_inches='tight', dpi=300)

# Display the plot
plt.show()

# Set the path to save the CSV file
csv_save_path2 = 'cleaned/cleaned2018.csv'

# Save the GeoDataFrame as a CSV
merged_gdf2.to_csv(csv_save_path2, index=False)  # index=False avoids saving the index as a column
