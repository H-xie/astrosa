# -*- coding: UTF-8 -*-
"""
@File    ：weather.py
@Author  ：heaven
@Date    ：2023/2/15 22:49

假设：
望远镜是地平式的，HEALPix 也用地平的球，天区云层覆盖情况，也是地平坐标系
HEALPix 的`nside`取决于望远镜的视场。我们假设，望远镜的视场是 a_telescope，nside2resol(nside) 应等于 a_telescope
"""
from abc import ABC

from astropy.time import Time
import pandas as pd


class Deprecate:
    class AbstractCloud(ABC):
        pass

    class Cloud(AbstractCloud):
        def __init__(self, data: pd.DataFrame):
            self.data = data

        def __getitem__(self, item):
            return self.data.at[item, "cloud"]

    class MuCloud(AbstractCloud):

        def __init__(self, data: pd.MultiIndex):
            self.data = data


class Cloud:
    """云的数据
    数据格式形如：
                                 0         1     ...      3070      3071
2023-01-01 19:00:00.000  0.737025  0.534117  ...  0.715236  0.804846
2023-01-01 19:01:00.000  0.345179  0.124946  ...  0.665552  0.686118
2023-01-01 19:02:00.000  0.563526  0.571504  ...  0.768975  0.459521
2023-01-01 19:03:00.000  0.218363  0.717141  ...  0.893263  0.624087
2023-01-01 19:04:00.000  0.439289  0.244890  ...  0.912568  0.178179
                           ...       ...  ...       ...       ...
2023-01-02 11:35:00.000  0.555391  0.742877  ...  0.851219  0.722592
2023-01-02 11:36:00.000  0.518966  0.734740  ...  0.274434  0.020305
    """

    def __init__(self, data):
        self._data = data

    @property
    def data(self):
        return self._data

    def __getitem__(self, item):
        return self._data.loc[item]


class Weather:
    """一个时刻的天气情况
    """

    def __init__(self, cloud: Cloud):
        """cloud is in index of healpix_idx
        """
        self._cloud = cloud

    @property
    def cloud(self):
        return self._cloud
