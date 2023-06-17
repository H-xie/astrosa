import astropy.io.fits as fits
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np
import astropy.units as u


# Point
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y


# create MASK
class Mask:
    def __init__(self):
        datashape = [2080, 2080]
        self.data = np.full(datashape, 0, dtype=np.uint16)
        # self.data = np.expand_dims(self.data, axis=2)

        self.center = Point(1053, 1017)
        self.radius = int(983 / 90 * 70)
        self.full_radius = 983
        self.biasNorth = 155.6 * u.deg  # degree clockwise from right

        self.createMask(self.data, self.center, self.radius)

    def createMask(self, data, center: Point, radius):
        cv.circle(data, (center.x, center.y), radius, 1, -1)


def segment_cloud_OTSU(cloud_file: str):
    # load cloud data
    cloud_fits = fits.open(cloud_file)
    cloud = cloud_fits[0].data
    cloud = (cloud - cloud.min()).astype(np.uint16)
    cloud = cloud.transpose(1, 2, 0)
    gray_cloud = cv.cvtColor(cloud, cv.COLOR_RGB2GRAY)

    cloud_mask = Mask(gray_cloud)

    masked_cloud = cloud * cloud_mask.data
    image_to_plot = masked_cloud / cloud.max()
    plt.imshow(image_to_plot, origin='lower')
    plt.show()

    # get cloud's saturation
    cloud_8bit = masked_cloud / cloud.max() * 255
    cloud_8bit = cloud_8bit.astype(np.uint8)
    cloud_saturation = cv.cvtColor(cloud_8bit, cv.COLOR_RGB2HSV)[:, :, 1]

    plt.imshow(cloud_saturation, origin='lower', cmap='Blues_r')
    plt.show()

    # get histogram of saturation
    hist_saturation = np.histogram(cloud_saturation, bins=256, range=(0, 255))[0]
    hist_saturation[0] = 0

    # 总像素数量
    total_pixels = np.sum(hist_saturation)

    # 初始化类间方差最大值和最佳阈值
    max_variance = 0
    threshold = 0

    # 对于每个可能的阈值进行计算
    for t in range(len(hist_saturation)):
        # 类别1：小于等于阈值 t
        class1_pixels = np.sum(hist_saturation[:t + 1])
        class1_weights = class1_pixels / total_pixels
        class1_mean = np.sum(np.arange(t + 1) * hist_saturation[:t + 1]) / class1_pixels

        # 类别2：大于阈值 t
        class2_pixels = np.sum(hist_saturation[t + 1:])
        class2_weights = class2_pixels / total_pixels
        class2_mean = np.sum(np.arange(t + 1, len(hist_saturation)) * hist_saturation[t + 1:]) / class2_pixels

        # 类间方差
        variance = class1_weights * class2_weights * (class1_mean - class2_mean) ** 2

        # 更新最大方差和阈值
        if variance > max_variance:
            max_variance = variance
            threshold = t

    print(f"threshold: {threshold}")
    seg_cloud = cloud_saturation > threshold
    plt.imshow(seg_cloud, origin='lower', cmap='gray')
    plt.show()

    seg_cloud = np.expand_dims(seg_cloud, axis=2)
    result = masked_cloud * seg_cloud.astype(np.int32)

    return result


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Convert cloud data to FITS format.')
    parser.add_argument('cloud', type=str, help='cloud name')
    # parser.add_argument('folder', type=str, help='cloud folder')
    args = parser.parse_args()

    # seg_cloud = segment_cloud_OTSU(args.cloud)
    # plt.imshow(seg_cloud / seg_cloud.max(), origin='lower')
    # plt.show()

    # iterate cloud folder
    import os

    from astropy.io import fits
    from photutils.detection import DAOStarFinder
    from astropy.stats import sigma_clipped_stats

    datafits = fits.open(args.cloud)[0]
    # 读取图像
    data = datafits.data[0]
    gain = datafits.header['GAIN_ELE']
    # data = data / 1e6

    mask = Mask(data).data
    t = mask == 0
    mask = t

    mean, median, std = sigma_clipped_stats(data, mask=mask, sigma=3.0)
    print((mean, median, std))

    # 创建DAOStarFinder对象
    daofind = DAOStarFinder(fwhm=3.0, threshold=5. * std)

    # 提取点源
    sources = daofind.find_stars(data - median, mask=mask)

    # 打印点源坐标和其他属性
    print(sources)

    import numpy as np
    import matplotlib.pyplot as plt
    from astropy.visualization import SqrtStretch
    from astropy.visualization.mpl_normalize import ImageNormalize
    from photutils.aperture import CircularAperture

    positions = np.transpose((sources['xcentroid'], sources['ycentroid']))
    apertures = CircularAperture(positions, r=4.0)
    norm = ImageNormalize(stretch=SqrtStretch())
    plt.imshow(data, cmap='Greys', origin='lower', norm=norm,
               interpolation='nearest')
    apertures.plot(color='blue', lw=1.5, alpha=0.5)
    plt.legend()

    plt.show()
