#  Licensed under the MIT license - see LICENSE.txt
import os
import sqlite3

import pandas as pd

from astrosa import plot
from astrosa.assess import *
from utils import obs_start, obs_end, observer

# folder
folder_name = os.path.join('experiments', 'longshort')
os.makedirs(folder_name, exist_ok=True)

# connect to database
conn = sqlite3.connect('astrosa/data/astrosa.sqlite')

# read candidate
candidates = pd.read_sql('select * from longshort_candidates_2023_06_08_00_00_00', con=conn)

# read Cloud
cloud_data = pd.read_sql('select * from cloud_2023_06_08_00_00_00', con=conn, index_col='index')
cloud_data.index = cloud_data.index.astype('datetime64[ns]')
cloud_data = cloud_data.iloc[cloud_data.index.argsort()]
cloud_data.columns = cloud_data.columns.astype(int)
cloud_data = cloud_data.astype(float)

cloud = Cloud(cloud_data)

weather = Weather(cloud)



# read Plan
asp_priority_plan = pd.read_sql('select * from priority_schedule_2023_06_08_00_00_00_longshort', con=conn)
asp_sequantial_plan = pd.read_sql('select * from sequential_schedule_2023_06_08_00_00_00_longshort', con=conn)

asp_plans = {"priority": asp_priority_plan, "sequential": asp_sequantial_plan}

# overall result
result_total = pd.DataFrame(index=asp_plans.keys(),
                            columns=['overhead', 'scientific_score',
                                     'expected_quality',
                                     'scheduled_rate_in_request',
                                     'scheduled_rate_in_time',
                                     'cloud',
                                     'ratio_to_best_airmass',
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

    result['score'].to_csv(f'{folder_name}/{asp_name}_score.csv', index='id')

    result_for_plot = plot.sky.add_altaz(result['score'])
    plot.sky.trace(result_for_plot, f'{folder_name}/{asp_name}_trace')

result_total.to_csv(f'{folder_name}/score.csv')
print("end")
