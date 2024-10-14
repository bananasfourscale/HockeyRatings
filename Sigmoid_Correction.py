# from math import exp, log
from numpy import std, mean


# The arbitrary sigmoid peak that I've decided to use because reasons
sigmoid_peak = .990048

# The standard deviation scalar to get the 1st percentile
ninety_nineth_per = 2.58


def normalize_set(data_set : dict={}) -> dict:
    data_list = list(data_set.values())
    normal_set = {}
    max_data = max(data_list)
    min_data = min(data_list)
    try:
        if (max_data != min_data):
            for item in data_set.keys():
                normal_set[item] = (
                    (data_set[item] - min_data) / (max_data - min_data)
                )
        else:
            for item in data_set.keys():
                normal_set[item] = (data_set[item] / len(data_list))
    except RuntimeWarning as w:
        print(w)
        print("min = ", min_data, "max = ", max_data, "key = ", item,
            "value = ", data_set[item])
    return normal_set


def solve_for_scalar_value(data_set : dict={}, debug : bool=False) -> float:
    normalized_set = normalize_set(data_set)
    if debug:
        # print(normalized_set)
        print("\tnorm mean = ", mean(list(normalized_set.values())))
        print("\tnorm variance = ", pow(std(list(normalized_set.values())), 2))
        print("\tnorm variance / mean = ", pow(std(list(normalized_set.values())), 2) /
            mean(list(normalized_set.values())))
        print()

    # Index of dispersion (σ^2 / μ)
    if mean(list(normalized_set.values())) == 0:
        return 0
    return (pow(std(list(normalized_set.values())), 2) /
            mean(list(normalized_set.values())))
    # mean_val = mean(list(data_set.values()))
    # std_dev = std(list(data_set.values()))
    # print("\tmean = ", mean_val)
    # print("\tvariance = ", pow(std_dev, 2))
    # print("\tvariance/mean = ", pow(std_dev, 2) / mean_val)
    # if (std_dev == 0):
    #     return 0
    # return (
    #     (-1 * log((1 - sigmoid_peak) / sigmoid_peak)) /
    #     ((mean_val + (std_dev * ninety_nineth_per)) - mean_val)
    # )

                             
def apply_sigmoid_correction(data_set : dict={}, low_desired : bool=False,                
    debug : bool=False) -> dict:

    scalar = solve_for_scalar_value(data_set, debug)\

    mean_val = mean(list(data_set.values()))
    sig = std(list(data_set.values()))
    # data_set['99sig'] = mean_val + (sig * ninety_nineth_per)
    # data_set['-99sig'] = mean_val - (sig * ninety_nineth_per)
    normal_set = normalize_set(data_set)
    if debug:
        sorted_set = {k: v for k, v in sorted(data_set.items(), key=lambda item: item[1])}
    for item in data_set.keys():
        if low_desired is True:
            data_set[item] = 1 - (
                (
                (
                    ((2*normal_set[item] - 1) - 
                        (scalar * (2*normal_set[item] - 1)))
                    /
                    (scalar - (2 * scalar * abs((2*normal_set[item] - 1))) + 1)
                ) + 1
                )
                / 2
            )
        else:
            data_set[item] = (
                (
                (
                    ((2*normal_set[item] - 1) - 
                        (scalar * (2*normal_set[item] - 1)))
                    /
                    (scalar - (2 * scalar * abs((2*normal_set[item] - 1))) + 1)
                ) + 1
                )
                / 2
            )
    if debug:
        for key in sorted_set.keys():
            print("base {} : {}".format(key, sorted_set[key]))
            print("normalized {} : {}".format(key, normal_set[key]))
            print("scaled {} : {}".format(key, data_set[key]))
            print()
    # data_set.pop('99sig')
    # data_set.pop('-99sig')
    return data_set

'''
https://dhemery.github.io/DHE-Modules/technical/sigmoid/#stages
y= (x - (k * x))/ (k - (2 * k * abs(x)) + 1)
k < 0 would have a sharper middle curve and favor stats with lower variance
k > 0 would have sharper ends and favor stats with a higher variance

first normalize all input data between 0 and 1 with
if max(x_data) != min(x_data)
x_normalized = (x_data[x] - min(x_data)) / (max(x_data) - min(x_data))
else
x_normalized = x / len(x_data)
'''
