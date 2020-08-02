'''Run scenarios'''

# %%
import json
import matplotlib.pyplot as plt
import pandas as pd
import unitlist as ul
import numpy as np
from datetime import datetime

from importlib import reload

reload(ul)


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


def get_data():
    df = pd.read_csv('DataSet2_clean.csv')

    for i in ['When do you require storage', 'Create Date']:
        df[i] = pd.to_datetime(df[i])

    return df


when = 'When do you require storage'
df = get_data().sort_values('Create Date')[['Room size required in sqmtrs (1)',
                                            'When do you require storage',
                                            'Create Date',
                                            'Enquiry Status']]

df = df[df['Enquiry Status'] == 'Reserved']

start = list(df['Create Date'])[0]
end = list(df['Create Date'])[-1]
dr = pd.date_range(start=start, end=end)

with open('seed_occupancy_default.json') as json_file:
    available = json.load(json_file)

for increase in available.keys():
    n = 50

    sim_data = []
    t0 = datetime.now()
    for i in range(n):
        u = ul.Units(start=start, seed='default', increase=increase)

        reservations = run_simulation(u=u, dr=dr)
        sim_data += [reservations]

    print(n, 'simulations took', datetime.now() - t0)

    sim_data = pd.DataFrame(sim_data, columns=dr).T

    # fig, ax = plt.subplots()  # figsize=(13, 8))
    # sim_data.plot(ax=ax, legend=False, alpha=0.6)
    # ax.set_ylabel('Total Occupancy')
    # ax.set_title(f'Stochastic model (n={n}), (ndays=365)')

    saveas = f'increase_{increase}_scenario'
    sim_data.to_csv(f'{saveas}.csv')
