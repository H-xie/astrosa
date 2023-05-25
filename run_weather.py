from ossaf.assess import *
import pandas as pd

cloud = pd.read_json("ossaf/data/cloud.json")
weather = Weather(cloud)

print(weather.cloud.iloc[:, 0])
