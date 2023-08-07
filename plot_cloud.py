#  Licensed under the MIT license - see LICENSE.txt
import sqlite3

import matplotlib.pyplot as plt
import pandas as pd

from astrosa.plot import plot_cloud

conn = sqlite3.connect('astrosa/data/astrosa.sqlite')
data = pd.read_sql_query('select * from cloud_2023_06_08_00_00_00', con=conn, index_col='index')
# data = pd.read_json('astrosa/data/cloud.json')

plot_cloud(data.iloc[1, :])
plt.gcf().savefig('cloud.svg')

plt.show()
