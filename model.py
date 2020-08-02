'''This is the model

It uses:
1. take enquiry dates and requested sizes and check if there is availability
2. if so, the customer has "some probability" (?) of making the reservation
3. if it's full, then we lose the customer
4. Optimising available storage sizes


Assumptions:
* Customers are willing to accept units "slightly" (?) larger than required
    NOTE: this is defined in unitlist.py


Temporary assumptions (until model is improved):
* 30% conversion rate
* 590 day stay
* first in(quiry), first served
* greedy unit allocation algorithm: find the smallest room that
    meets customer requirements. If full, move to the next size up.


TODO:


'''

# %%
import matplotlib.pyplot as plt
import pandas as pd
import unitlist as ul
import numpy as np
from datetime import datetime

from importlib import reload

reload(ul)


def get_data():
    df = pd.read_csv('DataSet2_clean.csv')

    for i in ['When do you require storage', 'Create Date']:
        df[i] = pd.to_datetime(df[i])

    return df


df = get_data()[['Room size required in sqmtrs (1)',
                 'When do you require storage',
                 'Create Date']] \
        .dropna(how='any') \
        .sort_values('Create Date')  # first come, first served


def run_simulation(u, dr, **kawrgs):
    '''
    Parameters:
    ----------

    u: storage unit class

    dr: simulation date range
    '''
    # movein = {}  # Debug
    # movingout = []  # Debug
    # debug_dr = dr # Debug

    reservations = []

    for date in dr:
        d = df[df['Create Date'] == date]

        u.move_out(date)

        # # ----- Debug
        # if date in debug_dr:
        #     movingout += [u.free_rooms]
        # # ----- Debug

        for row in d.itertuples():
            size = row._1
            when = row._2
            if not u.attempt_booking(size, when, p=0.25, ndays=365):
                # print(date, 'NO MORE ROOM!!')
                break
            # else: movein[date] = movein.get(date, 0) + 1  # debug

        # --- number of units reserved
        reserved = sum({k: u.max_capacity[str(k)] -
                        u.available[k] for k in u.available}.values())
        reservations += [reserved]

    # # ----- Debug
    # pd.Series(index=debug_dr, data=movein).plot(label='movein')
    # pd.Series(index=debug_dr, data=movingout).plot(label='moveout')
    # plt.legend()

    # (pd.Series(index=debug_dr, data=movein) -
    #   pd.Series(index=debug_dr, data=movingout)).plot(label='movein')
    # # ----- Debug

    return reservations


start = df['Create Date'][0]
end = df['Create Date'][9997]
dr = pd.date_range(start=start, end=end)


# --- %% plot total reservations
n = 10

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
ax.set_title(f'Stochastic model (n={n}), (ndays=365)')

saveas = f'total_occupancy_n={n}_simulated'
sim_data.to_csv(f'{saveas}.csv')


# %% [[[Historical simulation]]]
saveas = f'total_occupancy_n={n}_simulated'

sim_data = pd.read_csv('total_occupancy_n=100_simulated.csv', index_col=0)
sim_data.index = pd.to_datetime(sim_data.index)

nans = pd.DataFrame(np.nan, index=pd.date_range('2016-01-01', '2016-01-02'), columns=sim_data.columns)
sim_data = pd.concat([nans, sim_data], axis=0).resample('1D').mean()

ax = (sim_data / 7.54).plot(figsize=(9, 5), legend=False, alpha=0.3)
(sim_data.mean(axis=1) / 7.54).plot(ax=ax, lw=2, c='0.2', label='Average Occupancy')

ax.grid(which='both')
ax.set_ylabel('Total Occupancy (%)')
ax.set_title(f'Simulated reservations, Stochastic lease duration (n={n})',
             loc='left',
             fontdict={'fontsize': 16},
             pad=10,
             c='0.3')

ax.text(0.02, 0.05,
        f'Average occupancy: {(sim_data.mean(axis=1) / 7.54).mean():.4}%',
        fontsize=12,
        transform=ax.transAxes)

ax.set_ylim((89.8, 100.2))

h_, l_ = ax.get_legend_handles_labels()
ax.legend(h_[-1:], l_[-1:], loc='upper left')

plt.savefig(f'plots/{saveas}.png', dpi=300, bbox_inches='tight')

# compare simulated reservations vs actual historical reservations


# %% [[[hack code]]] plot both historical and simulated

ax = (sim_data.mean(axis=1) / 7.54).plot(figsize=(13, 8), alpha=0.9, label='Simulated reservations')
(sim_data2.mean(axis=1) / 7.54).plot(ax=ax, alpha=0.9, label='Actual reservations')

ax.grid(which='both')
ax.set_ylabel('Total Occupancy (%)')
ax.set_title(f'Simulated vs. Actual reservations, Stochastic lease duration',
             loc='left',
             fontdict={'fontsize': 16},
             pad=10,
             c='0.3')

ax.set_ylim((89.8, 100.2))

ax.legend(loc='upper left')

plt.savefig(f'plots/historical_simulated_vs_actual.png', dpi=300, bbox_inches='tight')


# %% plot distribution
# target = 250
# beta = 1.0/target

# Y = np.random.exponential(beta, 5000)
# plt.hist(Y, normed=True, bins=200,lw=0,alpha=.8)


a = np.random.exponential(1000, size=1000)
ndays = 600
a = np.random.normal(loc=ndays, scale=ndays*0.05, size=1000)

plt.hist(a, bins=40)

plt.show()
