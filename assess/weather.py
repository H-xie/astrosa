# -*- coding: UTF-8 -*-
"""
@File    ：weather.py
@Author  ：heaven
@Date    ：2023/2/15 22:49

假设：
望远镜是地平式的，HEALPix 也用地平的球，天区云层覆盖情况，也是地平坐标系
HEALPix 的`nside`取决于望远镜的视场。我们假设，望远镜的视场是 a_telescope，nside2resol(nside) 应等于 a_telescope
"""
from astropy.time import Time
import pandas as pd


class Cloud:
    def __init__(self, data: pd.DataFrame):
        self.data = data

    def __getitem__(self, item):
        return self.data.at[item, "cloud"]


class Weather:
    """一个时刻的天气情况
    """

    def __init__(self, datetime: Time, cloud: pd.DataFrame):
        """cloud is in index of healpix_idx
        """
        self.datetime = datetime
        self._cloud = Cloud(cloud)

    @property
    def cloud(self):
        return self._cloud
