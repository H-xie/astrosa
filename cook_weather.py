import pandas as pd
import numpy as np
import healpy as hp
from astropy.time import Time
import astropy.units as u

# create a zone
nside = 4 ** 2

npix = hp.nside2npix(nside)

print(npix)

# set random cloud
# cloud is (0,1) means the thickness

ntime_tic = 1000 # every minute

cloud = np.random.random([ ntime_tic,npix])
print(cloud.shape)

# create data frame

start_time = Time("2023-01-01 19:00:00")
datetime_list = [start_time + i*u.minute for i in range(ntime_tic)]


df_cloud = pd.DataFrame(cloud,index=datetime_list, columns=range(npix))
df_cloud.to_json("assess/tests/data/cloud.json")

