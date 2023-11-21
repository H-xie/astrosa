#  Licensed under the MIT license - see LICENSE.txt

import sqlite3

from astrosa.assess import *
from utils import obs_start, obs_end, observer

# connect to database
conn = sqlite3.connect('astrosa/data/astrosa.sqlite')

# read candidate
candidates = pd.read_sql('select * from candidate_2023_06_08_00_00_00', con=conn)

# read Cloud
cloud = pd.read_sql('select * from cloud_2023_06_08_00_00_00', con=conn, index_col='index')
cloud.index = cloud.index.astype('datetime64[ns]')
cloud = cloud.iloc[cloud.index.argsort()]
cloud.columns = cloud.columns.astype(int)
cloud = cloud.astype(float)
weather = Weather(Cloud(cloud))

# read Plan
asp_priority_plan = pd.read_sql('select * from priority_schedule_2023_06_08_00_00_00', con=conn)
asp_sequential_plan = pd.read_sql('select * from sequential_schedule_2023_06_08_00_00_00', con=conn)

asp_plans = {"priority": asp_priority_plan, "sequential": asp_sequential_plan}

# overall result
result_total = pd.DataFrame(index=asp_plans.keys(),
                            columns=['overhead', 'scientific_score', 'expected_quality', 'scheduled_rate', 'cloud',
                                     'airmass'])

for asp_name, asp_plan in asp_plans.items():
    asp_plan['start'] = asp_plan['start'].astype('datetime64[ns]')
    asp_plan['end'] = asp_plan['end'].astype('datetime64[ns]')

    asp_plan = asp_plan.rename(columns={'name': 'id',
                                        'start': 'start_time',
                                        'end': 'end_time',
                                        'RA_ICRS_': 'ra',
                                        'DE_ICRS_': 'dec',
                                        'VTmag': 'mag'})

    plan = Plan(asp_plan)

    ossaf = Assessor(observer, plan, None, candidates=candidates, weather=weather, obs_start=obs_start, obs_end=obs_end)

    result = ossaf.run()

    print(asp_name, " ========================== ")
    print(result['total'])
    result_total.loc[asp_name] = result['total']

    result['score'].to_csv(f'{asp_name}_score.csv', index='id')

result_total.to_csv("score.csv")
print("end")
