import pandas as pd


changes = pd.read_csv("csv/Detail Change.csv", sep=";")

for col in changes.columns:
    if not col == 'Change ID':
        c_temp = changes[['Change ID', col]]
        c_temp_grouped = c_temp.groupby('Change ID')[col].nunique().reset_index()
        n_unique_filter = c_temp_grouped[col] > 1
        non_unique_c = c_temp_grouped[n_unique_filter]

        if non_unique_c.size == 0:
            print(col)
