import math

def calculate_distance ( origin, destiny ):
    return math.sqrt ( ( origin [ 0 ] - destiny [ 0 ] ) ** 2 +
                       ( origin [ 1 ] - destiny [ 1 ] ) ** 2 )
