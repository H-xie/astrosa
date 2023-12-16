import sqlite3

import numpy as np
import pandas as pd

from astrosa.assess import Cloud, Weather, Plan, Assessor
from astrosa.tests.utils import observer, obs_end, obs_start

conn_astrosa = sqlite3.connect('astrosa/data/astrosa.sqlite')


def test_cloud_set_mask():
    # connect to database
    conn = sqlite3.connect('astrosa/data/astrosa.sqlite')

    # read candidate
    candidates = pd.read_sql('select * from candidate_2023_06_08_00_00_00', con=conn)

    # read Cloud
    cloud_data = pd.read_sql('select * from cloud_2023_06_08_00_00_00', con=conn, index_col='index')
    cloud_data.index = cloud_data.index.astype('datetime64[ns]')
    cloud_data = cloud_data.iloc[cloud_data.index.argsort()]
    cloud_data.columns = cloud_data.columns.astype(int)
    cloud_data = cloud_data.astype(float)

    mask = np.zeros(cloud_data.shape[1], dtype=bool)
    mask[0:10] = True

    cloud = Cloud(cloud_data)
    cloud.set_mask(mask)

    weather = Weather(cloud)

    # read Plan
    asp_priority_plan = pd.read_sql('select * from priority_schedule_2023_06_08_00_00_00', con=conn)
    asp_sequantial_plan = pd.read_sql('select * from sequential_schedule_2023_06_08_00_00_00', con=conn)

    asp_plans = {"priority": asp_priority_plan, "sequential": asp_sequantial_plan}

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

        ossaf = Assessor(observer, plan, None, candidates=candidates, weather=weather, obs_start=obs_start,
                         obs_end=obs_end)

        result = ossaf.run()

        print(asp_name, " ========================== ")
        print(result['total'])
        result_total.loc[asp_name] = result['total']

        result['score'].to_csv(f'{asp_name}_score.csv', index='id')

    result_total.to_csv("score.csv")
    print("end")
