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
* check that u.all_units dictionary works
* convert seeds to json files for easy loading
* add moveout dates for seed occupancy

'''

# %%
import matplotlib.pyplot as plt
import pandas as pd
import unitlist as ul
import json
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
        .sort_values('Create Date')


def run_simulation(u, dr, **kawrgs):
    '''
    Parameters:
    ----------

    u: storage unit class

    dr: simulation date range
    '''

    reservations = []

    for date in dr:
        d = df[df['Create Date'] == date]

        # display(d)
        u.move_out(date)

        for row in d.itertuples():
            size = row._1
            when = row._2
            if not u.attempt_booking(size, when, p=0.2, ndays=590):
                # print(date, 'NO MORE ROOM!!')
                break

        # --- number of units reserved
        reserved = sum({k: u.max_capacity[str(k)] - u.available[k] for k in u.available}.values())
        reservations += [reserved]

    return reservations


# --- %% plot total reservations
from datetime import datetime
n = 5

start = df['Create Date'][0]
end = df['Create Date'][9997]
dr = pd.date_range(start=start, end=end)


sim_data = []
t0 = datetime.now()
for i in range(n):
    u = ul.Units(start=start)

    reservations = run_simulation(u=u, dr=dr)
    sim_data += [reservations]

print(n, 'simulations took', datetime.now() - t0)

sim_data = pd.DataFrame(sim_data, columns=dr).T

fig, ax = plt.subplots()  # figsize=(13, 8))
sim_data.plot(ax=ax, legend=False)
ax.set_ylabel('Total Occupancy')
ax.set_title(f'Stochastic model (n={n})')

saveas = f'total_occupancy_n={n}_historical'
# sim_data.to_csv(f'{saveas}.csv')
# plt.savefig(f'plots/{saveas}.png', dpi=300)



# %% plot sim_data


sim_data = pd.read_csv('total_occupancy_n=100_historical.csv')
sim_data.index = pd.to_datetime(sim_data['Unnamed: 0'])
sim_data.index.name = 'date'
sim_data = sim_data.drop('Unnamed: 0', axis=1)

# %%
fig, ax = plt.subplots(figsize=(13, 8))
(sim_data/7.54).plot(ax=ax, legend=False, alpha=0.4, lw=1)
ax.set_ylabel('Total Occupancy (%)')
ax.set_title(f'Stochastic model (n={n})')



# %%
import numpy as np

# target = 250
# beta = 1.0/target

# Y = np.random.exponential(beta, 5000)
# plt.hist(Y, normed=True, bins=200,lw=0,alpha=.8)


a = np.random.exponential(1000, size=1000)
a = np.random.normal(loc=500, scale=180, size=1000)

plt.hist(a, bins=40)

plt.show()
