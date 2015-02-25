"""
Responsible for storing data cubes.
"""

import numpy

class cube ( object ):
    """
    Responsible for storing data cubes.
    """
    def __init__ ( self,
                   log = print,
                   tan_data = None ):
        super ( cube, self ).__init__ ( )
        self.log = log
        if tan_data != None:
            self.__ndim = tan_data.ndim
            if self.__ndim == 3:
                self.__tan_data = numpy.copy ( tan_data )
                self.__planes = self.__tan_data.shape [ 0 ]
                self.__rows   = self.__tan_data.shape [ 1 ]
                self.__cols   = self.__tan_data.shape [ 2 ]
            elif self.__ndim == 2:
                self.__tan_data = numpy.ndarray ( shape = ( 1, tan_data.shape [ 0 ], tan_data.shape [ 1 ] ) )
                self.__planes = 1
                self.__rows   = self.__tan_data.shape [ 1 ]
                self.__cols   = self.__tan_data.shape [ 2 ]
                for i_row in self.get_rows_range ( ):
                    for i_col in self.get_cols_range ( ):
                        self.__tan_data [ 0 ] [ i_row ] [ i_col ] = tan_data [ i_row ] [ i_col ]
            else:
                self.log ( "Data has dimentionality different from [2, 3] dimensions." )

    def get_array ( self ):
        return self.__tan_data

    def get_cols ( self ):
        return self.__cols

    def get_cols_range ( self ):
        return range ( self.__cols )

    def get_planes ( self ):
        return self.__planes

    def get_planes_range ( self ):
        return range ( self.__planes )

    def get_rows ( self ):
        return self.__rows

    def get_rows_range ( self ):
        return range ( self.__rows )
