""" 度量
各类量化指标是一种度量，

类似 astroplan 的 constrains.py

"""
#  Licensed under the MIT license - see LICENSE.txt

import abc

from .const import MAX_PRIORITY


class Metric(abc.ABC):
    """
    虚基类
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass


class Overhead(Metric):

    def __init__(self):
        pass


class DataQuality(Metric):

    def __init__(self):
        pass

    @classmethod
    def from_cloud(cls, cloud):
        return cloud

    @classmethod
    def from_airmass(cls, secz):
        return secz


class ScientifcValue(Metric):

    def __init__(self):
        pass

    @classmethod
    def from_priority(cls, priority):
        return MAX_PRIORITY - priority
