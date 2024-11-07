# %%
import pandas as pd
import numpy as np

df = pd.read_csv("../data/main/5-hospitals_clustered.csv")


# %%
old_rating = df['Rating']
df['Rating'] = np.round(df['Rating'].apply(lambda x: x + np.random.normal(0, 0.05)), 1).clip(lower=0, upper=5)
df['Number of Reviews'] = np.round(np.exp(old_rating * np.log(df['Number of Reviews']) / df['Rating'])).astype(int)
df['id'] = "Hospital #" + df.index.astype(str)
df['City'] = df['CITY'].str.title().str.replace('\r\n', '')
df['State'] = df['STATE'].str.title().str.replace('\r\n', '')
df = df[['id', 'City', 'State', 'Rating', 'Number of Reviews', 'Latitude', 'Longitude']]
df.to_csv("../data/main/6-hospitals_anonymized.csv", index=False)





