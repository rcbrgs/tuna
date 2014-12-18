import numpy
from PyQt4.QtGui import QImage, QPixmap
import struct

class file_format ( object ):
    def convert_from_ndarray_into_QPixmap_list ( self, image_ndarray = numpy.ndarray ):
        QPixmap_list = []

        if len ( image_ndarray.shape ) == 2:
            QPixmap_list.append ( self.pack_ndarray_slice_into_QPixmap ( 
                image_height = image_ndarray.shape[0],
                image_width  = image_ndarray.shape[1],
                image_ndarray_slice = image_ndarray ) )

        if len ( image_ndarray.shape ) == 3:
            for slice_index in range ( image_ndarray.shape[0] ):
                QPixmap_list.append ( self.pack_ndarray_slice_into_QPixmap ( 
                    image_height = image_ndarray.shape[1],
                    image_width  = image_ndarray.shape[2],
                    image_ndarray_slice = image_ndarray[slice_index] ) )

        return QPixmap_list

    def pack_ndarray_slice_into_QPixmap ( self, image_height = None, image_width = None, image_ndarray_slice = None ):
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
