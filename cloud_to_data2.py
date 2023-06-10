import datetime
import os
import sqlite3

import numpy as np
import pandas as pd
# 像素坐标系到地平坐标系的映射
from astropy import units as u
from astropy.coordinates import SkyCoord, AltAz, EarthLocation
from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from astropy.table import QTable
from astropy.time import Time
from photutils.detection import DAOStarFinder

from cloud_to_data import Mask
from astropy_healpix import HEALPix


def to_altaz(x, y, x_offset=1053, y_offset=1017, radius=983, north=155.6 * u.deg):
    # move to center
    x = x - 1053
    y = y - 1017

    # polar coordinates
    r = np.sqrt(x ** 2 + y ** 2)
    theta = np.arctan2(y, x)
    # print(f"theta: {theta}, r: {r}")

    # convert to altaz
    alt = r / radius * u.rad * np.pi / 2
    alt = np.pi / 2 * u.rad - alt
    az = (- theta) * u.rad - north
    # print(f"alt: {alt}, az: {az}")

    return AltAz(alt=alt, az=az)


# JLO 坐标
location = EarthLocation(lat=43.82416667 * u.deg, lon=126.331111 * u.deg, height=313 * u.m)

engine = sqlite3.connect('ossaf/data/tyc2.sqlite')

limit_magnitude = 8
tyc2 = pd.read_sql_query(f"SELECT * FROM tyc2 WHERE VTmag < {limit_magnitude} ", engine)


def find_tyc_star(star: SkyCoord, altaz):
    d_ra = tyc2.RA_ICRS_ - star.ra
    d_dec = tyc2.DE_ICRS_ - star.dec

    d = d_ra ** 2 + d_dec ** 2

    min_id = np.argmin(d)
    min_d = np.sqrt(d[min_id])

    # print(f"min_d: {min_d}, min_id: {min_id}")

    threshold = min_d_threshold(altaz)

    if min_d > threshold:
        return None, min_d
    else:
        return tyc2.iloc[min_id], min_d


mask = Mask()
mask_data = mask.data
t = mask_data == 0
mask_data = t


def min_d_threshold(star: AltAz, factor=20):
    """
    根据地平高度判断最小距离阈值
    """
    a = 2 * star.alt.to(u.rad).value / np.pi
    # print(a)
    b = (1 - a) * mask.full_radius
    # print(b)
    c = (1 / b)
    # print(c)
    c *= factor
    result = c * 360 / 2 / np.pi
    return result


