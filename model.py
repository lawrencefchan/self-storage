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



'''

# %%

import pandas as pd
import unitlist as ul
import json
from importlib import reload

reload(ul)


def get_data():
    df = pd.read_csv('DataSet2_clean.csv')

    for i in [when, 'Create Date']:
        df[i] = pd.to_datetime(df[i])

    return df


with open(f'available_units_default.json') as json_file:
    max_capacity = json.load(json_file)

when = 'When do you require storage'
size = 'Room size required in sqmtrs (1)'

df = get_data()[[size, when, 'Create Date']] \
    .dropna(how='any') \
    .sort_values('Create Date')

# %%
u = ul.Units()

start = df['Create Date'][0]
end = df['Create Date'][9997]
dr = pd.date_range(start=start, end=end)


BREAK = False
reservations = []

for date in dr:
    d = df[df['Create Date'] == date]

    # display(d)
    u.move_out(date)

    for row in d.itertuples():
        if not u.attempt_booking(row._1, row._2, ndays=71):
            print(date, 'NO MORE ROOM!!')
            # BREAK = True
            break

    # if BREAK:
    #     break

    # --- number of units reserved
    reserved = sum({k: max_capacity[str(k)] - u.available[k] for k in u.available}.values())
    reservations += [reserved]

# %% plot total reservations

import matplotlib.pyplot as plt

# plt.plot(reservations)
ax = pd.Series(data=reservations, index=dr).plot()
ax.set_ylabel('Total no. reservations')



# %% WIP: conversion rate (monthly)


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

