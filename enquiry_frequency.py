# %% historical monthly enquiry frequency

import pandas as pd
import matplotlib.pyplot as plt


when = 'When do you require storage'
size = 'Room size required in sqmtrs (1)'


def calc_p_reservation(size, date):
    pass


def get_data():
    df = pd.read_csv('DataSet2_clean.csv')

    for i in [when, 'Create Date']:
        df[i] = pd.to_datetime(df[i])

    return df


df = get_data()

enq_freq = {}
for date, d in df.groupby([when]):
    enq_freq[date] = d.shape[0]

s = pd.Series(enq_freq, name='Enquiry Frequency').resample('1D').mean()
df = pd.DataFrame(s)


df['Day'] = df.index.strftime('%m-%d')
df['Year'] = df.index.year

df = pd.pivot_table(df,index='Day',columns='Year',values='Enquiry Frequency')
df.index = pd.date_range('2020-01-01', '2020-12-31', freq='d')

# %% plot daily
ax = df.plot()
dr = pd.date_range('2020-01-01', '2020-12-31', freq='MS')
ax.set_xticklabels([i[:3] for i in dr.month_name()])

ax.set_xlabel('Month that storage was required')
ax.set_ylabel('Enquiry Frequency')

ax.grid(which='major')
ax.set_title('Daily Enquiry Frequency by Year ',
             loc='left',
             fontdict={'fontsize': 16},
             pad=10,
             c='0.3')

plt.savefig('plots/enquiryfreq_daily.png',
            dpi=300,
            bbox_inches='tight',
            transparent=False)


# %% plot monthly
month_df = df.resample('MS').sum()
ax = month_df.plot()
month_df.iloc[:, :3].mean(axis=1).plot(ax=ax, lw=5, c='k', alpha=0.7, label='Averge')

dr = pd.date_range('2020-01-01', '2020-12-31', freq='MS')
ax.set_xticklabels([i[:3] for i in dr.month_name()])

ax.set_xlabel('Month that storage was required')
ax.set_ylabel('Monthly Total Enquiry Frequency')

ax.grid(which='both')
ax.legend(loc='lower right', title='Year')

ax.set_title('Monthly Enquiry Frequency by Year ',
             loc='left',
             fontdict={'fontsize': 16},
             pad=10,
             c='0.3')

plt.savefig('plots/enquiryfreq_monthly.png',
            dpi=300,
            bbox_inches='tight',
            transparent=False)
