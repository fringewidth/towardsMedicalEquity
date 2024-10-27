# %%
import camelot
hospitals_pdf = camelot.read_pdf('List-of-Hospitals.pdf', pages='all')

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

hospitals_df.to_csv('hospitals.csv', index=False)

# %%
# split the data into 4 files
nRows = hospitals_df.shape[0]

nRowsPerFile = nRows // 4

for i in range(4):
    start = i * nRowsPerFile
    end = (i+1) * nRowsPerFile
    if i == 3:
        end = nRows
    hospitals_df[start:end].to_csv(f'hospitals_{i}.csv', index=False)

