from .core import *


""" 度量
各类量化指标是一种度量，

"""
class Metric(object):
    """
    虚基类
    """

    __metaclass__ = ABCMeta

    def __init__(self):
        pass

class Overhead(Metric):

    def __init__(self):
        pass


class DataQuality(Metric):

    def __init__(self):
        pass

class ScientifcValue(Metric):

    def __init__(self):
        pass

