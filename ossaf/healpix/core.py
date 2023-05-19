from astropy_healpix import HEALPix


class HH:
    @classmethod
    def ang2pix(cls, nside, order='ring', lon=None, lat=None):
        hp = HEALPix(nside, order)
        return hp.lonlat_to_healpix(lon, lat)

    @classmethod
    def pix2ang(cls, nside, order='ring', pix=None):
        hp = HEALPix(nside, order)
        return hp.healpix_to_lonlat(pix)

    @classmethod
    def nside2npix(cls, nside, order='ring'):
        hp = HEALPix(nside, order)
        return hp.npix
