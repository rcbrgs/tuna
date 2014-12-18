from sympy import Point, Line

class find_rings_by_expading_ellipses ( object ):
    def __init__ ( self, image_ndarray = None ):
        if image_ndarray:
            self.__image_ndarray = image_ndarray

    def set_ellipse_center_region ( self, initial_x = None, initial_y = None, final_x = None, final_y = None ):
        if initial_x:
            self._initial_x = initial_x
        if initial_y:
            self._initial_y = initial_y
        if final_x:
            self._final_x = final_x
        if final_y:
            self._final_y = final_y

    def set_signal_magnitude_threshold ( self, threshold = None ):
        if threshold:
            self._signal_magnitude_threshold = threshold

    def find_ellipse_of_maximal_focii_distance ( self ):
        """
        
        """
        # generate possible focii tuples object: A list of two coordenate tuples.
        possible_focii = [ [ ( 100, 100 ), ( 110, 110 ) ],
                           [ ( 110, 110 ), ( 120, 120 ) ] ]
        # 1: select next focii or return current best ellipse in results
        focii = possible_focii[0]
        # find maximal distance
        image_max_x = self.__image_ndarray.shape[0]
        image_max_y = self.__image_ndarray.shape[1]
        line_top = Line ( Point ( 0, image_max_y ), Point ( image_max_x, image_max_y ) )
        line_left = Line ( Point ( 0, 0 ), Point ( 0, image_max_y ) )
        line_bottom = Line ( Point ( 0, 0 ), Point ( image_max_x, 0 ) )
        line_right = Line ( Point ( image_max_x, 0 ), Point ( image_max_x, image_max_y ) )
        ## Calculate maximum major and minor axis that fit in the image
        focus_1 = Point ( focii[0] )
        focus_2 = Point ( focii[1] )
        line_major_axis = Line ( focus_1, focus_2 )
        ### Crop line into segment that is inside image
        cross_top = line_major_axis.intersection ( line_top )
        cross_left = line_major_axis.intersection ( line_left )
        cross_bottom = line_major_axis.intersection ( line_bottom )
        cross_right = line_major_axis.intersection ( line_right )
        cross_1 = None
        cross_2 = None
        if cross_top != []:
            cross_1 = cross_top
        if cross_left != []:
            if cross_1:
                cross_2 = cross_left
            else:
                cross_1 = cross_left
        if cross_bottom != []:
            if cross_1:
                cross_2 = cross_bottom
            else:
                cross_1 = cross_bottom
        if cross_right != []:
            cross_2 = cross_right
        distance = Line ( cross_1, focus_1 ).length ( )
        temp = Line ( cross_1, focus_2 ).length ( )
        if distance > temp:
            distance = temp
        temp = Line ( cross_2, focus_1 ).length ( )
        if distance > temp:
            distance = temp
        temp = Line ( cross_2, focus_2 ).length ( )
        if distance > temp:
            distance = temp
        major_axis_extreme_1 = Point ( focus_1.x + distance * cos ( line_major_axis.slope ), focus_1.y + distance * cos ( line_major_axis.slope ) ) # had to take account of inclination...
        ### Measure linear distance from either focus to the line segment
        ### Select shortest distance as the major axis upper limit
        ### Set minor axis as equal to major axis
        ### Verify minor axis inside image, shorten until it does
        ## 2: Get pixel coordinates for all points in a ellipse with given focii and axis
        ## Check for violations of threshold
        ## If all points check, return this ellipse.
        ## If major axis == 2 pixels, return empty.
        ## If major axis > minor axis, shorten major axis by 1 pixel. Otherwise shorten minor axis.
        ## Goto 2:

        # remove tuples for which it is impossible to get greater distance
        # add current ellipse to result
        # goto 1:
        
