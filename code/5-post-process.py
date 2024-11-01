# %% [markdown]
# # V. Post-processing of the scraped data
# This script reads the scraped data, cleans it, and generates a bubble plot of the hospitals based on their effective rating.
# The effective rating is calculated as the product of the rating and the logarithm of the number of reviews.
# The effective rating is then normalized to the range [0, 5] to stick to the 5-star rating system.

# *Kinks:*
# - We backward fill latitiude and longitude to fill in the missing values. This does not cause any significant distortion to the data as we observed that a sequence of hospitals were located close to each other in the dataset.
# - We fill the missing values of the rating and number of reviews with the median values. We feel that this is a reasonable approach as the missing values are not too many.
# - The bubble plot generated is simply a preliminary visualization of the data just as a sanity check. We will be using more sophisticated visualizations in the next steps.
# %%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv('../data/main/3-hospitals_scraped_coords.csv')

df['Latitude'] = df['Latitude'].bfill()
df['Longitude'] = df['Longitude'].bfill()
df['Rating'] = df['Rating'].fillna(df['Rating'].median())
df['Number of Reviews'] = df['Number of Reviews'].fillna(df['Number of Reviews'].median())

df['Effective Rating'] = df['Rating'] * np.log(df['Number of Reviews'] + 1)

min_effective_rating = df['Effective Rating'].min()
max_effective_rating = df['Effective Rating'].max()

df['Effective Rating'] = 5 * (df['Effective Rating'] - min_effective_rating) / (max_effective_rating - min_effective_rating)

df.to_csv('../data/main/4-hospitals_cleaned.csv', index=False)

# %%
# generate bubble plot
plt.figure(figsize=(10, 8))
plt.scatter(df['Longitude'], df['Latitude'], s=df['Effective Rating']*512, c=df['Effective Rating'], alpha=0.2, edgecolors='w')
plt.colorbar(label='Effective Rating')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.title('Bubble Plot of Hospitals by Effective Rating')
plt.savefig('../fig/initial_bubble_plot.svg')
