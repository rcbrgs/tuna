from math import floor, sqrt
import numpy
from file_format import adhoc, file_reader, fits
from gui import widget_viewer_2d
from tools.get_pixel_neighbours import get_pixel_neighbours
from time import time

class orders ( object ):
    """
    Responsible for creating arrays where each position correspond to the distance, in number of FSR bandwidths, from the intereference image center.
    """
    def __init__ ( self, 
                   fa_borders_to_center_distances = numpy.ndarray, 
                   log = print, 
                   iit_center = ( int, int ), 
                   regions = None, 
                   ring_borders = None, 
                   noise = numpy.ndarray ):
        """
        Initializes variables and calls the array creation method.
        """
        super ( orders, self ).__init__ ( )
        self.log = log
        self.__fa_borders_to_center_distances = fa_borders_to_center_distances
        self.__iit_center = iit_center
        self.__regions = regions
        self.__ring_borders = ring_borders
        self.__noise = noise
        self.__orders = None

        if ( self.__ring_borders != None and
             self.__regions != None ):
            self.run ( )

    def ordenate_regions ( self ):
        """
        From the unordered regions array, find the correct reordering.
        This is done by finding the average distance to the center for each color.
        Region is attributed according to this average and the border rings values.
        """
        d_regions_average_distance = { }
        for i_row in range ( self.__regions.shape[0] ):
            for i_col in range ( self.__regions.shape[1] ):
                f_region = self.__regions[i_row][i_col]
                f_distance = sqrt ( ( self.__iit_center[0] - i_col ) ** 2 +
                                    ( self.__iit_center[1] - i_row ) ** 2 )
                if f_region not in d_regions_average_distance.keys ( ):
                    d_regions_average_distance[f_region] = [f_distance, 1]
                else:
                    d_regions_average_distance[f_region][0] += f_distance
                    d_regions_average_distance[f_region][1] += 1

        for f_region in d_regions_average_distance.keys ( ):
            d_regions_average_distance[f_region][0] /= d_regions_average_distance[f_region][1]
            self.log ( "d_regions_average_distance [ %f ] = %s" % ( f_region, str ( d_regions_average_distance[f_region] ) ) )
        return d_regions_average_distance

    def ordenate_regions_old ( self ):
        """
        From the unordered regions array, find the correct reordering.
        This is done by finding the minimal distance to the center for each color.
        """
        ift_colors_min_distance = { }
        for i_row in range ( self.__regions.shape[0] ):
            for i_col in range ( self.__regions.shape[1] ):
                i_color = self.__regions[i_row][i_col]
                f_distance = sqrt ( ( self.__iit_center[0] - i_col ) ** 2 +
                                    ( self.__iit_center[1] - i_row ) ** 2 )
                if i_color not in ift_colors_min_distance.keys ( ):
                    ift_colors_min_distance[i_color] = f_distance
                elif ift_colors_min_distance[i_color] > f_distance:
                    ift_colors_min_distance[i_color] = f_distance

        for color in ift_colors_min_distance.keys ( ):
            self.log ( "ift_colors_min_distance [ %f ] = %s" % ( color, str ( ift_colors_min_distance[color] ) ) )
        return ift_colors_min_distance

    def get_orders ( self ):
        """
        Returns the FSR distance array.
        """
        #self.log ( __name__ )
        return self.__orders

    def run_old ( self ):
        """
        FSR distance array creation method.
        """
        i_start = time ( )
        self.log ( "orders.run", end='' )

        regions = self.__regions
        ring_borders = self.__ring_borders
        orders = numpy.zeros ( shape = regions.shape )
        max_x = orders.shape[0]
        max_y = orders.shape[1]

        pixel_count = 0
        for x in range ( max_x ):
            for y in range ( max_y ):
                if ( ring_borders[x][y] > 0 ):
                    #if ( self.__noise[x][y] == 0 ):
                    #    pixel_count += 1
                    pixel_count += 1

        if pixel_count == 0:
            self.log ( "No borders detected in phase map." )
            self.log ( "Orders map set to zero-filled array." )
            self.__orders = numpy.zeros ( shape = self.__regions.shape )
            return

        ift_colors_min_distances = self.ordenate_regions ( )
        ift_colors_min_distances.remove ( 0.0 )
        

        
        center_x = self.__iit_center[0]
        center_y = self.__iit_center[1]
        center_color = regions[center_x][center_y] 
        if ( center_color == 0 ):
            self.log ( "Center detected to be on a border, which is wrong." )
            self.log ( "Setting FSR distance array to zero-filled array." )
            self.__orders = numpy.zeros ( shape = self.__regions.shape )
            return

        #self.log ( "Center of symmetric rings possibly near (%d, %d)." % ( center_x, center_y ) )
        #self.log ( "Center in region of color %d." % center_color )

        colors = [ ]
        for x in range ( max_x ):
            for y in range ( max_y ):
                if ( regions[x][y] not in colors ):
                    colors.append ( regions[x][y] )
        colors.remove ( 0.0 )
        if -1 in colors:
            colors.remove ( -1 )
        print ( "Region colors: %s." % colors )

        connections = [ ]
        #for x in range ( max_x ):
        #    for y in range ( max_y ):
        #        if ( regions[x][y] not in colors ):
        #            colors.append ( regions[x][y] )
        #        if ( ring_borders[x][y] == 1 ):
        #            neighbourhood = get_pixel_neighbours ( position = ( x, y ), array = regions )
        #            relationship = []
        #            for neighbour in neighbourhood:
        #                if regions[neighbour[0]][neighbour[1]] > 1:
        #                    if regions[neighbour[0]][neighbour[1]] not in relationship:
        #                        relationship.append ( regions[neighbour[0]][neighbour[1]] )
        #            if len ( relationship ) == 2:
        #                if relationship not in connections:
        #                    if [ relationship[1], relationship[0] ] not in connections:
        #                        connections.append ( relationship )
        #print ( "Neighbourhood connections: ", connections )


        # compose connections as a list where each element is a list of regions colors that border a given ring.
        ia_explored_borders = ring_borders
        it_distance_connections = { }
        for x in range ( max_x ):
            for y in range ( max_y ):
                i_distance = int ( ring_borders[x][y] )
                if ( i_distance > 0 ):
                    neighbourhood = get_pixel_neighbours ( position = ( x, y ), array = regions )
                    relationship = [ ]
                    for neighbour in neighbourhood:
                        if regions[neighbour[0]][neighbour[1]] > 1:
                            if regions[neighbour[0]][neighbour[1]] not in relationship:
                                relationship.append ( regions[neighbour[0]][neighbour[1]] )
                    if len ( relationship ) == 2:
                        if relationship not in connections:
                            if [ relationship[1], relationship[0] ] not in connections:
                                connections.append ( relationship )
                    elif ( len ( relationship ) == 1 ):
                        if i_distance not in it_distance_connections.keys ( ):
                            it_distance_connections[i_distance] = relationship
                        else:
                            if relationship[0] not in it_distance_connections[i_distance]:
                                it_distance_connections[i_distance].append ( relationship[0] )
                                
        print ( "Neighbourhood connections: ", connections )
        print ( "Per distance connections:  ", it_distance_connections )

        # 
        

        region_order = { 0 : [ center_color ] }
        order = 0

        self.log ( "region_order = %s." % region_order )
        self.log ( "connections = %s." % str ( connections ) )

        while connections != []:
            flag = False
            while order in region_order:
                order += 1
            for color in colors:
                for connectee in region_order[order-1]:
                    if ( [color, connectee] in connections ):
                        connections.remove ( [color, connectee] )
                        if ( order in region_order ):
                            region_order[order].append ( color )
                        else:
                            region_order[order] = [ color ]
                        flag = True
                    if ( [connectee, color] in connections ):
                        connections.remove ( [connectee, color] )
                        if ( order in region_order ):
                            region_order[order].append ( color )
                        else:
                            region_order[order] = [ color ]
                        flag = True
            if flag == False:
                self.log ( "Broke connections re-indexing to avoid infinite loop." )
                region_order[order] = [ color ]
                break
                        
            self.log ( "region_order = %s." % region_order )
            self.log ( "connections = %s." % str ( connections ) )

        # region_order indexed the order for each region in inverted fashion.
        # So the dictionary is re-indexed to account for that.
        #reindexed_region_order = { }
        #for entry in region_order.keys ( ):
        #    reindexed_region_order [order - entry] = region_order[entry]
        #self.log ( "reindexed_region_order = %s." % ( reindexed_region_order ) )
        #region_order = reindexed_region_order

        for x in range ( max_x ):
            for y in range ( max_y ):
                color = regions[x][y]
                for order_key in region_order.keys ( ):
                    if color in region_order[order_key]:
                        orders[x][y] = order_key
                        break

        # Rings borders should get the value of its smallest neighbouring region.
        for x in range ( max_x ):
            for y in range ( max_y ):
                #if ( ring_borders[x][y] == 1 and
                #     self.__noise[x][y] == 0 ):
                if ( ring_borders[x][y] == 1 ):
                    possible_orders = [ ]
                    for neighbour in get_pixel_neighbours ( position = ( x, y ), array = orders ):
                        if orders[neighbour[0]][neighbour[1]] not in possible_orders:
                            if ring_borders[neighbour[0]][neighbour[1]] == 0:
                                possible_orders.append ( orders[neighbour[0]][neighbour[1]] )
                    if ( len ( possible_orders ) == 0 ):
                        orders[x][y] = -2
                        continue
                    if ( len ( possible_orders ) == 1 ):
                        # Sometomes the border is two pixels thick, and the only non-border neighbours
                        # will be of the next region.
                        #orders[x][y] = numpy.amin ( numpy.array ( possible_orders ) ) - 1
                        orders[x][y] = possible_orders[0]
                    else:
                        orders[x][y] = numpy.amin ( numpy.array ( possible_orders ) )

        # Supposing the noise is on the perifery of the map, attributing the highest order to the noise
        # region is better than attributing order = 0 there.
        #max_order = numpy.amax ( orders )
        #orders += max_order * self.__noise
                    
        self.__orders = orders

        self.log ( " %ds." % ( time ( ) - i_start ) )


    def run ( self ):
        self.create_fsr_map ( )

    def create_fsr_map ( self ):
        """
        FSR distance array creation method.
        """
        i_start = time ( )
        self.log ( "orders.run", end='' )

        regions = self.__regions
        ring_borders = self.__ring_borders
        orders = numpy.zeros ( shape = regions.shape )
        max_x = orders.shape[0]
        max_y = orders.shape[1]

        pixel_count = 0
        for x in range ( max_x ):
            for y in range ( max_y ):
                if ( ring_borders[x][y] > 0 ):
                    #if ( self.__noise[x][y] == 0 ):
                    #    pixel_count += 1
                    pixel_count += 1

        if pixel_count == 0:
            self.log ( "No borders detected in phase map." )
            self.log ( "Orders map set to zero-filled array." )
            self.__orders = numpy.zeros ( shape = self.__regions.shape )
            return

        d_regions_average_distances = self.ordenate_regions ( )
        
        # find how many rings are there
        fl_rings = [ ]
        for i_row in range ( max_x ):
            for i_col in range ( max_y ):
                if self.__fa_borders_to_center_distances [ i_row ] [ i_col ] > 0:
                    b_possible_new_ring = True
                    for f_ring in fl_rings:
                        if ( ( self.__fa_borders_to_center_distances [ i_row ] [ i_col ] < f_ring + 5 ) and
                             ( self.__fa_borders_to_center_distances [ i_row ] [ i_col ] > f_ring - 5 ) ):
                            b_possible_new_ring = False
                    if b_possible_new_ring:
                        fl_rings.append ( self.__fa_borders_to_center_distances [ i_row ] [ i_col ] )
        self.log ( "fl_rings = %s" % str ( fl_rings ) )

        # order rings by distance
        fl_ordered_rings = sorted ( fl_rings )
        self.log ( "fl_ordered_rings = %s" % str ( fl_ordered_rings ) )

        # attribute FSR by verifying ring-relative "position"
        d_regions_fsr = { }
        fl_regions = list ( d_regions_average_distances.keys ( ) )
        while ( len ( fl_regions ) > 0 ):
            f_region = fl_regions[0]
            f_average_distance = float ( d_regions_average_distances [ f_region ] [ 0 ]  )
            i_region_fsr = len ( fl_ordered_rings )
            for i_fsr in range ( len ( fl_ordered_rings ) ):
                if f_average_distance < fl_ordered_rings [ i_fsr ]:
                    i_region_fsr = i_fsr
                    break
            d_regions_fsr [ f_region ] = i_region_fsr
            fl_regions.remove ( f_region )

        self.log ( "d_regions_fsr = %s" % str ( d_regions_fsr ) ) 

        for i_row in range ( max_x ):
            for i_col in range ( max_y ):
                orders [ i_row ] [ i_col ] = d_regions_fsr [ self.__regions [ i_row ] [ i_col ] ]

        # correction for center deviation: 
        # row-wise, each fsr increase can happen only when the wrapped map goes from max channel to 0,
        # and each fsr decrease can happen only when the wrapped map goes from 0 to max channel.
        self.log ( "Center deviation correction" )
        for i_row in range ( max_x ):
            i_previous = orders [ i_row ] [ 0 ]
            for i_col in range ( 1, max_y ):
                if orders [ i_row ] [ i_col ] > i_previous:
                    if self.__fa_borders_to_center_distances [ i_row ] [ i_col ] == 0:
                        orders [ i_row ] [ i_col ] = i_previous
                        print ( ">" )
                if orders [ i_row ] [ i_col ] < i_previous:
                    if self.__fa_borders_to_center_distances [ i_row ] [ i_col ] == 0:
                        orders [ i_row ] [ i_col ] = i_previous
                        print ( "<" )
                i_previous = orders [ i_row ] [ i_col ]
        
        self.__orders = orders

        self.log ( " %ds." % ( time ( ) - i_start ) )