def to_data(sources, time):
    def save_all_zero():
        nside = 4
        hp = HEALPix(nside=nside, order='ring')
        result = pd.DataFrame(columns=['H_ID', 'clear'])
        for i in range(hp.npix):
            result = pd.concat(
                [result, pd.DataFrame([[i, 0]], columns=['H_ID', 'clear'])])

        result.set_index('H_ID', inplace=True)
        result = result.T
        result.index = [time.to_datetime()]
        result.to_sql('clear', engine, if_exists='append')

    if sources is None:
        save_all_zero()
        return

    frame = AltAz(obstime=time, location=location)

    df_source = sources.to_pandas()
    altaz_sources = to_altaz(df_source.xcentroid.to_numpy(), df_source.ycentroid.to_numpy())
    star = SkyCoord(alt=altaz_sources.alt, az=altaz_sources.az, frame=frame)
    icrs_sources = star.transform_to('icrs')

    valid_sources = pd.DataFrame()
    num_valid_sources = 0
    for i in range(len(icrs_sources)):
        tyc, r = find_tyc_star(icrs_sources[i], star[i])
        # print(tyc, r)
        if tyc is not None:
            num_valid_sources += 1
            valid_sources = pd.concat([valid_sources, tyc], axis=1)
    valid_sources = valid_sources.T

    # if no valide sources save all cloud
    if num_valid_sources == 0:
        save_all_zero()
        return

    valid_icrs = SkyCoord(ra=valid_sources.RA_ICRS_ * u.deg, dec=valid_sources.DE_ICRS_ * u.deg, frame='icrs')
    valid_altaz = valid_icrs.transform_to(frame)

    # healpix 存储
    sky_zone_healpix = pd.DataFrame(columns=['H_ID', 'valid', 'total'])

    nside = 4
    hp = HEALPix(nside=nside, order='ring')
    for i in range(hp.npix):
        sky_zone_healpix = pd.concat(
            [sky_zone_healpix, pd.DataFrame([[i, 0, 0, 0]], columns=['H_ID', 'valid', 'total', 'mag_score'])])

    # 遍历可见星，填充表格
    h_id = hp.lonlat_to_healpix(lon=valid_altaz.az, lat=valid_altaz.alt)
    for index in h_id:
        # healpix
        sky_zone_healpix.loc[sky_zone_healpix.H_ID == index, 'valid'] += 1

    # 天区总星数
    tyc2_total = SkyCoord(ra=tyc2.RA_ICRS_ * u.deg, dec=tyc2.DE_ICRS_ * u.deg, frame='icrs')
    tyc2_total_altaz = tyc2_total.transform_to(frame)
    tycho2_heapix = hp.lonlat_to_healpix(lon=tyc2_total_altaz.az, lat=tyc2_total_altaz.alt)
    for i in range(len(tyc2_total_altaz)):
        mag = tyc2.VTmag[i]
        tstar = tyc2_total_altaz[i]
        # healpix
        h_id = tycho2_heapix[i]
        sky_zone_healpix.loc[sky_zone_healpix.H_ID == h_id, 'total'] += 1
        sky_zone_healpix.loc[sky_zone_healpix.H_ID == h_id, 'mag_score'] += limit_magnitude - mag

    sky_zone_healpix.mag_score = sky_zone_healpix.mag_score / 9

    # sky_zone_healpix['cloudy'] = 1 - (sky_zone_healpix.valid / sky_zone_healpix.total) / 0.15
    sky_zone_healpix['clear'] = (sky_zone_healpix.valid / sky_zone_healpix.mag_score) / 0.4
    sky_zone_healpix.loc[sky_zone_healpix.valid > 0, 'clear'] += 0.5
    sky_zone_healpix.loc[sky_zone_healpix['clear'] > 1, 'clear'] = 1

    sky_zone_healpix['cloud'] = 1 - sky_zone_healpix['clear']
    sky_zone_healpix.to_sql('cloud', engine, if_exists='replace')

    # TODO 按时间保存云量数据。
    result = pd.DataFrame(sky_zone_healpix.loc[:, ['H_ID', 'clear']])
    result.set_index('H_ID', inplace=True)
    result = result.T
    result.index = [time.to_datetime()]
    result.to_sql('clear', engine, if_exists='append')


# 遍历所有文件
folder = 'D:\\吉林云量\\2023-06-08\\'
for filename in os.listdir(folder):
    if not filename.endswith('bz2'):
        continue

    print(filename, datetime.datetime.now().isoformat())
    datafits = fits.open(folder + filename)[0]

    # 载入数据
    # 读取图像
    # datafits = fits.open("ossaf/data/2023_05_23__00_24_04.fits.bz2")[0]
    # 载入 RGB 三色 并转为亮度
    data = datafits.data[0] + datafits.data[1] + datafits.data[2]
    data = data.astype(np.float64)
    data /= 3
    data = data.astype(np.uint16)
    gain = datafits.header['GAIN_ELE']
    # data = data / 1e6

    time = datafits.header['DATE-OBS']
    time = Time(time, format='isot', scale='utc', location=location)
    time = time - 8 * u.hour

    mean, median, std = sigma_clipped_stats(data, mask=mask_data, sigma=3.0)
    # print((mean, median, std))

    # 创建DAOStarFinder对象
    daofind = DAOStarFinder(fwhm=4.0, threshold=5. * std)

    # 提取点源
    sources = daofind.find_stars(data - median, mask=mask_data)

    to_data(sources, time)

engine.close()
