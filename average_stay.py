'''Generate json file for average stay duration per unit size'''

# %%
import json
import pandas as pd

df = pd.read_csv('leases.csv')

df['area'] = df['Width (m)'] * df['Length (m)']
df['Avg. Stay (days)'] = df['Avg. Stay (days)'].apply(lambda x: int(x.replace(',','')))


averages = {}
for i, d in df[['area', 'Avg. Stay (days)']].groupby('area'):
    averages[f'{round(i, 2)}'] = int(d['Avg. Stay (days)'].mean())


with open('average_stay.json', 'w') as outfile:
    json.dump(averages, outfile, indent=4, ensure_ascii=False)

# %% check actual distribution vs np.choice
import matplotlib.pyplot as plt
import numpy as np

df['Avg. Stay (days)'].plot.kde(alpha=0.8)
a = df['Avg. Stay (days)'].value_counts() / 754

d = []
for i in range(1000):
    d += [np.random.choice(a.index, p=a.values)]

pd.Series(d).plot.kde(alpha=0.8)
