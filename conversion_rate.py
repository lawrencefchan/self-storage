
# %% historical conversion rate (monthly)
import pandas as pd
import matplotlib.pyplot as plt


when = 'When do you require storage'
size = 'Room size required in sqmtrs (1)'


def calc_p_reservation(size, date):
    pass


def get_data():
    df = pd.read_csv('DataSet2_clean.csv')

    for i in ['When do you require storage', 'Create Date']:
        df[i] = pd.to_datetime(df[i])

    return df


df = get_data()

df['month'] = df[when].dt.month
df['year'] = df[when].dt.year

df['Enquiry Status'] = [True if _ == 'Reserved'
                        else False for _ in df['Enquiry Status']]

conversion_rate = {}
for mth, d in df.groupby(['month', 'year']):
    date = pd.Timestamp(year=mth[1], month=mth[0], day=1)
    conversion_rate[date] = round(d['Enquiry Status'].sum() / d.shape[0], 3)

s = pd.Series(conversion_rate, name='Conversion Rate').resample('1MS').mean()

df = {}
for y in s.index.year.unique():
    df[y] = list(s[f'{y}'])

df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in df.items()]))
df.index = pd.date_range('2020-01-01', '2020-12-01', freq='MS')

# %%
ax = df.plot()
df.iloc[:, :3].mean(axis=1).plot(ax=ax, lw=5, c='k', alpha=0.7, label='Averge')
ax.legend()

ax.set_xticklabels(df.index.month_name())

ax.set_xlabel('Month that storage was required')
ax.set_ylabel('Conversion Rate')

ax.grid(which='both')
ax.set_title('Conversion Rate by Year ',
             loc='left',
             fontdict={'fontsize': 16},
             pad=10,
             c='0.3')

# plt.savefig('plots/conversionrate.png',
#             dpi=300,
#             bbox_inches='tight',
#             transparent=False)
