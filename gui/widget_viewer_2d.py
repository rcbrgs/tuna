"""
widget_viewer_2d displays 2d images in a dock.

It is composed of a QDockWidget that displays a QPixMap. Eventually, more image-related functions will be added here.
"""

import numpy
from PyQt4.QtGui import QColor, QImage, QPixmap
import pylab
import struct
from PyQt4.QtGui import QDockWidget, QGridLayout, QLabel, QPalette, QPixmap, QScrollArea
from PyQt4.QtCore import pyqtSignal, QSize

class widget_viewer_2d ( QDockWidget ):
    opened = pyqtSignal ( str )
    closed = pyqtSignal ( str )
    def __init__ ( self, log = None, *args, **kwargs ):
        super ( widget_viewer_2d, self ).__init__ ( *args, **kwargs )
        self.setFloating ( True )
        if log:
            self.log = log
        else:
            self.log = print
        
    def set_image_ndarray ( self, image_ndarray = numpy.ndarray ):
        self.__image_ndarray = image_ndarray
        self.__image_qpixmap_list = self.generate_qpixmap_list ( image_ndarray )

    def select_slice ( self, slice_index = 0 ):
        self.__slice_index = slice_index
        self.__image_canvas = self.__image_qpixmap_list[self.__slice_index]

    def set_title ( self, title = str ):
        self.__title = title 

    def generate_qpixmap_list ( self, image_ndarray = numpy.ndarray ):
        qpixmap_list = []

        if len ( image_ndarray.shape ) == 2:
            qpixmap_list.append ( self.pack_ndarray_slice_into_qpixmap ( 
                image_height = image_ndarray.shape[0],
                image_width  = image_ndarray.shape[1],
                image_ndarray_slice = image_ndarray ) )

        if len ( image_ndarray.shape ) == 3:
            for slice_index in range ( image_ndarray.shape[0] ):
                self.log ( "Processing slice %s." % slice_index )
                qpixmap_list.append ( self.pack_ndarray_slice_into_qpixmap ( 
                    image_height = image_ndarray.shape[1],
                    image_width  = image_ndarray.shape[2],
                    image_ndarray_slice = image_ndarray[slice_index] ) )

        return qpixmap_list

    def pack_ndarray_slice_into_qpixmap ( self, image_height = None, image_width = None, image_ndarray_slice = None, colormap = None ):
        # Code refactored from http://nathanhorne.com/?p=500. Publicly available in 2014-12-18.
        canvas_2d = QPixmap ( image_width, image_height )
        converted_image_data = QImage ( image_width, image_height, QImage.Format_RGB32 )
        uchar_data = converted_image_data.bits ( )
        uchar_data.setsize ( converted_image_data.byteCount ( ) )
        i = 0
        for height in range ( image_height ):
            for width in range ( image_width ):
                gray = int ( image_ndarray_slice[height][width] )
                uchar_data[i:i+4] = struct.pack ('I', gray )
                i += 4
        canvas_2d.convertFromImage ( converted_image_data )
        return canvas_2d

    def display ( self ):
        self.__title_label = QLabel ( self.__title )
        self.__canvas_label = QLabel ( self )
        self.__canvas_label.setPixmap ( self.__image_canvas )

        self.__layout = QGridLayout ( )	
        self.__layout.addWidget ( self.__title_label )
        self.__layout.addWidget ( self.__canvas_label )

        self.__scroll_area = QScrollArea ( )
        self.__scroll_area.setBackgroundRole ( QPalette.Dark )
        self.__scroll_area.setLayout ( self.__layout )

        self.setWidget ( self.__scroll_area )

