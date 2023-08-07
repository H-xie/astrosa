#  Licensed under the MIT license - see LICENSE.txt

import astropy.coordinates as coord
import astropy.time as atime
import astropy.units as u
from astropy.coordinates import AltAz


class Telescope:
    def __init__(self, location, v_max, a_max, field_of_view: u.deg, max_magnitude, current_pointing,
                 current_time=None):
        """
        :param v_max: maximum velocity of telescope unit: degree/sec
        :param a_max: maximum acceleration of telescope unit: degree/sec^2
        :param field_of_view: field of view in degree
        :param max_magnitude: maximum magnitude of telescope (the larger the number, the fainter the object)
        :param current_pointing: current pointing of telescope
        :param current_time: current time

        """
        self.v_max = v_max
        self.a_max = a_max
        self.field_of_view = field_of_view
        self.max_magnitude = max_magnitude

        self.current_pointing = current_pointing
        self.current_time = current_time

        self.location = location

    def slew(self, target_pointing: coord.SkyCoord) -> [atime.Time, atime.TimeDelta]:
        if self.current_time is None:
            raise ValueError("current_time is None. Set current time first.")

        if self.current_pointing is None:
            self.current_pointing = target_pointing
            return True

        else:
            obstime = None
            if isinstance(target_pointing, AltAz):
                altaz_target = target_pointing
            else:
                frame = AltAz(obstime=self.current_time, location=self.location)
                altaz_target = target_pointing.transform_to(frame)
                obstime = target_pointing.obstime

            slew_time = self.slew_time(altaz_target)

            if obstime is None:
                self.current_time = self.current_time + slew_time
                self.current_pointing = target_pointing
                return True

            elif obstime > self.current_time + slew_time:
                self.current_time = obstime
                self.current_pointing = target_pointing
                return True
            else:
                return False

    def slew_time(self, target_pointing) -> atime.TimeDelta:

        if isinstance(target_pointing, AltAz):
            altaz_target = target_pointing
        else:
            frame = AltAz(obstime=self.current_time, location=self.location)
            altaz_target = target_pointing.transform_to(frame)

        altaz_current = self.current_pointing

        # unit: degree
        distance_alt = abs(altaz_current.alt - altaz_target.alt)
        distance_az = abs(altaz_current.az - altaz_target.az)

        # (1/2)*(v_max/a_max) + (s-1/2*a_max^2)/v_max + (1/2)*(v_max/a_max)
        # 加速 平稳 减速
        result = max(distance_az, distance_alt).value / self.v_max + self.v_max / self.a_max
        result = atime.TimeDelta(result, format='sec')

        return result
