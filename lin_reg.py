
# %%

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_csv('leases.csv')
df['Type'] = ['Locker' if i == 'Locker' else i[-1] for i in df['Type (U=Upstairs, D=Downstairs)']]
df['Area'] = df['Width (m)'] * df['Length (m)']

rate = 'Standard Rate (/month)'

convert = [rate,
           'Avg. Stay (days)']

for i in convert:
    df[i] = df[i].replace('[\$,]', '', regex=True).astype(float)

df0 = df[['Area', rate, 'Type']]
df0.columns = ['area', 'rate', 'Type']

plt.figure(figsize=(7, 5))
ax = sns.scatterplot(x='area', y='rate', hue='Type', data=df0, s=20, alpha=0.6)
ax.set_ylabel('Rate ($)')
ax.set_xlabel('Area $(m^2)$')

plt.show()

# %%

plt.figure(figsize=(7, 5))
# ax = sns.scatterplot(x='Avg. Stay (days)', y='Avg. Re-Lease (days)', data=df, hue='Type')
ax = sns.scatterplot(x='Avg. Stay (days)', y=rate, data=df, hue='Type')

plt.show()

# %%

df0 = df[[rate, 'Area', 'Avg. Stay (days)', 'Avg. Re-Lease (days)', 'Type']]
df0.columns = ['Standard Rate ($)', 'Area $(m^2)$'] + list(df0.columns[2:])

# NOTE: the var of standard rate != 0 due to floating point error
# This is a hack to prevent sns from plotting the KDE of rate
# which becomes very large as var -> 0
df0['Standard Rate ($)'] = [86.3602 if i == 86.36 else i for i in df0['Standard Rate ($)']]

g = sns.pairplot(df0, hue='Type')

plt.show()
# plt.savefig('Pairplot.png', dpi=300, bbox_inches='tight')
