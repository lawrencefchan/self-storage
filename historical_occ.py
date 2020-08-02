'''Actual historical occupancy'''

# %%
import numpy as np
import pandas as pd
import unitlist as ul
import matplotlib.pyplot as plt
from datetime import datetime

from importlib import reload

reload(ul)


def get_data():
    df = pd.read_csv('DataSet2_clean.csv')

    for i in ['When do you require storage', 'Create Date']:
        df[i] = pd.to_datetime(df[i])

    return df


def run_simulation(u, dr, **kawrgs):

    reservations = []
    for date in dr:
        d = df[df['Create Date'] == date]

        u.move_out(date)

        for row in d.itertuples():
            size = row._1
            when = row._2
            if not u.attempt_booking(size, when, p=1, ndays=365):
                # print(date, 'NO MORE ROOM!!')
                break
            # else: print(u.available)  # debug

        # --- number of units reserved
        reserved = sum({k: u.max_capacity[str(k)] -
                        u.available[k] for k in u.available}.values())
        reservations += [reserved]

    return reservations


when = 'When do you require storage'
df = get_data().sort_values('Create Date')[['Room size required in sqmtrs (1)',
                                            'When do you require storage',
                                            'Create Date',
                                            'Enquiry Status']]
df = df[df['Enquiry Status'] == 'Reserved']

start = list(df['Create Date'])[0]
end = list(df['Create Date'])[-1]
dr = pd.date_range(start=start, end=end)


# %% plot total reservations
n = 100

sim_data = []
t0 = datetime.now()
for i in range(n):
    u = ul.Units(start=start, seed='default')

    reservations = run_simulation(u=u, dr=dr)
    sim_data += [reservations]

print(n, 'simulations took', datetime.now() - t0)

sim_data = pd.DataFrame(sim_data, columns=dr).T

fig, ax = plt.subplots()  # figsize=(13, 8))
sim_data.plot(ax=ax, legend=False, alpha=0.6)
ax.set_ylabel('Total Occupancy')
ax.set_title(f'Stochastic model (n={n})')

saveas = f'total_occupancy_n={n}_historical'
sim_data.to_csv(f'{saveas}.csv')


# %%
saveas = f'total_occupancy_n={n}_historical'

sim_data2 = pd.read_csv('total_occupancy_n=100_historical.csv', index_col=0)
sim_data2.index = pd.to_datetime(sim_data2.index)

nans = pd.DataFrame(np.nan, index=pd.date_range('2016-01-01', '2016-01-02'), columns=sim_data2.columns)

sim_data2 = pd.concat([nans, sim_data2], axis=0).resample('1D').mean()

ax = (sim_data2 / 7.54).plot(figsize=(9, 5), legend=False, alpha=0.3)

(sim_data2.mean(axis=1) / 7.54).plot(ax=ax, lw=2, c='0.2', label='Average Occupancy')

ax.grid(which='both')
ax.set_ylabel('Total Occupancy (%)')
ax.set_title(f'Actual reservations, Stochastic lease duration (n={n})',
             loc='left',
             fontdict={'fontsize': 16},
             pad=10,
             c='0.3')

ax.text(0.02, 0.05,
        f'Average occupancy: {(sim_data2.mean(axis=1) / 7.54).mean():.4}%',
        fontsize=12,
        transform=ax.transAxes)

ax.set_ylim((89.8, 100.2))

h_, l_ = ax.get_legend_handles_labels()
ax.legend(h_[-1:], l_[-1:], loc='upper left')

plt.savefig(f'plots/{saveas}.png', dpi=300, bbox_inches='tight')

# compare simulated reservations vs actual historical reservations
