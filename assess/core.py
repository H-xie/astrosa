# -*- coding: utf-8 -*-
# @Time    : 2023-02-01 001 21:59
# @Author  : H-XIE
from logging import warn, warning

import astropy.units as u
from astroplan import FixedTarget as aspFixedTarget
from astroplan import Target as aspTarget
from astropy.time import Time

from abc import ABCMeta, ABC

from .weather import Weather
from .scheduler import Scheduler


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

    def __init__(self, nDays):
        self.nDays = nDays
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

        assert (self.nDays == 1) or (self.nDays > 1) and (len(self.table) == self.nDays)

    @property
    def slew(self):
        # TODO 计算指向耗时
        return 0 * u.second

    def is_valid(self):
        self.check()

        if self.nDays > 1:
            for p in self.table:
                p.isValid()
        else:
            end = None
            for shot in self.data:
                if (end is not None) and shot.start_time - end > self.slew:
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
                 day: Time,
                 observer,
                 plan: Plan = None,
                 scheduler: Scheduler = None,
                 weather: Weather = None):
        assert (plan is not None) or (scheduler is not None), \
            f"plan is for static observation, scheduler is for dynamic observation. Either should provide"

        if scheduler is not None and weather is None:
            warning('No weather is set, scheduler will run as free')

        self.day = day
        self.site = observer
        self.plan = plan
        self.scheduler = scheduler
        self.weather = weather

        # result metric 是一个字典，key 是度量的名称，value 是度量的值
        self.result = None

    def run_static_list(self):
        pass

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
