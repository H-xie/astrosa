import pandas as pd
from rich.progress import Progress, TimeElapsedColumn, track

import astroplan
from assess import *
from utils import df2Targets, obs_start, obs_end

# scheduler = Scheduler()

# create Plan
asp_priority_plan = pd.read_json('assess/tests/data/schedule_15of30.json')
asp_priority_plan['start'] = asp_priority_plan['start'].astype('datetime64')
asp_priority_plan['end'] = asp_priority_plan['end'].astype('datetime64')

asp_priority_plan = asp_priority_plan.rename(columns={'name': 'id',
                                                      'start': 'start_time',
                                                      'end': 'end_time',
                                                      '_RAJ2000': 'ra',
                                                      '_DEJ2000': 'dec',
                                                      'VTmag': 'mag'})

plan = Plan(asp_priority_plan)

# create Cloud
cloud = pd.read_json("assess/tests/data/cloud.json", orient='index')
weather = Weather(Cloud(cloud))
observer = astroplan.Observer.at_site("BAO")

ossaf = Ossaf(observer, plan, None, weather, obs_start=obs_start, obs_end=obs_end)

result = ossaf.run()

print(result)

result['score'].to_csv('score15.csv')

print("end")
