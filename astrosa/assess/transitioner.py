"""
继承自 astroplan 的 Transitioner 类，用于计算两个观测块之间的 slew time。
slew time 用astrosa的Telescope类的slew方法计算。

English:
Inherit from the Transitioner class of astroplan, used to calculate the slew time between two observing blocks.
The slew time is calculated using the slew method of the astrosa Telescope class.
"""
import astropy.units as u
from astroplan.constraints import _get_altaz
from astroplan.scheduling import Transitioner as ASPTransitioner, TransitionBlock
from astroplan.target import get_skycoord

from . import calculate_slew


class Transitioner(ASPTransitioner):
    """
    仅重写__call__方法，用astrosa的Telescope类的slew方法计算slew time。

    English:
    Only rewrite the __call__ method, and use the slew method of the astrosa Telescope class to calculate the slew time.
    """

    zero_velocity = 0 * u.deg / u.second

    def __init__(self, max_velocity, max_accelartion, slew_rate=None, instrument_reconfig_times=None):
        super().__init__(slew_rate,instrument_reconfig_times)
        self.max_velocity = max_velocity
        self.max_accelartion = max_accelartion

    def __call__(self, oldblock, newblock, start_time, observer):
        components = {}
        if (oldblock is not None) and (newblock is not None):
            targets = get_skycoord([oldblock.target, newblock.target])
            azz = _get_altaz(start_time, observer, targets)['altaz']
            t_az,_ = calculate_slew(azz[0].az, azz[1].az,
                                  self.zero_velocity,
                                  self.max_velocity[0],
                                  self.max_accelartion[0])
            t_alt,_ = calculate_slew(azz[0].alt, azz[1].alt,
                                   self.zero_velocity,
                                   self.max_velocity[0],
                                   self.max_accelartion[0])
            slew_time = max(t_az[-1], t_alt[-1])
            components['slew_time'] = slew_time

        if self.instrument_reconfig_times is not None:
            components.update(self.compute_instrument_transitions(oldblock, newblock))

        if components:
            return TransitionBlock(components, start_time)
        else:
            return None
