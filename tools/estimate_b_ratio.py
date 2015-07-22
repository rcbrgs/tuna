import logging
import math
import tuna

class b_ratio_estimator ( object ):
    def __init__ ( self, radii, orders ):
        self.log = logging.getLogger ( __name__ )
        self.__version__ = '0.1.1'
        self.changelog = {
            '0.1.1'  : "Error: was returning b**2 instead of its radix.",
            '0.1.0'  : "First changelogged version."
            }
        
        self.orders = orders
        self.radii  = radii        

    def estimate ( self ):
        """
        The self.radii list should contain at least two radii.
        The innermost radii is of order "p", and the next one is of order "p-1".
        """
        if not isinstance ( self.radii, list ):
            self.log.error ( "radii should be a list!" )
            return None

        if len ( self.radii ) < 2:
            self.log.error ( "Estimation requires at least 2 radii!" )
            return None

        if not isinstance ( self.orders, list ):
            self.log.error ( "orders should be a list!" )
            return None

        if len ( self.orders ) != len ( self.radii ):
            self.log.error ( "radii and orders should have the same length!" )
            return None

        pc   = self.orders [ 0 ]
        pc_1 = self.orders [ 1 ]

        r    = self.radii  [ 0 ]
        r_1  = self.radii  [ 1 ]
        self.log.info ( "r = {:e}, pc = {:e}; r_1 = {:e}, pc_1 = {:e}".format ( r, pc, r_1, pc_1 ) )

        b_squared = 2 * pc_1 / ( pc**2 * ( r_1**2 - r**2 ) - 2 * pc * r_1**2 + r_1**2 )

        return math.sqrt ( b_squared )

def estimate_b_ratio ( radii, orders ):
    """
    From a list of radii, supposing each radius corresponds to the distance from a ring to the center, calculates b.
    """

    estimator = b_ratio_estimator ( radii, orders )
    estimate = estimator.estimate ( )
    return estimate
