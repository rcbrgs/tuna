from math import floor, sqrt
import numpy
from file_format import adhoc, file_reader, fits
from gui import widget_viewer_2d
from tools.get_pixel_neighbours import get_pixel_neighbours

class orders ( object ):
    """
    Responsible for creating arrays where each position correspond to the distance, in number of FSR bandwidths, from the intereference image center.
    """
    def __init__ ( self, log = print, iit_center = ( int, int ), regions = None, ring_borders = None, noise = numpy.ndarray ):
        """
        Initializes variables and calls the array creation method.
        """
        super ( orders, self ).__init__ ( )
        self.log = log
        self.__iit_center = iit_center
        self.__regions = regions
        self.__ring_borders = ring_borders
        self.__noise = noise
        self.__orders = None

        if ( self.__ring_borders != None and
             self.__regions != None ):
            self.run ( )

    def get_orders ( self ):
        """
        Returns the FSR distance array.
        """
        self.log ( __name__ )
        return self.__orders

    def run ( self ):
        """
        FSR distance array creation method.
        """
        self.log ( __name__ )
        regions = self.__regions
        ring_borders = self.__ring_borders
        orders = numpy.zeros ( shape = regions.shape )
        max_x = orders.shape[0]
        max_y = orders.shape[1]

        pixel_count = 0
        for x in range ( max_x ):
            for y in range ( max_y ):
                if ( ring_borders[x][y] == 1 ):
                    if ( self.__noise[x][y] == 0 ):
                        pixel_count += 1

        if pixel_count == 0:
            self.log ( "No borders detected in phase map." )
            self.log ( "Orders map set to zero-filled array." )
            self.__orders = numpy.zeros ( shape = self.__regions.shape )
            return
            
        center_x = self.__iit_center[0]
        center_y = self.__iit_center[1]
        center_color = regions[center_x][center_y] 
        if ( center_color == 0 ):
            self.log ( "Center detected to be on a border, which is wrong." )
            self.log ( "Setting FSR distance array to zero-filled array." )
            self.__orders = numpy.zeros ( shape = self.__regions.shape )
            return

        self.log ( "Center of symmetric rings possibly near (%d, %d)." % ( center_x, center_y ) )
        self.log ( "Center in region of color %d." % center_color )

        colors = [ ]
        connections = [ ]
        for x in range ( max_x ):
            for y in range ( max_y ):
                if ( regions[x][y] not in colors ):
                    colors.append ( regions[x][y] )
                if ( ring_borders[x][y] == 1 ):
                    neighbourhood = get_pixel_neighbours ( position = ( x, y ), array = regions )
                    relationship = []
                    for neighbour in neighbourhood:
                        if regions[neighbour[0]][neighbour[1]] > 1:
                            if regions[neighbour[0]][neighbour[1]] not in relationship:
                                relationship.append ( regions[neighbour[0]][neighbour[1]] )
                    if len ( relationship ) == 2:
                        if relationship not in connections:
                            if [ relationship[1], relationship[0] ] not in connections:
                                connections.append ( relationship )
        print ( "Neighbourhood connections: ", connections )
        colors.remove ( 0.0 )
        if -1 in colors:
            colors.remove ( -1 )
        print ( "Region colors: %s." % colors )

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
                #region_order[order] = [ color ]
                break
                        
            self.log ( "region_order = %s." % region_order )
            self.log ( "connections = %s." % str ( connections ) )

        # region_order indexed the order for each region in inverted fashion.
        # So the dictionary is re-indexed to account for that.
        reindexed_region_order = { }
        for entry in region_order.keys ( ):
            reindexed_region_order [order - entry] = region_order[entry]
        self.log ( "reindexed_region_order = %s." % ( reindexed_region_order ) )
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
                if ( ring_borders[x][y] == 1 and
                     self.__noise[x][y] == 0 ):
                    possible_orders = [ ]
                    for neighbour in get_pixel_neighbours ( position = ( x, y ), array = orders ):
                        if orders[neighbour[0]][neighbour[1]] not in possible_orders:
                            if ring_borders[neighbour[0]][neighbour[1]] == 0:
                                possible_orders.append ( orders[neighbour[0]][neighbour[1]] )
                    if ( len ( possible_orders ) == 0 ):
                        orders[x][y] = 0
                        continue
                    if ( len ( possible_orders ) == 1 ):
                        # Sometomes the border is two pixels thick, and the only non-border neighbours
                        # will be of the next region.
                        orders[x][y] = numpy.amin ( numpy.array ( possible_orders ) ) - 1
                    else:
                        orders[x][y] = numpy.amin ( numpy.array ( possible_orders ) )

        # Supposing the noise is on the perifery of the map, attributing the highest order to the noise
        # region is better than attributing order = 0 there.
        max_order = numpy.amax ( orders )
        orders += max_order * self.__noise
                    
        self.__orders = orders
