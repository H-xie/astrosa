import numpy
import matplotlib.pyplot as plt
import astropy.units as u


def T(current_pos,
      target_pos,
      current_velocity,
      max_velocity=6 * u.deg / u.second,
      max_acceleration=1 * u.deg / u.second ** 2):
    """

    Parameters
    ----------
    current_pos :
    target_pos :
    current_velocity :
    max_velocity :
    max_acceleration :

    Returns
    -------

    """

    delta_pos = target_pos - current_pos
    triangle_distance = max_velocity ** 2 / max_acceleration / 2
    if current_velocity.value == 0 and abs(delta_pos.value) >= triangle_distance.value:
        return sene_1(current_pos,
                      target_pos,
                      current_velocity)


def sene_1(current_pos,
           target_pos,
           current_velocity,
           max_velocity=6 * u.deg / u.second,
           max_acceleration=1 * u.deg / u.second ** 2):
    """
    trapezoid velocity curve, calculate with direction

    Parameters
    ----------
    current_pos :
    target_pos :
    current_velocity :
    max_velocity :
    max_acceleration :

    Returns
    -------

    """
    delta_pos = target_pos - current_pos
    direction = numpy.sign(delta_pos.value)
    max_velocity = max_velocity * direction
    max_acceleration = max_acceleration * direction

    # acceleration phase
    t1 = max_velocity / max_acceleration
    s1 = max_acceleration * t1 ** 2 / 2

    # deceleration phase
    t3 = -max_velocity / -max_acceleration
    s3 = (max_velocity) * t3 + (-max_acceleration) * t3 ** 2 / 2

    # constant velocity phase
    s2 = delta_pos - s1 - s3
    t2 = s2 / max_velocity
    assert t2 >= 0

    # total time
    t = t1 + t2 + t3
    assert t >= 0

    # plot velocity curve
    tx = numpy.linspace(0, t.value, 100) * t1.unit
    vx = numpy.zeros(tx.shape) * max_velocity.unit
    vx[tx <= t1] = max_acceleration * tx[tx <= t1]
    vx[tx > t1] = max_velocity
    vx[tx > t1 + t2] = max_velocity - max_acceleration * (
            tx[tx > t1 + t2] - t1 - t2)

    #     plot
    plt.figure()
    plt.plot(tx, vx)

    # plot position curve
    sx = numpy.zeros(tx.shape) * u.deg
    sx[tx <= t1] = max_acceleration * tx[tx <= t1] ** 2 / 2
    sx[tx > t1] = max_velocity * (tx[tx > t1] - t1) + max_acceleration * (
            tx[tx > t1] - t1) ** 2 / 2 + max_acceleration * t1 ** 2 / 2
    sx[tx > t1 + t2] = max_velocity * (
            tx[tx > t1 + t2] - t1) - max_acceleration * (
                               tx[tx > t1 + t2] - t1 - t2) ** 2 / 2 + max_velocity * (
                               t2 - t1) + max_acceleration * (
                               t2 - t1) ** 2 / 2 + max_acceleration * t1 ** 2 / 2 + max_acceleration * t1 ** 2 / 2

    # plt.figure()
    plt.plot(tx, sx)
    plt.show()
