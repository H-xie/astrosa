# -*- coding: utf-8 -*-
# @Time    : 2023-02-01 001 21:59
# @Author  : H-XIE

from astroplan import FixedTarget
from astropy.time import Time

import astropy.units as u
class Shot(object):

    def __init__(self, target: FixedTarget, start_time: Time, end_time=Time):
        self.__target = target
        self.time = [start_time, end_time]

    @property
    def target(self):
        return self.target

    @property
    def start_time(self):
        return self.time[0]

    @property
    def end_time(self):
        return self.time[1]


class Plan(object):
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
