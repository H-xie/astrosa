# -*- coding: UTF-8 -*-
"""
@File    ：utils.py
@Author  ：heaven
@Date    ：2023/3/1 20:16 
"""
import pandas as pd
from astropy.coordinates import SkyCoord
import astropy.units as u

from assess import FixedTarget


def df2Targets(df: pd.DataFrame):
    coord = SkyCoord(ra=df['_RAJ2000'] * u.deg,
                     dec=df['_DEJ2000'] * u.deg)

    star = FixedTarget(coord=coord, name=df['tyc2-id'])

    return star