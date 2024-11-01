# %% [markdown]
# # III. Merge the scraped data
# # Once maps data is collected, we can merge the all CSVs into a single file

# %%
import pandas as pd

dfs = []

for i in range(4):
    df = pd.read_csv(f'../data/temp/hospitals_{i}_ratings.csv')
    dfs.append(df)

combined_df = pd.concat(dfs, ignore_index=True)

combined_df.to_csv('../data/main/2-hospitals_scraped.csv', index=False)