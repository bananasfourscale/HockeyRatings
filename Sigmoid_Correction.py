from math import exp, log
from numpy import std, mean


# The arbitrary sigmoid peak that I've decided to use because reasons
sigmoid_peak = .990048

# The standard deviation scalar to get the 1st percentile
ninety_nineth_per = 2.58


def solve_for_scalar_value(data_set : dict={}) -> float:
    mean_val = mean(list(data_set.values()))
    std_dev = std(list(data_set.values()))
    if (mean_val == 0) and (std_dev == 0):
        return 0
    return (-1 * log((1 - sigmoid_peak) / sigmoid_peak)) / \
        ((mean_val + (std_dev * ninety_nineth_per)) - mean_val)

def apply_sigmoid_correction(data_set : dict={}, low_desired : bool=False) \
                                                                        -> dict:
    scalar = solve_for_scalar_value(data_set)
    mean_val = mean(list(data_set.values()))
    for item in data_set.keys():
        if low_desired is True:
            data_set[item] = \
                1 / (1 + exp(-1 * (-1 * scalar * (data_set[item] - mean_val))))
        else:
            data_set[item] = \
                1 / (1 + exp(-1 * (scalar * (data_set[item] - mean_val))))
    return data_set
