import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
from sklearn.linear_model import Lasso
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error


df_wq = pd.read_csv('data/85950NED_woonquote.csv', sep=";")
df_2018 = pd.read_csv('cleaned/cleaned2018.csv')
df_2021 = pd.read_csv('cleaned/cleaned_2021.csv')

# Filter and clean the dataset
variables_to_keep = [
    'bev_dich', 'a_inw', 'a_00_14', 'a_15_24', 'a_25_44', 'a_45_64', 'a_65_oo',
    'a_ongeh', 'a_gehuwd', 'a_woning', 'p_ov_hw', 'g_wozbag', 'p_leegsw',
    'a_w_all', 'a_nw_all', 'p_wcorpw', 'a_opl_lg', 'a_opl_md', 'a_opl_hg',
    'p_arb_pp', 'p_arb_wn', 'p_arb_zs', 'a_inkont', 'g_ink_po', 'g_ink_pi',
    'a_soz_wb', 'a_soz_ao', 'a_soz_ww', 'a_soz_ow', 'p_wmo_t', 'p_jz_tn',
    'p_ink_li', 'p_ink_hi', 'p_hh_110', 'Woonquote_5'
]

# Filter dataset to keep only selected variables
df_2018_cleaned = df_2018[variables_to_keep]
df_2021_cleaned = df_2021[variables_to_keep]

# Replace only exact matches of '.' with NaN
df_2018_cleaned = df_2018_cleaned.replace(to_replace='^\\.$', value=np.nan, regex=True)
df_2021_cleaned = df_2021_cleaned.replace(to_replace='^\\.$', value=np.nan, regex=True)


# Replace commas with dots and convert to numeric
for col in df_2018_cleaned.columns:
    df_2018_cleaned[col] = df_2018_cleaned[col].replace(',', '.', regex=True).astype(float)
for col in df_2021_cleaned.columns:
    df_2021_cleaned[col] = df_2021_cleaned[col].replace(',', '.', regex=True).astype(float)

# Drop rows with missing values
df_2018_cleaned = df_2018_cleaned.dropna()
df_2021_cleaned = df_2021_cleaned.dropna()


#function for linear_regression so its usable for 2021 and 2018
def linear_regression(data_set):
    # Define dependent and independent variables
    X = data_set.drop(columns=['Woonquote_5'])
    y = data_set['Woonquote_5']

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Fit the regression model
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Predict on the test set
    y_pred = model.predict(X_test)

    # Evaluate the model
    r2 = r2_score(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)

    # Coefficients
    coefficients = pd.DataFrame({
        'Variable': X.columns,
        'Coefficient': model.coef_
    }).sort_values(by='Coefficient', ascending=False)

    # Display Results
    print(f"R²: {r2}")
    print(f"MSE: {mse}")
    print(coefficients)

def lasso_regression(data_set):
    # Define dependent and independent variables
    X = data_set.drop(columns=['Woonquote_5'])
    y = data_set['Woonquote_5']

    # Fill missing values in X with the mean of each column
    X = X.fillna(X.mean())

    # Split data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Initialize and train the Lasso regression model
    lasso = Lasso(alpha=1.0, random_state=42)  # Adjust alpha for regularization strength
    lasso.fit(X_train, y_train)

    # Predict on the test set
    y_pred = lasso.predict(X_test)

    # Evaluate the model
    r2 = r2_score(y_test, y_pred)  # R² score
    mse = mean_squared_error(y_test, y_pred)  # Mean squared error

    # Extract coefficients
    coefficients = pd.DataFrame({
        'Variable': X.columns,
        'Coefficient': lasso.coef_
    }).sort_values(by='Coefficient', ascending=False)

    # Display Results
    print(f"R²: {r2}")
    print(f"MSE: {mse}")
    print(coefficients)


lasso_regression(df_2018_cleaned)