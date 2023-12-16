import astropy.units as u
import matplotlib.pyplot as plt
import numpy as np


def calculate_slew(current_pos,
                   target_pos,
                   current_velocity,
                   max_velocity=6 * u.deg / u.second,
                   max_acceleration=1 * u.deg / u.second ** 2):
    """
    trapezoid velocity curve, calculate with direction

    Parameters
    ----------
    current_pos : current position
    target_pos : target position
    current_velocity : current velocity
    max_velocity : max velocity
    max_acceleration : max acceleration

    Returns
    -------
    tp : time point of each phase
    a : acceleration of each phase

    """
    max_acceleration = abs(max_acceleration)
    max_velocity = abs(max_velocity)

    delta_pos = target_pos - current_pos
    if delta_pos.value == 0:
        return [0 * u.second], [0 * u.deg / u.second ** 2]
    triangle_distance = max_velocity ** 2 / max_acceleration
    if abs(delta_pos.value) >= abs(triangle_distance.value):
        return scene_1(current_pos,
                       target_pos,
                       current_velocity,
                       max_velocity,
                       max_acceleration)
    elif current_velocity.value == 0:
        return scene_2(current_pos,
                       target_pos,
                       current_velocity,
                       max_velocity,
                       max_acceleration)
    elif np.sign(delta_pos) == np.sign(current_velocity):
        return scene_3(current_pos,
                       target_pos,
                       current_velocity,
                       max_velocity,
                       max_acceleration)
    else:
        return scene_4(current_pos,
                       target_pos,
                       current_velocity,
                       max_velocity,
                       max_acceleration)


def scene_1(current_pos,
            target_pos,
            current_velocity,
            max_velocity=6 * u.deg / u.second,
            max_acceleration=1 * u.deg / u.second ** 2):
    """
    trapezoid velocity curve, calculate with direction
    current_velocity should be 0

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
    # assert current_velocity.value == 0, f'current_velocity={current_velocity}'

    delta_pos = target_pos - current_pos
    direction = np.sign(delta_pos.value)
    max_velocity = max_velocity * direction
    max_acceleration = max_acceleration * direction

    # acceleration phase
    t1 = (max_velocity - current_velocity) / max_acceleration
    s1 = current_velocity * t1 + max_acceleration * t1 ** 2 / 2

    # deceleration phase
    t3 = -max_velocity / -max_acceleration
    s3 = max_velocity * t3 + (-max_acceleration) * t3 ** 2 / 2

    # constant velocity phase
    s2 = delta_pos - s1 - s3
    t2 = s2 / max_velocity
    assert t2 >= 0

    # total time
    t = t1 + t2 + t3
    assert t >= 0

    tp = [t1, t1 + t2, t1 + t2 + t3]
    a = [max_acceleration, 0 * u.deg / u.second ** 2, -max_acceleration]

    return tp, a


def scene_2(current_pos,
            target_pos,
            current_velocity,
            max_velocity=6 * u.deg / u.second,
            max_acceleration=1 * u.deg / u.second ** 2):
    """
    trapezoid velocity curve, calculate with direction
    current_velocity should be 0

    the distance is too short, cannot reach max velocity
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
    assert current_velocity.value == 0

    delta_pos = target_pos - current_pos
    direction = np.sign(delta_pos.value)
    max_acceleration = max_acceleration * direction

    # a * t^2 = s
    t = 2 * np.sqrt(delta_pos / max_acceleration)
    assert t >= 0

    t1 = 1 / 2 * t
    t2 = t

    # return time point and acceleration
    tp = [t1, t2]
    a = [max_acceleration, -max_acceleration]

    return tp, a


