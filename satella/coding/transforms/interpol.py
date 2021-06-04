import typing as tp
from satella.coding.typing import U, K
import bisect


def linear_interpolate(series: tp.Sequence[tp.Tuple[K, U]], t: K,
                       clip: bool = False) -> U:
    """
    Given a sorted (ascending) series of (t_value, y_value) interpolating linearly a function of
    y=f(t) compute a linear approximation of f at t
    of two closest values.

    t must be larger or equal to t_min and smaller or equal to t_max

    :param series: series of (t, y) sorted by t ascending
    :param t: t to compute the value for
    :param clip: if set to True, then values t: t<t_min f(t_min) will be returned
        and for values t: t>t_max f(t_max) will be returned
    :return: return value
    :raise ValueError: t was smaller than t_min or greater than t_max
    """
    if t < series[0][0]:
        if clip:
            return series[0][1]
        else:
            raise ValueError('t smaller than t_min')
    if t > series[-1][0]:
        if clip:
            return series[-1][1]
        else:
            raise ValueError('t greater than t_max')

    if t == series[0][0]:
        return series[0][1]

    i = bisect.bisect_left([y[0] for y in series], t) - 1

    if i == len(series) - 1:
        return series[-1][1]

    t1, v1 = series[i]
    t2, v2 = series[i + 1]

    assert t1 <= t <= t2, 'Series not sorted!'
    return (v2 - v1) / (t2 - t1) * (t - t1) + v1
