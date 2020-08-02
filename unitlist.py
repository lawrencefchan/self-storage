
'''Class for available leases'''
# %%
import json
import pandas as pd
import numpy as np


class Units(object):
    def __init__(self, start, seed='default', increase=None):
        '''Parameters:
        ----------
        start: simulation start date (pd.Timestamp)

        seed: unit occupancy at start of simulation. May be one of:
            * default: load current occupancy from leases.csv
            * empty: all rooms are empty
        '''

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

        def init_max_capacity(self, increase=None) -> dict:
            '''temporary code that extracts max capacity from json file
            This may be updated to dynamically adjust to different scenarios
            '''

            with open('available_units_default.json') as json_file:
                max_capacity = json.load(json_file)

            if increase in max_capacity.keys():
                max_capacity[increase] = max_capacity[increase] + 1

            self.max_capacity = max_capacity
            return

        def init_average_stay(self) -> dict:
            '''Function to get average stay per unit size from json file'''

            with open('average_stay.json') as json_file:
                average_stay = json.load(json_file)

            self.average_stay = average_stay
            return

        def init_seed(self, seed):
            with open('seed_occupancy_default.json') as json_file:
                available = json.load(json_file)

            if seed == 'default':
                pass
            elif seed == 'full':
                available = {k: 0 for k, v in available.items()}
            elif seed == 'empty':
                available = {k: v for k, v in self.max_capacity.items()}
            # elif type(seed) is float:
            #     available = {k: int((1-seed) * v) for k, v in self.max_capacity.items()}

            else:
                raise KeyError('Unknown seed.')

            self.available = available
            return

        def init_moveout_dates(self, start, ndays=1000) -> dict:
            '''This function will randomly assign unit moveout dates based on average
            stay distribution to units currently occupied.

            It uses the difference between maximum capacity (self.max_capacity)
            and units currently available (self.available).

            Parameters:
            ----------
            start: simulation start date (pd.Timestamp)

            ndays: DEPRECATED [0, ndays] is the range of moveout dates generated

            Returns {moveout_date: [unit sizes with that moveout date]}
            '''

            # 
            units_occupied = {}
            for size, n_units in self.max_capacity.items():
                s = self.average_stay[size]
                for unit in range(n_units - self.available[size]):
                    moveout_date = start + pd.Timedelta(np.random.randint(s), unit='D')
                    units_occupied[moveout_date] = units_occupied.get(moveout_date, []) + [size]

            # # --- uniform distribution
            # days_occupied = np.random.randint(ndays, size=len(units))
            # days_occupied = [start + pd.Timedelta(int(i), unit='D') for i in days_occupied]

            # from collections import defaultdict
            # # use defaultdict to append to keys not already in dict
            # units_occupied = defaultdict(list)
            # for k, v in zip(days_occupied, units):
            #     units_occupied[k].append(v)

            self.units_occupied = units_occupied

        # self.all_units = get_all_units()
        init_max_capacity(self, increase=increase)
        init_average_stay(self)
        init_seed(self, seed)
        init_moveout_dates(self, start)

    def attempt_booking(self, req_size, when, p=1, ndays=590) -> bool:
        '''
        Parameters:
        ----------
        size: Room size required (sqm)

        when: Indicative start date of storage lease

        p: customer conversion rate

        ndays: DEPRECATED: Length of storage lease duration

        Assumptions:
        -----------
        Customers accept units between 90-150% of their requirement(hardcoded)
        '''

        # --- stochastic element here
        if np.random.rand() > p:  # booking is not made but return True to
            return True           # allow booking attempts to continue

        # self.debug = 0

        availability = False
        for size in self.available:
            if (float(size) >= 0.9*req_size
                    and float(size) <= 1.5*req_size
                    and self.available[size] > 0):
                availability = True

                # book unit: record end date, size
                avg_ndays = self.average_stay[size]
                ndays = int(np.random.normal(avg_ndays, avg_ndays * 0.015))
                # integer number of days needed otherwise move_out() wont work
                # ndays = 590

                end = when + pd.Timedelta(f'{int(ndays)}d')
                units_movingout = self.units_occupied.get(end, []) + [size]
                self.units_occupied[end] = units_movingout

                # remove a room from available rooms
                self.available[size] = self.available[size] - 1

                # if self.debug == 0:
                #     print(i, self.available[i])
                # self.debug = 1

                break

        return availability

    def move_out(self, date):
        '''This function will:
        * remove date from self.units_occupied
        * add rooms back to self.available (dict)
        '''
        free_rooms = self.units_occupied.pop(date, [])

        self.free_rooms = len(free_rooms)  # debuging
        # if len(free_rooms) > 0:
        #     print(len(free_rooms), 'units moved out today')

        for i in free_rooms:
            if self.available.get(i, None) is None:
                print(free_rooms)

            self.available[i] = self.available[i] + 1
