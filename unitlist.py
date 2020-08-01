'''Class for available leases'''
# %%
import pandas as pd
from collections import Counter
import numpy as np


class Units(object):
    def __init__(self):

        def get_all_units() -> dict:
            # returns {unitname: (total n. units, unit area)}
            df = pd.read_csv('leases.csv')
            unit_type = 'Type (U=Upstairs, D=Downstairs)'

            area = df['Width (m)'].mul(df['Length (m)']).round(2)

            # --- available unit sizes
            self.available = Counter(sorted(list(area)))

            area.index = df[unit_type]
            area = area.loc[area.index.drop_duplicates()].to_dict()

            all_units = df[unit_type].value_counts().to_dict()
            all_units = {k: (v, area[k]) for k, v in all_units.items()}

            return all_units

        self.all_units = get_all_units()
        self.units_occupied = {}  # {moveout_date: [unit sizes with that moveout date]}

    def attempt_booking(self, size, when, p=1, ndays=590) -> bool:
        '''
        Parameters:
        ----------
        size: Room size required (sqm)

        when: Indicative start date of storage lease

        p: customer conversion rate

        ndays: Length of storage lease duration

        Assumptions:
        -----------
        Customers accept units between 100-200% of their requirement (hardcoded)
        '''

        # --- stochastic element here
        if np.random.rand() > p:
            # booking is not made
            return True  # Return true to allow booking attempts to continue

        availability = False
        for i in self.available:
            if i >= size and i <= (2 * size) and self.available[i] > 0:
                availability = True

                # book unit: record end date, size
                end = when + pd.Timedelta(f'{ndays}d')
                units_movingout = self.units_occupied.get(end, []) + [i]
                self.units_occupied[end] = units_movingout

                # remove a room from available rooms
                self.available[i] = self.available[i] - 1
                break

        return availability

    def move_out(self, date):
        '''Automatically remove date from self.units_occupied, add rooms
        back to self.available list'''
        free_rooms = self.units_occupied.pop(date, [])

        # if len(free_rooms) > 0:
        #     print(len(free_rooms), 'units moved out today')

        for i in free_rooms:
            if self.available.pop(round(i, 2), None) is None:
                print(free_rooms)

            self.available[round(i, 2)] = self.available[round(i, 2)] + 1
