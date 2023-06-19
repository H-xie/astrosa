import sqlite3

import astroplan
from ossaf.assess import *
from utils import obs_start, obs_end, observer

# scheduler = Scheduler()

# create Plan
conn = sqlite3.connect('ossaf/data/tyc2.sqlite')
asp_priority_plan = pd.read_sql('select * from priority_schedule_2023_06_08_00_00_00', con=conn)
asp_priority_plan['start'] = asp_priority_plan['start'].astype('datetime64')
asp_priority_plan['end'] = asp_priority_plan['end'].astype('datetime64')

asp_priority_plan = asp_priority_plan.rename(columns={'name': 'id',
                                                      'start': 'start_time',
                                                      'end': 'end_time',
                                                      'RA_ICRS_': 'ra',
                                                      'DE_ICRS_': 'dec',
                                                      'VTmag': 'mag'})

plan = Plan(asp_priority_plan)

# read Cloud
cloud = pd.read_sql('select * from clear', con=conn, index_col='index')
cloud.iloc[:, 1::] = 1 - cloud.iloc[:, 1::]
cloud.index = cloud.index.astype('datetime64')
cloud = cloud.iloc[cloud.index.argsort()]
cloud.columns = cloud.columns.astype(int)
weather = Weather(Cloud(cloud))

ossaf = Ossaf(observer, plan, None, weather, obs_start=obs_start, obs_end=obs_end)

result = ossaf.run()

print(result)

result['score'].to_csv('score.csv')

print("end")
