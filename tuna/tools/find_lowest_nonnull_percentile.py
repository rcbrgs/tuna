import numpy

def find_lowest_nonnull_percentile ( array ):
    """
    This function will attempt to find the lowest value, starting at 1, which makes numpy.percentile return a non-null value when fed the input array.

    Parameters:

    - array, a numpy.ndarray containing the data.
    """
    lower_percentile = 1
    lower_percentile_value = numpy.percentile ( array, lower_percentile )
    while ( lower_percentile_value <= 0 ):
        lower_percentile += 1
        if lower_percentile == 100:
            lower_percentile = 1
            break
        lower_percentile_value = numpy.percentile ( array, lower_percentile )

    return lower_percentile
