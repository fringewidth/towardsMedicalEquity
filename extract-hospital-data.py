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


