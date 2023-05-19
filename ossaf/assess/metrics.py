""" 度量
各类量化指标是一种度量，

类似 astroplan 的 constrains.py

"""
import abc


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
        return 1 - cloud


class ScientifcValue(Metric):

    def __init__(self):
        pass
