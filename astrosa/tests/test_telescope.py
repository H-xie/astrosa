import pytest
from astropy.coordinates import EarthLocation, AltAz
from astropy.time import Time

from astrosa.assess import *
import astropy.units as u

from astrosa.assess.telescope import Telescope

observe_time = Time('2023-06-08')
location = EarthLocation(lat=43.82416667 * u.deg,
                         lon=126.331111 * u.deg,
                         height=313 * u.m)
initial_pointing = AltAz(alt=0 * u.deg,
                         az=0 * u.deg,
                         obstime=observe_time,
                         location=location)


# 创建转台
@pytest.fixture
def mount():
    return Mount([0.1 * u.deg / u.second, 0.1 * u.deg / u.second],
                 [0.1 * u.deg / u.second ** 2, 0.1 * u.deg / u.second ** 2],
                 initial_pointing)


def test_mount(mount):
    target = AltAz(alt=8 * u.deg,
                   az=200 * u.deg,
                   obstime=observe_time + 3000 * u.second,
                   location=location)
    result, obstime = mount.slew(target)
    print(f'result: {result}, obstime: {obstime}')


@pytest.fixture
def terminal():
    configure_time = {"filter_none": {"filter_U": 5 * u.second,
                                      "filter_B": 10 * u.second,
                                      "filter_V": 15 * u.second
                                      },
                      "filter_U": {"filter_B": 5 * u.second,
                                   "filter_V": 10 * u.second},
                      "filter_B": {"filter_V": 5 * u.second},
                      "camera1": {"camera2": 7 * u.second},
                      }
    return Terminal("filter_none", "camera1", configure_time)


def test_terminal(terminal):
    print(terminal.configure_time)
    print(terminal.set_to("filter_U", "camera1"))

    print(terminal.set_to("filter_none", "camera2"))

    print(terminal.set_to("camera1", "camera2"))
    print(terminal.set_to("filter_none", "camera2"))
    print(terminal.set_to("filter_V", "camera2"))
    print(terminal.set_to("c", "camera2"))


@pytest.fixture
def telescope1(mount, terminal):
    return Telescope(mount=mount, terminal=terminal)


def test_telescope(telescope1):

    print(telescope1)
