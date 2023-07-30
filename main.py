import sqlite3

import astroplan
from ossaf.assess import *
from utils import obs_start, obs_end, observer

# connect to database
conn = sqlite3.connect('ossaf/data/tyc2.sqlite')

# read candidate
candidates = pd.read_sql('select * from candidate_2023_06_08_00_00_00', con=conn)

# read Cloud
cloud = pd.read_sql('select * from "clear_2023-06-11T10:00:35.690250"', con=conn, index_col='index')
cloud.iloc[:, 1::] = 1 - cloud.iloc[:, 1::]
cloud.index = cloud.index.astype('datetime64')
cloud = cloud.iloc[cloud.index.argsort()]
cloud.columns = cloud.columns.astype(int)
weather = Weather(Cloud(cloud))

# read Plan
asp_priority_plan = pd.read_sql('select * from priority_schedule_2023_06_08_00_00_00', con=conn)
asp_sequantial_plan = pd.read_sql('select * from sequential_schedule_2023_06_08_00_00_00', con=conn)

# asp_plans = [asp_priority_plan, asp_sequantial_plan]
asp_plans = {"priority": asp_priority_plan, "sequential": asp_sequantial_plan}

# overall result
result_total = pd.DataFrame(index=asp_plans.keys(), columns=['overhead', 'scientific_score', 'expected_quality', 'scheduled_rate','cloud', 'airmass'])

for asp_name, asp_plan in asp_plans.items():
    asp_plan['start'] = asp_plan['start'].astype('datetime64')
    asp_plan['end'] = asp_plan['end'].astype('datetime64')

    asp_plan = asp_plan.rename(columns={'name': 'id',
                                        'start': 'start_time',
                                        'end': 'end_time',
                                        'RA_ICRS_': 'ra',
                                        'DE_ICRS_': 'dec',
                                        'VTmag': 'mag'})

    plan = Plan(asp_plan)

    ossaf = Ossaf(observer, plan, None, candidates=candidates, weather=weather, obs_start=obs_start, obs_end=obs_end)

    result = ossaf.run()

    print(asp_name, " ========================== ")
    print(result['total'])
    result_total.loc[asp_name] = result['total']

    result['score'].to_csv(f'{asp_name}_score.csv', index='id')

result_total.to_csv("score.csv")
print("end")
