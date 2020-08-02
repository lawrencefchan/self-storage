
'''Class for available leases'''
# %%
import json
import pandas as pd
import numpy as np


class Units(object):
    def __init__(self, start):

        def get_all_units() -> dict:
            # returns {unitname: (total n. units, unit area)}
            df = pd.read_csv('leases.csv')
            unit_type = 'Type (U=Upstairs, D=Downstairs)'

            area = df['Width (m)'].mul(df['Length (m)']).round(2)

            # # --- available unit sizes
            # NOTE: this gives default (max) availability
            # self.available = Counter(sorted(list(area)))

            area.index = df[unit_type]
            area = area.loc[area.index.drop_duplicates()].to_dict()

            all_units = df[unit_type].value_counts().to_dict()
            all_units = {k: {'availability': v, 'room size': area[k]} for k, v in all_units.items()}

            return all_units

        def get_max_capacity() -> dict:
            '''temporary code that extracts max capacity from json file
            This may be updated to dynamically adjust to different scenarios
            '''

            with open('available_units_default.json') as json_file:
                max_capacity = json.load(json_file)

            return max_capacity

        def get_seed():
            with open('seed_occupancy_default.json') as json_file:
                seed = json.load(json_file)
            return seed

        def init_moveout_dates(self, start, ndays=1000) -> dict:
            '''This function will randomly assign unit moveout dates using some
            distribution (?) to units currently occupied (on init).

            It uses the difference between maximum capacity (self.max_capacity)
            and units currently available (self.available).

            Parameters:
            ----------
            start: simulation start date (pd.Timestamp)

            ndays: [0, ndays] is the range of moveout dates generated

            Returns {moveout_date: [unit sizes with that moveout date]}
            '''
            units = []

            for size, n_units in self.max_capacity.items():
                # append size of each occupied unit to list
                units += (n_units - self.available[size]) * [size]

            # --- uniform distribution
            days_occupied = np.random.randint(ndays, size=len(units))

            # --- exponential distribution
            # days_occupied = np.random.exponential(300, size=len(units))

            # --- lognormal distribution
            # days_occupied = np.random.lognormal(6, 0.05, size=len(units))

            # --- normal distribution
            # days_occupied = np.random.normal(loc=500, scale=180, size=len(units))
            # days_occupied = [_ if _ < 0 else _ for _ in days_occupied]

            days_occupied = [start + pd.Timedelta(int(i), unit='D') for i in days_occupied]

            from collections import defaultdict
            # use defaultdict to append to keys not already in dict without errors
            units_occupied = defaultdict(list)
            for k, v in zip(days_occupied, units):
                units_occupied[k].append(v)

            return units_occupied

        # self.all_units = get_all_units()
        self.max_capacity = get_max_capacity()
        self.available = get_seed()
        self.units_occupied = init_moveout_dates(self, start)

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
            if float(i) >= size and float(i) <= (2 * size) and self.available[i] > 0:
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
        '''This function will:
        * remove date from self.units_occupied
        * add rooms back to self.available (dict)
        '''
        free_rooms = self.units_occupied.pop(date, [])

        # if len(free_rooms) > 0:
        #     print(len(free_rooms), 'units moved out today')

        for i in free_rooms:
            if self.available.get(i, None) is None:
                print(free_rooms)

            self.available[i] = self.available[i] + 1
