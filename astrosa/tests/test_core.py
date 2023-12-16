#  Licensed under the MIT license - see LICENSE.txt
import sqlite3
import unittest

import astroplan
import pandas as pd

from astrosa.assess import Assessor, Plan, Weather, Cloud
from utils import obs_start, obs_end


class TestAssessor(unittest.TestCase):

    def test_init(self):
        observer = astroplan.Observer.at_site('BAO')

        conn_astrosa = sqlite3.connect('astrosa/data/astrosa.sqlite')
        # read candidates
        candidates = pd.read_sql('select * from candidate_2023_06_08_00_00_00', con=conn_astrosa)

        # read Cloud
        cloud = pd.read_sql('select * from cloud_2023_06_08_00_00_00', con=conn_astrosa, index_col='index')
        cloud.index = cloud.index.astype('datetime64[ns]')
        cloud = cloud.iloc[cloud.index.argsort()]
        cloud.columns = cloud.columns.astype(int)
        cloud = cloud.astype(float)
        weather = Weather(Cloud(cloud))

        # read plan
        asp_plan = pd.read_sql('select * from priority_schedule_2023_06_08_00_00_00', con=conn_astrosa)
        asp_plan['start'] = asp_plan['start'].astype('datetime64[ns]')
        asp_plan['end'] = asp_plan['end'].astype('datetime64[ns]')

        asp_plan = asp_plan.rename(columns={'name': 'id',
                                            'start': 'start_time',
                                            'end': 'end_time',
                                            'RA_ICRS_': 'ra',
                                            'DE_ICRS_': 'dec',
                                            'VTmag': 'mag'})

        plan = Plan(asp_plan)
        # create assessor
        assessor = Assessor(observer, plan, None, candidates=candidates, weather=weather, obs_start=obs_start,
                            obs_end=obs_end)

        result = assessor.run()

        # 判断 result['score']['airmass'] 是否大于0
        assert (result['score']['airmass'] > 0).all()


if __name__ == '__main__':
    unittest.main()
