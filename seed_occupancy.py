# %% Generate seed occupancy from leases.csv

import pandas as pd
import json

# seed occupancy
df = pd.read_csv('leases.csv')
df['area'] = df['Width (m)'].mul(df['Length (m)']).round(2)

available = {}
for i in df['area'].unique():
    d = df[df['area'] == i]['Occ.']

    available[str(i)] = int(d.isna().sum())

with open('seed_occupancy_default.json', 'w') as outfile:
    json.dump(available, outfile, indent=4, ensure_ascii=False)

