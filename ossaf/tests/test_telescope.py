from unittest import TestCase

import astropy.units as u
from astropy.coordinates import EarthLocation, SkyCoord, AltAz
from astropy.time import Time

from ossaf.assess.telescope import Telescope


class TestTelescope(TestCase):

    def __init__(self, *args, **kwargs):
        super(TestTelescope, self).__init__(*args, **kwargs)

        # TODO: add site.py
        location = EarthLocation(lat=43.832964 * u.deg, lon=126.343235 * u.deg, height=313 * u.m)
        obstime = Time("2023-05-01 00:00:00", format='iso', scale='utc')
        print(obstime)
        pointing = AltAz(alt=30 * u.deg, az=70 * u.deg)
        self.telescope = Telescope(location, 6, 1, 1.5 * u.deg, 10, pointing, obstime)

    def testSlew(self):
        print(self.telescope)
        obstime = Time("2023-05-01 00:00:00", format='iso', scale='utc')
        target = SkyCoord(alt=40 * u.deg, az=77 * u.deg, frame='altaz', obstime=obstime,
                          location=self.telescope.location)
        is_success = self.telescope.slew(target)
        print(is_success)

        obstime = Time("2023-05-01 00:10:00", format='iso', scale='utc')
        target = SkyCoord(alt=40 * u.deg, az=77 * u.deg, frame='altaz', obstime=obstime,
                          location=self.telescope.location)
        is_success = self.telescope.slew(target)
        print(is_success)

        target = AltAz(alt=50 * u.deg, az=180 * u.deg)
        slew_time = self.telescope.slew_time(target)
        print(f"from {self.telescope.current_pointing} to {target} : {slew_time} seconds")
