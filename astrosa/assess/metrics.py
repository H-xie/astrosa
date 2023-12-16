""" 度量
各类量化指标是一种度量，

类似 astroplan 的 constrains.py

"""
#  Licensed under the MIT license - see LICENSE.txt

import abc

import astropy.units as u
import numpy as np
from astroplan import Observer

from utils import obs_end, obs_start
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

    @classmethod
    def effectiveness(cls, exposure_time, observation_time):
        return exposure_time / observation_time
    @classmethod
    def overhead(cls, exposure_time, observation_time):
        return 1 - cls.effectiveness(exposure_time, observation_time)


class DataQuality(Metric):

    def __init__(self):
        pass

    @classmethod
    def from_cloud(cls, cloud):
        return cloud

    @classmethod
    def from_airmass(cls, secz):
        return secz

    @classmethod
    def from_seeing(cls, seeing):
        return seeing

    @classmethod
    def from_skybrightness(cls, skybrightness):
        return skybrightness

    @classmethod
    def score(cls, cloud, airmass, seeing=None, skybrightness=None):
        """

        Parameters
        ----------
        cloud : 单位：无量纲 English: dimensionless
        airmass : 单位：无量纲 English: dimensionless
        seeing : 单位：角秒 English: arcsec
        skybrightness : 单位：mag/arcsec^2 English: mag/arcsec^2

        Returns
        -------

        """
        result = cloud
        result += 1 / 3 * (airmass - 1)

        if seeing is not None:
            result += seeing

        if skybrightness is not None:
            result += 1 / skybrightness

        return result


class ScientifcValue(Metric):

    def __init__(self):
        pass

    @classmethod
    def from_priority(cls, priority):
        return MAX_PRIORITY - priority


class RatioToBestAirmass(Metric):

    def __init__(self):
        pass

    @classmethod
    def from_target(cls, observer: Observer, current_time, target):
        """
        实际观测的大气质量与最佳观测大气质量的相对偏差
        Engllish: The relative deviation of the actual observation airmass from the best observation airmass

        如果目标高度角小于等于0，那么大气质量为无穷大
        English: If the target altitude is less than or equal to 0, the airmass is np.inf

        Parameters
        ----------
        observer :
        current_time :
        target :

        Returns
        -------

        """
        meridian_time = observer.target_meridian_transit_time(current_time, target)

        if not observer.is_night(meridian_time):
            if current_time < meridian_time:
                best_time = obs_end
            else:
                best_time = obs_start
        else:
            best_time = meridian_time

        # get alt of target at meridian
        meridian_airmass = observer.altaz(best_time, target).secz


        if hasattr(target, 'secz'):
            target_airmass = target.secz
        else:

            alt = observer.altaz(current_time, target).alt
            if alt <= 0 * u.deg:
                target_airmass = np.inf
            else:
                target_airmass = observer.altaz(current_time, target).secz

        result = target_airmass - meridian_airmass
        result = result / meridian_airmass

        return result


class ScheduledRate(Metric):

    def __init__(self):
        pass

    @classmethod
    def in_request(cls, plan, candidates):
        return len(plan.data) / len(candidates)

    @classmethod
    def in_time(cls, exposure_time, candidates):
        return exposure_time.total_seconds() / (candidates.exposure_minutes.sum() * 60)
