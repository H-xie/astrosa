"""
绘制路径
"""
import pandas as pd

import ossaf.plot.sky

import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.style.use("dark_background")

score = pd.read_csv('score167.csv', index_col=0)

result = ossaf.plot.sky.add_altaz(score)

# ossaf.plot.sky.trace(result)
full_data = ossaf.plot.sky.ani_trace(result)
print(full_data)
