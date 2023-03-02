import astropy.units as u
import numpy as np
import pandas as pd
# import healpy as hp
from astropy.time import Time

from healpix import HH
from utils import *

# create a zone
nside = 4 ** 2

npix = HH.nside2npix(nside)

print(npix)

# set random cloud
# cloud is (0,1) means the thickness
start_time = observer.twilight_evening_astronomical(observing_date, 'next').to_value('datetime64', subfmt='date_hm')
end_time = observer.twilight_morning_astronomical(observing_date, 'next').to_value('datetime64', subfmt='date_hm')

start_time -= np.timedelta64(1,'m')
end_time += np.timedelta64(1,'m')

print(f'generate cloud data from {start_time} to {end_time}')

datetime_list =[]
iTime = start_time
while iTime < end_time:
    datetime_list.append(iTime)
    iTime += 1*np.timedelta64(1, 'm')

cloud = np.random.random([len(datetime_list), npix])

df_cloud = pd.DataFrame(cloud, index=datetime_list, columns=range(npix))
df_cloud.to_json("assess/tests/data/cloud.json", date_format='iso', orient='index')
