from ossaf.plot import plot_cloud
import matplotlib.pyplot as plt
import pandas as pd

data = pd.read_json('ossaf/data/cloud.json')

plot_cloud(data.iloc[:, 0])
plt.gcf().savefig('cloud.svg')

plt.show()
