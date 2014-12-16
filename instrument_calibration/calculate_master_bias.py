from astropy.io import fits
from PyQt4.QtGui import QImage, QPixmap
import struct

class calculate_master_bias ( object ):
    def __init__ ( self, file_name = str, *args, **kwargs ):
        self.file_name = file_name
        super ( calculate_master_bias, self ).__init__ ( *args, **kwargs )
        self.run ( )
        
    def run ( self ):
        try:
            hdu_list = fits.open ( file_name )
            #self.log ( "File opened as a FITS file." )
            image_height = hdu_list[0].header['NAXIS1']
            image_width = hdu_list[0].header['NAXIS2']
            #self.log ( "Image height = %d." % image_height )
            #self.log ( "Image width = %d." % image_width )
            image_data = hdu_list[0].data
            

            self.canvas_2d = QPixmap ( image_width, image_height )
            #self.log ( "QPixmap depth = %d" % self.canvas_2d.depth ( ) )
            #http://nathanhorne.com/?p=500
            converted_image_data = QImage ( image_width, image_height, QImage.Format_RGB32 )
            uchar_data = converted_image_data.bits ( )
            uchar_data.setsize ( converted_image_data.byteCount ( ) )
            i = 0
            for height in range ( image_height ):
                for width in range ( image_width ):
                    gray = int ( image_data [height][width] )
                    uchar_data[i:i+4] = struct.pack ('I', gray )
                    i += 4
            self.canvas_2d.convertFromImage ( converted_image_data )
            
            #self.image_viewer = widget_viewer_2d.widget_viewer_2d ( )
            #self.image_viewer.opened.connect ( self.register_image_widget )
            #self.image_viewer.closed.connect ( self.deregister_image_widget )
            #self.image_viewer.set_QPixmap ( self.canvas_2d )
            #self.addDockWidget ( PyQt4.QtCore.Qt.LeftDockWidgetArea, self.image_viewer )
        except IOError:
            #self.log ( "Could not open file as FITS file." )
            pass
