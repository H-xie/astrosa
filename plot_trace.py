"""
绘制路径
"""
import sqlite3

import pandas as pd

import ossaf.plot.sky

import matplotlib.pyplot as plt
import matplotlib as mpl

# mpl.style.use("dark_background")

score = pd.read_csv('priority_score.csv', index_col=0)
# score = pd.read_csv('sequential_score.csv', index_col=0)

result = ossaf.plot.sky.add_altaz(score)

ossaf.plot.sky.trace(result)
full_data = ossaf.plot.sky.ani_trace(result)
print(full_data)
