from plot.sky import plot_cloud
import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_json('assess/tests/data/cloud.json')

plot_cloud(data.iloc[:, 0])
plt.gcf().savefig('cloud.svg')

plt.show()
