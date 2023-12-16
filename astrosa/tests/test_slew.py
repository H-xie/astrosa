from math import sqrt

import astropy.units as u
from pytest import approx

from astrosa.assess import calculate_slew, plot_curve


def test_zero_initial_velocity1():
    # cannot reach max velocity
    tp, a = calculate_slew(0 * u.deg,
                           2 * u.deg,
                           0 * u.deg / u.second)

    print(tp, a)

    assert tp[0].value == approx(sqrt(2))
    assert tp[1].value == approx(2 * sqrt(2))
    assert a[0].value == 1
    assert a[1].value == -1

    tp, a = calculate_slew(0 * u.deg,
                           -2 * u.deg,
                           0 * u.deg / u.second)
    print(tp, a)
    assert tp[0].value == approx(sqrt(2))
    assert tp[1].value == approx(2 * sqrt(2))
    assert a[0].value == -1
    assert a[1].value == 1

    tp, a = calculate_slew(10 * u.deg,
                           2 * u.deg,
                           0 * u.deg / u.second)
    print(tp, a)
    assert tp[0].value == approx(sqrt(8))
    assert tp[1].value == approx(2 * sqrt(8))
    assert a[0].value == -1
    assert a[1].value == 1

    tp, a = calculate_slew(0 * u.deg,
                           -20 * u.deg,
                           0 * u.deg / u.second)
    print(tp, a)
    assert tp[0].value == approx(sqrt(20))
    assert tp[1].value == approx(2 * sqrt(20))
    assert a[0].value == -1
    assert a[1].value == 1


def test_zero_initial_velocity2():
    # can reach max velocity
    tp, a = calculate_slew(0 * u.deg,
                           40 * u.deg,
                           0 * u.deg / u.second)
    print(tp, a)
    assert tp[0].value == approx(6)
    assert tp[1].value == approx(6 + 4 / 6)
    assert tp[2].value == approx(12 + 4 / 6)
    assert a[0].value == 1
    assert a[1].value == 0
    assert a[2].value == -1

    tp, a = calculate_slew(0 * u.deg,
                           36 * u.deg,
                           0 * u.deg / u.second)
    print(tp, a)
    assert tp[0].value == approx(6)
    assert tp[1].value == approx(6)
    assert tp[2].value == approx(12)
    assert a[0].value == 1
    assert a[1].value == 0
    assert a[2].value == -1
    tp, a = calculate_slew(0 * u.deg,
                           -40 * u.deg,
                           0 * u.deg / u.second)
    print(tp, a)
    assert tp[0].value == approx(6)
    assert tp[1].value == approx(6 + 4 / 6)
    assert tp[2].value == approx(12 + 4 / 6)
    assert a[0].value == -1
    assert a[1].value == 0
    assert a[2].value == 1

    tp, a = calculate_slew(-40 * u.deg,
                           80 * u.deg,
                           0 * u.deg / u.second)
    print(tp, a)
    assert tp[0].value == approx(6)
    assert tp[1].value == approx(20)
    assert tp[2].value == approx(26)
    assert a[0].value == 1
    assert a[1].value == 0
    assert a[2].value == -1


