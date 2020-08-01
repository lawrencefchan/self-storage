# %%
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np


movein = pd.read_csv('movein.csv', index_col='Type').fillna(0)
moveout = pd.read_csv('moveout.csv', index_col='Type').fillna(0)

net = movein.cumsum(axis=1) - moveout.cumsum(axis=1)
# net = net - net.iloc[:, 0].values

plot = 'zeroed'

if plot == 'combined':
    ax = net.sub(net.min(axis=1), axis=0).sum(axis=0).T.plot(legend=False)
    ax.set_ylabel('Estimated occupancy')

elif plot == 'net':
    ax = net.sub(net.iloc[:, 0], axis=0).T.plot()
    ax.set_ylabel('Net change (normalised)')
    ax.legend(bbox_to_anchor=(1, 1.05), ncol=2)

elif plot == 'zeroed':
    ax = net.sub(net.min(axis=1), axis=0).T.plot()
    ax.set_ylabel('Realistic minimum')
    ax.legend(bbox_to_anchor=(1, 1.05), ncol=2)


ax.grid(which='both')

plt.show()

# %% munge (sort) storage unit type

leases = pd.read_csv('leases.csv')
lease_types = leases['Type (U=Upstairs, D=Downstairs)']

leases['type'] = [i if i == 'Locker' else i[-1] for i in lease_types]
leases['unit'] = [i if i == 'Locker' else float(i[:-1]) for i in lease_types]

type_df = []

for i in ['D', 'U', 'Locker']:
    type_df += [leases[leases.type == i].sort_values('unit')]

type_df = pd.concat(type_df, axis=0)


# %% create df for occupancy

occupancy = {}

for i in type_df['Type (U=Upstairs, D=Downstairs)'].unique():
    occupancy[i] = leases[lease_types == i]['Occ.'].notna().sum()

occupancy = pd.DataFrame.from_dict(occupancy, orient='index').reset_index()
occupancy.columns = ['Unit', 'Occ']
occupancy['Type'] = [i if i == 'Locker' else i[-1] for i in occupancy.Unit]

occupancy


# %% --- plot using sns

def change_width(ax, new_value):
    # func to change barchart bar width
    for patch in ax.patches:
        current_width = patch.get_width()
        diff = current_width - new_value

        # change bar width
        patch.set_width(new_value)

        # recenter bar
        patch.set_x(patch.get_x() + diff * .5)


fig, ax = plt.subplots(figsize=(10, 7))
sns.barplot(x='Unit', y='Occ', hue='Type', data=occupancy, ax=ax)

change_width(ax, .75)
plt.xticks(rotation=90)

plt.ylabel('Current Occupancy')

plt.show()

# plt.savefig('Current Occupancy.png', dpi=300,
#             bbox_inches='tight')

# %%
net = movein.cumsum(axis=1) - moveout.cumsum(axis=1)


for row in occupancy.itertuples():
    try:
        net.loc[row.Unit] = net.loc[row.Unit] + row.Occ
    except KeyError:
        continue

fig, ax = plt.subplots(figsize=(10, 7))

for i in ['D', 'U']:

    units = occupancy[occupancy.Type == i]['Unit']
    net.loc[units].sum(axis=0).plot(label=i, marker='.', legend=i, ax=ax)

locker_occ = occupancy[occupancy.Type == 'Locker']['Occ'].values
ax.axhline(locker_occ, ls='--', label='Locker', c='C2')

plt.ylim(bottom=0)
plt.ylabel('Estimated Monthly Occupancy')
plt.legend(title='Type')

plt.show()

# plt.savefig('Est. Monthly Occupancy.png', dpi=300,
#             bbox_inches='tight')
