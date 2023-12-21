"""
ax.plot(theta, r) matplotlib 的函数
theta 是弧度, r 是直径
theta 是方向角 AZ, r 是高度角 ALT
"""
#  Licensed under the MIT license - see LICENSE.txt

import astropy.units as u
import astropy_healpix as ahp
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from astroplan import FixedTarget
from astropy.coordinates import SkyCoord
from astropy_healpix.healpy import ang2pix
from matplotlib import animation
from matplotlib.colors import ListedColormap

from utils import observer

values = [0, 1]
color_set = plt.cm.viridis(np.linspace(0, 0.5, len(values)))
cmap = ListedColormap(color_set)

matplotlib.rcParams['font.size'] = 12

def trace(data: pd.DataFrame, savename: str = 'trace'):
    fig = plt.figure()
    ax = fig.add_subplot(projection='polar')

    ax.set_theta_zero_location('N')

    theta = [None, None]
    r = [None, None]

    slew_alpha = 0.2
    # delt_alpha = (1 - slew_alpha) / len(data)
    for _, line in data.iterrows():
        # Plot slew
        if theta[0] is not None:
            theta[1] = np.deg2rad(line['start_az'])
            r[1] = 90 - line['start_alt']

            ax.plot(theta, r, color=cmap(values[0]), alpha=slew_alpha,
                    linestyle='--', linewidth=1)
            # slew_alpha += delt_alpha
            # print(theta, r)

        else:
            # print("---------------------------------")
            pass

        theta[0] = line['start_az']
        r[0] = line['start_alt']
        theta[1] = line['end_az']
        r[1] = line['end_alt']

        theta = np.deg2rad(theta)
        r = 90 - np.array(r)

        # print(theta, r, 'x')
        # plot exposure trace
        ax.plot(theta, r, color=cmap(values[1]))

        # annotate
        # ax.annotate(line['id'], (theta[1], r[1]), xytext=(theta[1], r[1] + 15), arrowprops={
        #     'arrowstyle': '->',
        #     'linewidth': 0.5,
        # }, fontsize=5)

        # move end to begin
        theta[0] = theta[1]
        r[0] = r[1]

    ax.set_rmax(90)
    degree_sign = u'\N{DEGREE SIGN}'
    r_labels = [
        '90' + degree_sign,
        '',
        '60' + degree_sign,
        '',
        '30' + degree_sign,
        '',
        '0' + degree_sign + ' Alt.',
    ]
    ax.set_rgrids(range(0, 91, 15), r_labels)

    # create legend
    ax.legend(['Exposure', 'Slew'], bbox_to_anchor=(1.2, 1.1), fontsize=12)

    fig.savefig(f'{savename}.svg')
    fig.savefig(f'{savename}.pdf')


def ani_trace(data: pd.DataFrame, savename: str = 'trace'):
    fig = plt.figure(dpi=800)
    ax = fig.add_subplot(projection='polar')

    ax.set_theta_zero_location('N')

    # time, az, alt
    start = data[['id', 'start_time', 'start_az', 'start_alt']].copy()
    start = start.rename(columns={'start_time': 'time',
                                  'start_az': 'az',
                                  'start_alt': 'alt'})
    end = data[['id', 'end_time', 'end_az', 'end_alt']].copy()
    end = end.rename(columns={'end_time': 'time',
                              'end_az': 'az',
                              'end_alt': 'alt'})

    full_data = pd.concat([start, end])
    full_data = full_data.sort_values(by='time')
    theta = full_data['az']
    r = full_data['alt']

    theta = theta.apply(np.deg2rad)
    r = 90 - r

    line2 = ax.plot(theta[0], r[0], color=cmap(values[0]), alpha=1)[0]
    ax.set_rmax(90)
    degree_sign = u'\N{DEGREE SIGN}'
    r_labels = [
        '90' + degree_sign,
        '',
        '60' + degree_sign,
        '',
        '30' + degree_sign,
        '',
        '0' + degree_sign + ' Alt.',
    ]
    ax.set_rgrids(range(1, 106, 15), r_labels)

    def update(frame):
        # update the line plot:
        line2.set_xdata(theta[:frame])
        line2.set_ydata(r[:frame])
        return line2

    def advaced_update(frame):
        """ 每一帧绘制多段曲线，即不是 `set_data` 而是多次plot？
        """
        # TODO 动图绘制多色线条（多线段）
        pass

    ani = animation.FuncAnimation(fig=fig, func=update, frames=len(theta), interval=100, repeat=False)

    writer = animation.PillowWriter(fps=15)
    ani.save(f'{savename}.gif', writer=writer)
    return full_data


def to_altaz(dataline):
    coord = SkyCoord(ra=dataline['ra'] * u.deg, dec=dataline['dec'] * u.deg)
    target = FixedTarget(coord)
    altaz = observer.altaz(dataline['time'], target)
    return [altaz.alt.value, altaz.az.value]


def add_altaz(data: pd.DataFrame) -> pd.DataFrame:
    result = data

    for tag in ['start', 'end']:
        tmp_data = data.loc[:, (f'{tag}_time', 'ra', 'dec')]
        tmp_data = tmp_data.rename(columns={f'{tag}_time': 'time'})
        start_loc = tmp_data.apply(to_altaz, axis=1, result_type='expand')

        start_loc.columns = [f'{tag}_alt', f'{tag}_az']
        result = pd.concat([result, start_loc], axis=1)

    return result


def plot_cloud(data: pd.Series):
    """ 一个时间点是一行, 接口只处理 1 个时刻的数据

    """

    npix = len(data)
    nside = ahp.npix_to_nside(npix)
    xsize = npix
    ysize = xsize
    # print(f'nside {nside}, xsize {xsize}')

    theta = np.linspace(0, np.pi / 2, ysize)
    phi = np.linspace(-np.pi, np.pi, xsize)
    PHI, THETA = np.meshgrid(phi, theta)

    grid_pix = ang2pix(nside, THETA, PHI)
    grid_map = data.to_numpy()[grid_pix]

    longitude = np.radians(np.linspace(-180, 180, xsize))
    latitude = np.linspace(0, 90, ysize)

    # 创建新的图
    fig = plt.figure()
    ax = fig.add_subplot(projection='polar')
    plt.sca(ax)

    ret = plt.contourf(longitude,
                       latitude,
                       grid_map,
                       vmin=0,
                       vmax=1,
                       levels=50,
                       cmap='Blues_r')

    cb = fig.colorbar(ret, pad=0.1, ticks=np.linspace(0, 1, 11), extend='neither')

    # 用和轨迹图一样的配置
    ax.set_theta_zero_location('N')
    ax.set_rmax(90)
    degree_sign = u'\N{DEGREE SIGN}'
    r_labels = [
        '90' + degree_sign,
        '',
        '60' + degree_sign,
        '',
        '30' + degree_sign,
        '',
        '0' + degree_sign + ' Alt.',
    ]
    ax.set_rgrids(range(0, 91, 15), r_labels)


if __name__ == '__main__':
    ani_trace(None)
