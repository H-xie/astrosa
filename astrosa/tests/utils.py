import astropy.units as u
from astroplan import Observer
from astropy.coordinates import EarthLocation
from astropy.time import Time

location = EarthLocation(lat=43.82416667 * u.deg, lon=126.331111 * u.deg, height=313 * u.m)
observer = Observer(location)
observing_date = Time('2023-06-08')

obs_start = observer.twilight_evening_astronomical(time=observing_date, which='next')
obs_end = observer.twilight_morning_astronomical(time=obs_start, which='next')
