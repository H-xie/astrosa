#  Licensed under the MIT license - see LICENSE.txt

from abc import ABC, ABCMeta
from logging import warning

import pandas as pd
from astroplan import FixedTarget as aspFixedTarget
from astroplan import Target as aspTarget, Scheduler
from astropy.coordinates import SkyCoord, AltAz
from astropy.time import Time

from .const import NSIDE
from .metrics import *
from .telescope import Telescope
from .weather import Weather
from ..healpix import HH


class Target(aspTarget, ABC):
    """
    Abstract base class for target objects.
    因为 `astroplan` 提供的Target没有比较功能，所以我需要给他添加个
    `__eq__` 方法
    """
    __metaclass__ = ABCMeta

    def __eq__(self, other):
        if self.ra == other.ra and self.dec == other.dec:
            return True


class FixedTarget(Target, aspFixedTarget):
    pass


class Plan:
    """
    计算得到的观测序列
    可以是一晚的，也可以是连续多晚的，也可以是不连续的多个晚上。

    序列必须是头尾相接，有序的序列，观测时间不可重叠。

    if multiple night, use a chain table `self.table`
    else use `self.data`
    """

    def __init__(self, data: pd.DataFrame):

        # check data format
        DATA_COLUMNS = ['id', 'ra', 'dec', 'start_time', 'end_time', 'priority']
        for c in DATA_COLUMNS:
            if c in data.columns:
                pass
            else:
                raise ValueError(c, ' is not exist in data: pd.DataFrame.',
                                 data.columns)

        # save to member
        self.data = data


class Assessor:
    """ 评估器
            用的时候就是它了，创建一个就好。配置上：
            1. weather 记录
            2. day 观测日
            3. scheduler.py 调度器（动态）
            4. plan 观测计划序列（静态）

            """

    def __init__(self,
                 observer,
                 plan: Plan = None,
                 scheduler: Scheduler = None,
                 candidates: pd.DataFrame = None,
                 weather: Weather = None,
                 telescope: Telescope = None,
                 **kwargs):
        assert (plan is not None) or (scheduler is not None), \
            f"plan is for static observation, scheduler is for dynamic observation. Either should provide"

        if scheduler is not None and weather is None:
            warning('No weather is set, scheduler will run as free')

        self.observer = observer
        self.plan = plan
        self.scheduler = scheduler
        self.candidates = candidates
        self.weather = weather
        self.telescope = telescope

        # result metric 是一个字典，key 是度量的名称，value 是度量的值
        self.result = None

        self.obs_start = kwargs['obs_start']
        self.obs_end = kwargs['obs_end']

    def run_static_list(self):
        print("static list runner")

        result = {'total': pd.Series(dtype=float),
                  'score': pd.DataFrame(data=self.plan.data, copy=True)}

        # total used time
        def _used_time():
            t = self.plan.data['end_time'] - self.plan.data['start_time']
            return t.sum()

        whole_score = list()
        t_used = _used_time()
        total_time = (self.obs_end - self.obs_start).to_datetime()
        result['total']['overhead'] = Overhead.overhead(t_used, total_time)

        # priority score
        result['total']['scientific_score'] = 0
        # plan is ordered by time
        for iPlan, shot in self.plan.data.iterrows():
            coord = SkyCoord(ra=shot['ra'] * u.deg, dec=shot['dec'] * u.deg)
            target = FixedTarget(coord, name=shot['id'])

            # only count cloud at the beginning and the end
            obstime = Time([shot['start_time'], shot['end_time']])
            altaz_frame = AltAz(obstime=obstime, location=self.observer.location)

            # 赤道坐标系👉地平坐标系👉healpix 编码
            altaz_target = target.coord.transform_to(altaz_frame)
            hindex = HH.ang2pix(nside=NSIDE, lon=altaz_target.az, lat=altaz_target.alt)

            # 天气如何? 得分如何?
            len_score = 2
            score_cloud = [0] * len_score
            score_airmass = [0] * len_score
            # TODO: calculate by time resolution
            for i in range(len_score):
                # find the closest time of row
                obstime_stamp = obstime[i].to_value('datetime64')
                closest_time = self.weather.cloud.data.index.asof(obstime_stamp)

                cc = self.weather.cloud[closest_time, hindex[i]]

                score_cloud[i] = DataQuality.from_cloud(cc)

                # airmass
                score_airmass[i] = DataQuality.from_airmass(altaz_target[i].secz)

            whole_score.append(score_cloud)
            result['score'].loc[iPlan, 'cloud'] = np.mean(score_cloud)
            result['score'].loc[iPlan, 'airmass'] = np.mean(score_airmass)
            result['score'].loc[iPlan, 'scientific_score'] = ScientifcValue.from_priority(shot.priority)
            result['score'].loc[iPlan, 'ratio_to_best_airmass'] = RatioToBestAirmass.from_target(self.observer,
                                                                                                 obstime_stamp,
                                                                                                 target)

        result['score']['expected_quality'] = DataQuality.score(result['score']['cloud'],
                                                                result['score']['airmass'])

        # Total score
        result['total']['cloud'] = result['score']['cloud'].mean()
        result['total']['airmass'] = result['score']['airmass'].mean()
        result['total']['expected_quality'] = DataQuality.score(result['total']['cloud'],
                                                                result['total']['airmass'])
        result['total']['scheduled_rate_in_request'] = ScheduledRate.in_request(self.plan, self.candidates)
        if hasattr(self.candidates, 'exposure_minutes'):
            result['total']['scheduled_rate_in_time'] = ScheduledRate.in_time(t_used, self.candidates)
        result['total']['scientific_score'] += result['score']['scientific_score'].sum()
        result['total']['ratio_to_best_airmass'] = result['score']['ratio_to_best_airmass'].mean()

        return result

    def run_list_with_scheduler(self):
        """
        result is in `self.result`
        :return:
        """
        pass

    def run(self):

        # get static list if not None
        if self.plan is not None:
            pre_list = self.plan.data

        if self.scheduler is None:
            self.result = self.run_static_list()
        else:
            self.result = self.run_list_with_scheduler()

        return self.result
