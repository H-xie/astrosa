# -*- coding: utf-8 -*-
# @Time    : 2023-02-01 001 21:59
# @Author  : H-XIE
from abc import ABCMeta, ABC
from logging import warning

import astropy.units as u
import numpy as np
from astropy.time import Time
from astropy.coordinates import AltAz

from astroplan import FixedTarget as aspFixedTarget
from astroplan import Target as aspTarget
from .scheduler import Scheduler
from .weather import Weather

from healpy import ang2pix
from .const import NSIDE

from astropy.coordinates import SkyCoord

from .metrics import *


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


class Shot:

    def __init__(self, target: FixedTarget, start_time: Time, end_time=Time):
        self.__target = target
        self.time = [start_time, end_time]

    @property
    def target(self):
        return self.__target

    @property
    def start_time(self):
        return self.time[0]

    @property
    def end_time(self):
        return self.time[1]


class Plan:
    """
    计算得到的观测序列
    可以是一晚的，也可以是连续多晚的，也可以是不连续的多个晚上。

    序列必须是头尾相接，有序的序列，观测时间不可重叠。

    if multiple night, use a chain table `self.table`
    else use `self.data`
    """

    def __init__(self):
        self.table = None
        self.__data = None

    @property
    def data(self):
        return self.__data

    @data.setter
    def data(self, val):
        self.__data = val

    def check(self):
        assert (self.table is not None) or (self.__data is not None)

    @property
    def slew_time(self):
        # TODO 计算指向耗时
        return 0 * u.second

    def is_valid(self):
        self.check()

        end = None
        for shot in self.data:
            if (end is not None) and shot.start_time - end > self.slew_time:
                end = shot.end_time

            elif end is None:
                end = shot.end_time
            else:
                print(f'{shot.start_time} is too early')
                return False

        return True


class Ossaf:
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
                 weather: Weather = None):
        assert (plan is not None) or (scheduler is not None), \
            f"plan is for static observation, scheduler is for dynamic observation. Either should provide"

        if scheduler is not None and weather is None:
            warning('No weather is set, scheduler will run as free')

        self.observer = observer
        self.plan = plan
        self.scheduler = scheduler
        self.weather = weather

        # result metric 是一个字典，key 是度量的名称，value 是度量的值
        self.result = None

    def run_static_list(self):
        print("static list runner")

        whole_score = list()
        # plan 是有序的
        for shot in self.plan.data:
            target = shot.target

            # 假设曝光时间很短, 望远镜的指向变化很小, 只计算开始和结束位置的云.
            obstime = Time([shot.start_time, shot.end_time])
            altaz_frame = AltAz(obstime=obstime, location=self.observer.location)

            # 赤道坐标系👉地平坐标系👉healpix 编码
            altaz_target = target.coord.transform_to(altaz_frame)
            theta = np.pi / 2 - np.deg2rad(altaz_target.alt).value  # 维度, 高度角
            phi = np.deg2rad(altaz_target.az).value  # 经度, 方向角
            hindex = ang2pix(nside=NSIDE, theta=theta, phi=phi)

            # 天气如何? 得分如何?
            cloud = list()
            score = list()
            for i in range(2):
                cc = self.weather.cloud[obstime[i].to_datetime(), hindex[i]]
                cloud.append(cc)

                score.append(DataQuality.from_cloud(cc))

            score = np.mean(score)
            print(cloud, f"score = {score}")


            whole_score.append(score)

        return whole_score

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
            self.run_static_list()
        else:
            self.run_list_with_scheduler()

        return self.result
