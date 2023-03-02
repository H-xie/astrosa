# -*- coding: UTF-8 -*-
"""
@File    ：utils.py
@Author  ：heaven
@Date    ：2023/3/1 20:16 
"""
import pandas as pd
from astropy.coordinates import SkyCoord
import astropy.units as u
from astropy.time import Time

from assess import FixedTarget
from astroplan.observer import Observer

def df2Targets(df: pd.DataFrame):
    coord = SkyCoord(ra=df['_RAJ2000'] * u.deg,
                     dec=df['_DEJ2000'] * u.deg)

    star = FixedTarget(coord=coord, name=df['tyc2-id'])

    return star

observer = Observer.at_site('BAO')
observing_date = Time('2023-01-01')