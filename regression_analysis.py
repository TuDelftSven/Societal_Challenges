import pandas as pd

df_2018 = pd.read_csv('cleaned/cleaned2018.csv')
df_2021 = pd.read_csv('cleaned/cleaned_2021.csv')

print(df_2018.head(5))
print(df_2021.columns)


