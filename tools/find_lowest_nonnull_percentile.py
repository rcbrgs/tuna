import numpy

def find_lowest_nonnull_percentile ( array ):
    lower_percentile = 1
    lower_percentile_value = numpy.percentile ( array, lower_percentile )
    while ( lower_percentile_value <= 0 ):
        lower_percentile += 1
        if lower_percentile == 100:
            lower_percentile = 1
            break
        lower_percentile_value = numpy.percentile ( array, lower_percentile )

    return lower_percentile
