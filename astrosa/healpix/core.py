#  Licensed under the MIT license - see LICENSE.txt

from astropy_healpix import HEALPix as astroHP


class HH:
    @classmethod
    def ang2pix(cls, nside, order='ring', lon=None, lat=None):
        hp = astroHP(nside, order)
        return hp.lonlat_to_healpix(lon, lat)

    @classmethod
    def pix2ang(cls, nside, order='ring', pix=None):
        hp = astroHP(nside, order)
        return hp.healpix_to_lonlat(pix)

    @classmethod
    def nside2npix(cls, nside, order='ring'):
        hp = astroHP(nside, order)
        return hp.npix
