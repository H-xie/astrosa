"""
绘制路径
"""
#  Licensed under the MIT license - see LICENSE.txt

import sqlite3

import pandas as pd

import astrosa.plot.sky

import matplotlib.pyplot as plt
import matplotlib as mpl

# mpl.style.use("dark_background")

score = pd.read_csv('priority-result/priority_score.csv', index_col=0)
# score = pd.read_csv('sequential_score.csv', index_col=0)

result = astrosa.plot.sky.add_altaz(score)

astrosa.plot.sky.trace(result)
full_data = astrosa.plot.sky.ani_trace(result)
print(full_data)
