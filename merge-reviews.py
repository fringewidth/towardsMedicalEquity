# %%
import pandas as pd

dfs = []

for i in range(4):
    df = pd.read_csv(f'hospitals_{i}_ratings.csv')
    dfs.append(df)

combined_df = pd.concat(dfs, ignore_index=True)

combined_df.to_csv('hospitals_ratings.csv', index=False)