def test_same_direction():
    tp, a = calculate_slew(0 * u.deg,
                           2 * u.deg,
                           6 * u.deg / u.second)
    print(tp, a)
    vx, sx = plot_curve(6 * u.deg / u.second,
                        0 * u.deg,
                        tp,
                        a,
                        6 * u.deg / u.second)
    assert vx.max().value <= 6
    assert sx[-1].value == approx(2)

    tp, a = calculate_slew(0 * u.deg,
                           50 * u.deg,
                           6 * u.deg / u.second)
    print(tp, a)
    vx, sx = plot_curve(6 * u.deg / u.second,
                        0 * u.deg,
                        tp,
                        a,
                        6 * u.deg / u.second)
    assert vx.max().value <= 6
    assert sx[-1].value == approx(50)

    tp, a = calculate_slew(0 * u.deg,
                           50 * u.deg,
                           2 * u.deg / u.second)
    print(tp, a)
    vx, sx = plot_curve(2 * u.deg / u.second,
                        0 * u.deg,
                        tp,
                        a,
                        6 * u.deg / u.second)
    assert vx.max().value <= 6
    assert sx[-1].value == approx(50)

    tp, a = calculate_slew(0 * u.deg,
                           -50 * u.deg,
                           -2 * u.deg / u.second)
    print(tp, a)
    vx, sx = plot_curve(-2 * u.deg / u.second,
                        0 * u.deg,
                        tp,
                        a,
                        6 * u.deg / u.second)
    assert vx.min().value >= -6
    assert sx[-1].value == approx(-50)

    tp, a = calculate_slew(0 * u.deg,
                           20 * u.deg,
                           3 * u.deg / u.second)
    print(tp, a)
    vx, sx = plot_curve(3 * u.deg / u.second,
                        0 * u.deg,
                        tp,
                        a,
                        6 * u.deg / u.second)
    assert vx.max().value <= 6
    assert sx[-1].value == approx(20)

    tp, a = calculate_slew(0 * u.deg,
                           -20 * u.deg,
                           -3 * u.deg / u.second)
    print(tp, a)
    vx, sx = plot_curve(-3 * u.deg / u.second,
                        0 * u.deg,
                        tp,
                        a,
                        6 * u.deg / u.second)
    assert vx.min().value >= -6
    assert sx[-1].value == approx(-20)

    tp, a = calculate_slew(0 * u.deg,
                           18.1 * u.deg,
                           5 * u.deg / u.second)
    print(tp, a)
    vx, sx = plot_curve(5 * u.deg / u.second,
                        0 * u.deg,
                        tp,
                        a,
                        6 * u.deg / u.second)
    assert vx.max().value <= 6
    assert sx[-1].value == approx(18.1)
    tp, a = calculate_slew(0 * u.deg,
                           -18.1 * u.deg,
                           -5 * u.deg / u.second)
    print(tp, a)
    vx, sx = plot_curve(-5 * u.deg / u.second,
                        0 * u.deg,
                        tp,
                        a,
                        6 * u.deg / u.second)
    assert vx.min().value >= -6
    assert sx[-1].value == approx(-18.1)

    tp, a = calculate_slew(30 * u.deg,
                           -30 * u.deg,
                           -5 * u.deg / u.second)
    print(tp, a)
    vx, sx = plot_curve(-5 * u.deg / u.second,
                        30 * u.deg,
                        tp,
                        a,
                        6 * u.deg / u.second)
    assert vx.min().value >= -6
    assert sx[-1].value == approx(-30)


def test_different_direction():
    tp, a = calculate_slew(-30 * u.deg,
                           40 * u.deg,
                           -6 * u.deg / u.second)
    print(tp, a)
    vx, sx = plot_curve(-6 * u.deg / u.second,
                        -30 * u.deg,
                        tp,
                        a,
                        6 * u.deg / u.second)
    assert vx.min().value >= -6
    assert sx[-1].value == approx(40)

    tp, a = calculate_slew(30 * u.deg,
                           29 * u.deg,
                           4 * u.deg / u.second)
    print(tp, a)
    vx, sx = plot_curve(4 * u.deg / u.second,
                        30 * u.deg,
                        tp,
                        a,
                        6 * u.deg / u.second)
    assert vx.max().value <= 6
    assert sx[-1].value == approx(29)

def test_scene32():
    tp,a=calculate_slew(0*u.deg,
                        34*u.deg,
                        2*u.deg/u.second)
    print(tp,a)
    vx,sx=plot_curve(2*u.deg/u.second,
                     0*u.deg,
                     tp,
                     a,
                     6*u.deg/u.second)
    assert vx.max().value<=6
    assert sx[-1].value==approx(34)

    tp,a=calculate_slew(0*u.deg,
                        -34*u.deg,
                        -2*u.deg/u.second)
    print(tp,a)
    vx,sx=plot_curve(-2*u.deg/u.second,
                     0*u.deg,
                     tp,
                     a,
                     6*u.deg/u.second)
    assert vx.max().value<=6
    assert sx[-1].value==approx(-34)