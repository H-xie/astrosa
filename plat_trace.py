"""
绘制路径
"""
import pandas as pd

import plot.sky

score = pd.read_csv('data/result/score15.csv', index_col=0)

result = plot.sky.add_altaz(score)

plot.sky.trace(result)
full_data = plot.sky.ani_trace(result)
print(full_data)
