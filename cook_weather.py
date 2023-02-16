import pandas as pd
import numpy as np
import healpy as hp

# create a zone
nside = 4 ** 2

npix = hp.nside2npix(nside)

print(npix)

# set random cloud
# cloud is (0,1) means the thickness

cloud = np.random.random(npix)
print(cloud)

# create data frame

data = {"healpix_idx": range(npix),
        "cloud": cloud}
df_cloud = pd.DataFrame(data)
df_cloud.to_json("assess/test/data/cloud.json")
