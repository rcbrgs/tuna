"""
tuna_viewer_2d docstring

Basic viewer widget for 2d images. As standalone, minimal GUI for opening FITS files.
"""

import PyQt4.QtGui
import PyQt4.QtCore
import astropy.io.fits

import sys
sys.path.append ( '/home/nix/cloud_essential2/tuna' )
#import github.zmq.zmq_client
from github.zmq import zmq_client
#from ..zmq import zmq_client

class tuna_viewer_2d ( PyQt4.QtGui.QMainWindow ):
    def __init__ ( self, tuna_log_client ):
        super ( tuna_viewer_2d, self ).__init__ ( )
        self.logger = tuna_log_client.log
        self.init_gui ( )

    def init_gui ( self ):
        self.log ( 'Creating GUI elements.' )
        # Main window buttons
        #button_exit = PyQt4.QtGui.QPushButton ( 'Exit', self )
        #button_exit.clicked.connect ( PyQt4.QtCore.QCoreApplication.instance ( ).quit )
        #button_exit.resize ( button_exit.sizeHint ( ) )
        #button_exit.move ( 50, 50 )
        #button_exit.setToolTip ( 'Exits the program immediately.' )
        # Actions
        action_exit = PyQt4.QtGui.QAction ('&Exit', self )
        action_exit.setShortcut ( 'Ctrl+Q' )
        action_exit.setStatusTip ( 'Exits the program immediately.' )
        action_exit.triggered.connect ( PyQt4.QtCore.QCoreApplication.instance ( ).quit )
        action_open_file = PyQt4.QtGui.QAction ( '&Open file ...', self )
        action_open_file.setShortcut ( 'Ctrl+O' )
        action_open_file.setStatusTip ( 'Starts the process of selecting a file to be opened.' )
        action_open_file.triggered.connect ( self.open_file )
        # Menu
        bar_menu = self.menuBar ( ) 
        menu_file = bar_menu.addMenu ( '&File' )
        menu_file.addAction ( action_exit )
        menu_file.addAction ( action_open_file )
        # Toolbar
        self.toolbar = self.addToolBar ( 'Exit' )
        self.toolbar.addAction ( action_exit )
        # Main window
        self.log ( 'Configuring main window.')
        self.setGeometry ( 300, 300, 250,150 )
        self.setWindowTitle ( 'Tuna 2D Viewer' )
        self.statusBar ( ).showMessage ( 'Waiting for command.' )
        self.show ( )

    def log ( self, msg ):
        self.statusBar ( ) . showMessage ( msg )
        self.logger ( bytes ( msg, 'utf-8' ) )

    def open_file ( self ):
        self.log ( "Opening getOpenFileName dialog." )
        file_name = PyQt4.QtGui.QFileDialog.getOpenFileName ( self, 'Open file ...', '.', 'FITS files (*.fits *.FITS);;ADHOC files (*.ad2 *.AD2)' )
        self.log ( "File selected: %s." % file_name )
        try:
            hdu_list = astropy.io.fits.open ( file_name )
            self.log ( "File opened as a FITS file." )
            hdu_list.info ( )
            print ( hdu_list[0].header )
            image_height = hdu_list[0].header['NAXIS1']
            image_width = hdu_list[0].header['NAXIS2']
            self.log ( "Image height = %d." % image_height )
            self.log ( "Image width = %d." % image_width )
            image_data = hdu_list[0].data
            self.canvas_2d = PyQt4.QtGui.QPixmap ( image_width, image_width )
            self.log ( "QPixmap depth = %d" % self.canvas_2d.depth ( ) )
            #http://nathanhorne.com/?p=500
            converted_image_data = PyQt4.QtGui.QImage ( image_width, image_height, PyQt4.QtGui.QImage.Format_RGB32 )
            import struct
            uchar_data = converted_image_data.bits ( )
            uchar_data.setsize ( converted_image_data.byteCount ( ) )
            i = 0
            for height in range ( image_height ):
                for width in range ( image_width ):
                    gray = int ( image_data [height][width] )
                    uchar_data[i:i+4] = struct.pack ('I', gray )
                    i += 4
            #converted_image_data = []
            #for item in image_data:
            #    for subitem in item:
            #        converted_image_data.append ( int ( subitem ) )
            #        self.canvas_2d.loadFromData ( bytearray ( converted_image_data ), image_width * image_height )
            self.canvas_2d.convertFromImage ( converted_image_data )
            self.canvas_2d_label = PyQt4.QtGui.QLabel ( self )
            self.canvas_2d_label.setPixmap ( self.canvas_2d )         
            self.setCentralWidget ( self.canvas_2d_label )
        except IOError:
            self.log ( "Could not open file as FITS file." )

def main ( ):
    tuna_log = zmq_client.zmq_client ( )
    app = PyQt4.QtGui.QApplication ( sys.argv )
    main_widget = tuna_viewer_2d ( tuna_log )
    sys.exit ( app.exec_ ( ) )

if __name__ == "__main__":
    main ( )
