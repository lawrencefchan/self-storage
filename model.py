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


def run_simulation(**kawrgs):
    u = ul.Units(start=start)

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


# %% plot total reservations
n = 100

start = df['Create Date'][0]
end = df['Create Date'][9997]
dr = pd.date_range(start=start, end=end)

fig, ax = plt.subplots(figsize=(13, 8))
for i in range(n):
    reservations = run_simulation(start=start)
    pd.Series(data=reservations, index=dr).plot(ax=ax, alpha=0.7)

ax.set_ylabel('Total Occupancy')
ax.set_title(f'Stochastic model (n={n})')

plt.savefig(f'plots/total_occupancy_n={n}.png', dpi=300)

# %% WIP: conversion rate (monthly)

when = 'When do you require storage'
size = 'Room size required in sqmtrs (1)'


def calc_p_reservation(size, date):
    pass


df['month'] = df[when].dt.month

df['Enquiry Status'] = [True if _ == 'Reserved' else False for _ in df['Enquiry Status']]
for mth, d in df.groupby('month'):
    # display(d)
    # print(mth)

    break

d = d.sort_values('Create Date')[[when, size, 'Enquiry Status']]

for i in d[size].unique():
    display(d[d[size] == i])

    break

# u.all_units

