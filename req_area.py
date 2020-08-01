'''Another attempt at cleaning data for required area. A seperate regex pattern
is used to find each form. This is more labour intensive, but almost certainly
more accurate than the previous attempt.

'''

# %%
import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import re

df = pd.read_csv('DataSet2.csv')
size = 'Room size required in sqmtrs (1)'

req_area = df[size].str.lower()

# --- convert "locker" to 1m2
req_area = req_area.apply(lambda x: 1 if x == 'locker' else x)

# --- convert "car" to 8m2
req_area = req_area.apply(lambda x: 12 if 'car' in str(x) else x)

# --- remove text (e.g. na/x/unknown etc.) if str doesn't contain a digit
text = req_area.apply(lambda x: x if bool(re.search(r'\d', str(x))) else np.nan)
req_area = req_area[text.notna()]
print(text.isna().sum(), 'entries without numerals')

# --- extract the form (1.4m x 1.5m x 3)
pat = r'([0-9\.]+[ ]*[m]*[ x\*]+[0-9\.]+[ ]*[m]*[ x\*]*[0-9\.]*)'
dimensions = req_area.str.split(pat, n=1, expand=True)[1].fillna(value=np.nan)
req_area = req_area[dimensions.isna()]
dimensions = dimensions.dropna()

# ignore text in brackets (separate units)
# NOTE: If the assumption is made that separate units don't matter, once
# dimensions are accounted for, text in brackets is fortuitously irrelevant
pat = r' \([a-z0-9 \.\`]*\)'
req_area = req_area.apply(str).str.replace(pat, '')

# ignore text after '/' (same reasoning as above)
pat = r' \/[a-z0-9 \.\-\/\(\)]*'
req_area = req_area.apply(str).str.replace(pat, '')

# --- extract numerals ending in sqm/m2/none/ sq m/ sqm
# NOTE: `?:` is non-pattern matching (will not be extracted)
pat = r'^([0-9\.]+)[ ]*(?:sqm|m2||sq m|u|sqmu|m|sq)$'
# NOTE: apply str so str.extract works (idk why it doesn't otherwise...)
numerals = req_area.apply(str).str.extract(pat)[0].fillna(value=np.nan)
req_area = req_area[numerals.isna()]
numerals = numerals.dropna()

# --- extract requests for multiple units
pat = r'(each)'
multiples = req_area.apply(str).str.split(pat, expand=True)
req_area = req_area[multiples.isna().any(axis=1)]
multiples = multiples.dropna()

multiples[0] = [i[0]+"x"+re.search(r'[0-9\.]+', j).group(0) for i, j in zip(multiples[0], multiples[2])]

dimensions = pd.concat([dimensions, multiples[0]], axis=0)

# --- manually fix req_area (remaning)
req_area.iloc[:] = [1.1, 1.1, 1.1, 33.8, 4.5]

# --- combine

L = dimensions.str.replace(' ', '') \
              .str.extract(r'([0-9.]*)') \
              .apply(pd.to_numeric)[0]

W = dimensions.str.replace(' ', '') \
              .str.extract(r'(x[0-9.]*)')[0] \
              .str.split('x', expand=True)[1] \
              .apply(pd.to_numeric)

clean_df = pd.concat([L * W, numerals.apply(pd.to_numeric), req_area])

# check that all entries have been parsed
assert clean_df.shape[0] + text.isna().sum() == df.shape[0]

df[size] = clean_df

df.to_csv('DataSet2_clean.csv', index=False)

# %%

# df.head()
# pd.to_datetime(df['When do you require storage'], format="%d/%m/%Y")

# with pd.option_context('display.max_rows', 150, 'display.max_columns', 10):
#     display(df['When do you require storage'].value_counts().head(150))

dates = df['When do you require storage']  # .value_counts()
dates.index = pd.to_datetime(dates.index, format="%d/%m/%Y")
dates = dates.sort_index()

ax = dates.resample('1D').mean().plot()
# ax.get_xticklabels()

dates



# %%
when = 'When do you require storage'
dates = df[[when, 'Create Date']]

dates[when] = [np.nan if '01/1969' in _ else _ for _ in dates[when]]

for i in [when, 'Create Date']:
    dates[i] = pd.to_datetime(dates[i], format="%d/%m/%Y")

idx = dates[dates[when].dt.year == 1969].index

dates['timedelta'] = dates[when] - dates['Create Date']


# dates = dates.set_index(when) \
#              .sort_index()  # 'Create Date'

# dates[:'2015']

# dates[dates['timedelta'] < pd.to_timedelta(0)]
# dates[dates[when] - pd.to_datetime('2015-01-01') < pd.to_timedelta(0)]


munge_dates = pd.DataFrame({'day': dates.loc[idx, when].dt.day,
                            'month': dates.loc[idx, when].dt.month,
                            'year': dates.loc[idx, 'Create Date'].dt.year})

dates.loc[idx, when] = pd.to_datetime(munge_dates)


dates = dates['timedelta'].value_counts()
dates.index = dates.index.days

dates = dates.sort_index(ascending=False)

dates[1:].plot()



# %%

'''
Assumptions
* Separate units don't matter as they are easy to create with temporary dividers
* car/caravan size = 12m2
* Dates entered before ____ are (invalid? assumed to be entered in 2016?)
* Date requirements from Jan 1969 do not represent real datapoints (all NaN)
* Date requirements from 1969 have correct month and day values (year is incorrect)


'''



# [_ for _ in df[when] if '01/1969' in _]
df[when][[True if '01/1969' in _ else False for _ in df[when]]]