def scene_3(current_pos,
            target_pos,
            current_velocity,
            max_velocity=6 * u.deg / u.second,
            max_acceleration=1 * u.deg / u.second ** 2):
    """
    trapezoid velocity curve, calculate with direction
    current_velocity is not zero

    displacement has same direction with current velocity

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
    direction = np.sign(delta_pos.value)
    distance = abs(delta_pos)
    max_velocity = max_velocity * direction
    max_acceleration = max_acceleration * direction
    assert np.sign(current_velocity) == direction

    # threshold of full acceleration down to zero
    # vt^2 - v0^2 = 2 * a * s
    threshold_s_min = (-current_velocity ** 2) / 2 / max_acceleration
    threshold_s_min = abs(threshold_s_min)

    # threshold of full acceleration down from max velocity
    # vt^2 - v0^2 = 2 * a * s
    threshold_s_max = (max_velocity ** 2) / 2 / max_acceleration
    threshold_s_max += (max_velocity ** 2 - current_velocity ** 2) / 2 / max_acceleration
    threshold_s_max = abs(threshold_s_max)

    if distance < threshold_s_min:
        # speed down to zero
        t1 = -current_velocity / -max_acceleration
        s1 = current_velocity * t1 + (-max_acceleration) * t1 ** 2 / 2

        pos = s1 + current_pos
        tp, a = scene_2(pos,
                        target_pos,
                        0 * u.deg / u.second,
                        max_velocity,
                        max_acceleration)

        tp = [t1 + it for it in tp]
        tp = [t1] + tp
        a = [-max_acceleration] + a

        return tp, a

    elif distance >= threshold_s_max:
        max_velocity = abs(max_velocity)
        max_acceleration = abs(max_acceleration)
        return scene_1(current_pos,
                       target_pos,
                       current_velocity,
                       max_velocity,
                       max_acceleration)

    else:
        # s_rest = delta_pos - threshold_s_min
        # t1 = s_rest/current_velocity
        # t2 = t1 + current_velocity / max_acceleration
        #
        # tp = [t1, t2]
        # a = [0 * u.deg / u.second ** 2, -max_acceleration]
        #
        # plot_curve(current_velocity, current_pos, tp, a, max_velocity)
        # return tp, a

        s_rest = delta_pos - threshold_s_min * direction
        v0 = current_velocity
        # a*t**2 + 2*v0*t = s_rest
        t1 = (-2 * v0 + np.sqrt(4 * v0 ** 2 + 4 * max_acceleration * s_rest)) / (2 * max_acceleration)
        if t1.value < 0:
            t1 = (-2 * v0 - np.sqrt(4 * v0 ** 2 + 4 * max_acceleration * s_rest)) / (2 * max_acceleration)
        t2 = t1 + t1
        t3 = t2 + -v0 / -max_acceleration
        tp = [t1, t2, t3]
        a = [max_acceleration, -max_acceleration, -max_acceleration]

        return tp, a


def scene_4(current_pos,
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
    direction = np.sign(delta_pos.value)
    max_velocity = max_velocity * direction
    max_acceleration = max_acceleration * direction

    # speed down to zero
    t1 = -current_velocity / max_acceleration
    v1 = current_velocity + max_acceleration * t1
    s1 = current_pos + current_velocity * t1 + max_acceleration * t1 ** 2 / 2

    tp, a = calculate_slew(s1,
                           target_pos,
                           v1,
                           max_velocity,
                           max_acceleration)

    tp = [t1 + it for it in tp]
    tp = [t1] + tp
    a = [max_acceleration] + a

    return tp, a


def plot_curve(v0, s0, tp, a, max_velocity):
    """
    plot velocity and position curve in one figure

    Parameters
    ----------
    v0 :
    s0 :
    tp :
    a :
    max_velocity :

    Returns
    -------

    """
    # plot curve
    tx = np.linspace(0, tp[-1].value, 100) * tp[-1].unit
    vx = np.zeros(tx.shape) * max_velocity.unit
    sx = np.zeros(tx.shape) * u.deg
    for i in range(len(tp)):
        if i == 0:
            vx[tx <= tp[i]] = v0 + a[i] * tx[tx <= tp[i]]
            sx[tx <= tp[i]] = s0 + v0 * tx[tx <= tp[i]] + a[i] * tx[tx <= tp[i]] ** 2 / 2

            s0 += v0 * tp[i] + a[i] * tp[i] ** 2 / 2
            v0 += a[i] * tp[i]
        else:
            mask = np.logical_and(tx > tp[i - 1], tx <= tp[i])
            delta = a[i] * (tx[mask] - tp[i - 1])
            vx[mask] = v0 + delta
            sx[mask] = s0 + v0 * (tx[mask] - tp[i - 1]) + a[i] * (
                    tx[mask] - tp[i - 1]) ** 2 / 2

            s0 += v0 * (tp[i] - tp[i - 1]) + a[i] * (tp[i] - tp[i - 1]) ** 2 / 2
            v0 += a[i] * (tp[i] - tp[i - 1])

        # print(v0, s0)

    plt.figure()
    plt.plot(tx, vx)
    plt.plot(tx, sx)
    plt.show()
    return vx, sx


if __name__ == '__main__':
    tp, a = calculate_slew(0 * u.deg,
                           -50 * u.deg,
                           -2 * u.deg / u.second)
    print(tp, a)
