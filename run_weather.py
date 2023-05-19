from ossaf.assess import *
import pandas as pd

cloud = pd.read_json("ossaf/assess/test/data/cloud.json")
weather = Weather(Time('2023-01-01 16:00:00'), cloud)

print(weather.cloud[0])
