#  Licensed under the MIT license - see LICENSE.txt
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

from astrosa.plot import plot_cloud

conn = sqlite3.connect('astrosa/data/astrosa.sqlite')
data = pd.read_sql_query('select * from cloud_2023_06_08_00_00_00', con=conn, index_col='index')
data = data.astype(float)

one_cloud = data.iloc[10, :]
plot_cloud(one_cloud)
plt.gcf().savefig('cloud.svg')
plt.gcf().savefig('cloud.png')

one_cloud.to_csv('cloud.csv', index=False)

plt.show()
