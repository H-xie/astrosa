from astropy.io import fits
import pandas as pd

tyc2 = fits.open("assess/tests/data/tyc2.fit")

tyc2_rows = tyc2[1]._nrows

tyc2_dict = {}

for i in range(tyc2_rows):
    data = tyc2[1].data[i]
    # ID
    tycid = data[3:6]
    tycid_str = f"TYC {tycid[0]}-{tycid[1]}-{tycid[2]}"

    # ra J2000
    ra = data['_RAJ2000']

    # dec J2000
    dec = data['_DEJ2000']

    # 视星等 V
    VTmag = data['VTmag']

    record = [ra, dec, VTmag]
    tyc2_dict[tycid_str] = record

    # print(tycid_str, record)

df = pd.DataFrame.from_dict(tyc2_dict, orient='index', columns=['_RAJ2000', '_DEJ2000', 'VTmag'])
df.to_json('assess/tests/data/tyc2.json')
