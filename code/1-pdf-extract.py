# %% [markdown]
# # I. Extracting tables from PDF via Camelot
# In this notebook, we will convert a PDF containing a list of all hospitals in India, provided to the internet by NIT Jalandhar, into a CSV file. We will then split this CSV file into 4 parts.
# Upon noticing that the dataset has a bias towards Eye Hospitals, we filter out all hospitals with "eye" in their name. We note that this will not eliminate all eye hospitals in the dataset, but this will not significantly diverge the desired results.
# We also filter out all hospitals that do not have "Hospital" in their name. This removes all clinics, nursing homes, and other medical facilities that are not hospitals.
# We split the dataset into four parts so that we can distribute the scraping task to four different people.

# ## References:
# [List of Hospitals - Pan India](https://v1.nitj.ac.in/nitj_files/links/List_of_Hospital_-_Pan_India_28496.pdf)

# %%
import camelot
hospitals_pdf = camelot.read_pdf('../data/pdf/List-of-Hospitals.pdf', pages='all')

# %%
import pandas as pd
import re

# concat all tables except first row (which has different column names)
hospitals_df = pd.concat([table.df for table in hospitals_pdf[1:]], ignore_index=True)

# set first row column names to dataframe and concat
hospitals_df.columns = hospitals_pdf[0].df.columns
hospitals_df = pd.concat([hospitals_pdf[0].df, hospitals_df], ignore_index=True)

# remove first row (which is also column names)
hospitals_df = hospitals_df[1:]

# remove all hospitals that have "eye" in them
hospitals_df = hospitals_df[~hospitals_df['Hospital Name'].str.contains(re.compile('eye', re.IGNORECASE))]

# remove all hospitals that do not have "hospital" in them
hospitals_df = hospitals_df[hospitals_df['Hospital Name'].str.contains('Hospital')]

hospitals_df.to_csv('data/main/1-hospitals-from-pdf.csv', index=False)

# %%
# split the data into 4 files
nRows = hospitals_df.shape[0]

nRowsPerFile = nRows // 4

for i in range(4):
    start = i * nRowsPerFile
    end = (i+1) * nRowsPerFile
    if i == 3:
        end = nRows
    hospitals_df[start:end].to_csv(f'data/temp/hospitals-pdf_{i}.csv', index=False)

