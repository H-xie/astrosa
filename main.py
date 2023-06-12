import astroplan
from ossaf.assess import *
from utils import obs_start, obs_end, observer

# scheduler = Scheduler()

# create Plan
# asp_priority_plan = pd.read_json('ossaf/data/schedule_15of30.json')
asp_priority_plan = pd.read_json('schedule_167of1000.json')
asp_priority_plan['start'] = asp_priority_plan['start'].astype('datetime64')
asp_priority_plan['end'] = asp_priority_plan['end'].astype('datetime64')

asp_priority_plan = asp_priority_plan.rename(columns={'name': 'id',
                                                      'start': 'start_time',
                                                      'end': 'end_time',
                                                      '_RAJ2000': 'ra',
                                                      '_DEJ2000': 'dec',
                                                      'VTmag': 'mag'})

plan = Plan(asp_priority_plan)

# read Cloud
cloud = pd.read_json("ossaf/data/cloud.json", orient='index')
weather = Weather(Cloud(cloud))

ossaf = Ossaf(observer, plan, None, weather, obs_start=obs_start, obs_end=obs_end)

result = ossaf.run()

print(result)

result['score'].to_csv('score167.csv')

print("end")
