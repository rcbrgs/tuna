"""
simple_gui is a standalone, minimal GUI for Tuna.

This module should be run a an app by end users that want a GUI frontend to Tuna tools and pipelines. 
Also, some facilities do not make sense outside of the standalone app, such as the pipeline editor.
"""

import PyQt4.QtGui
import PyQt4.QtCore
import astropy.io.fits

import sys
sys.path.append ( '/home/nix/cloud_essential2/tuna' )
from github.zmq import zmq_client
from github.gui import widget_toolbox, widget_viewer_2d
from github.file_formats import adhoc

class tuna_viewer_2d ( PyQt4.QtGui.QMainWindow ):
    def __init__ ( self, tuna_log_client, desktop_widget ):
        super ( tuna_viewer_2d, self ).__init__ ( )
        self.logger = tuna_log_client.log
        self.desktop_widget = desktop_widget
        self.open_images_list = [ ]
        self.init_gui ( )

    def init_gui ( self ):
        """
        Create initial GUI elements and display them.
        """
        self.log ( 'Creating GUI elements.' )
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
        self.background = PyQt4.QtGui.QLabel ( )
        self.setCentralWidget ( self.background )
        self.log ( 'Configuring main window.')
        desktop_rect = self.desktop_widget.availableGeometry ( )
        self.log ( 'Desktop height = ' + str ( desktop_rect.height ( ) ) )
        self.log ( 'Desktop width  = ' + str ( desktop_rect.width ( ) ) )
        self.setGeometry ( 300, 300, 250,150 )
        self.setWindowTitle ( 'Tuna' )
        self.statusBar ( ).showMessage ( 'Waiting for command.' )
        self.show ( )
        # Toolboxes
        self.instrument_calibration_toolbox = widget_toolbox.toolbox ( )
        self.addDockWidget ( PyQt4.QtCore.Qt.LeftDockWidgetArea, self.instrument_calibration_toolbox )

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
            image_height = hdu_list[0].header['NAXIS1']
            image_width = hdu_list[0].header['NAXIS2']
            image_data = hdu_list[0].data
        except IOError:
            self.log ( "Could not open file as FITS file." )
            adhoc_file = adhoc.adhoc ( file_name = file_name )
            adhoc_file.read ( )
            image_data = adhoc_file.get_data ( )
            image_slices = image_data.shape[0]
            image_height = image_data.shape[1]
            image_width = image_data.shape[2]

        self.log ( "Image height = %d." % image_height )
        self.log ( "Image width = %d." % image_width )
        self.canvas_2d = PyQt4.QtGui.QPixmap ( image_width, image_height )
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
        self.canvas_2d.convertFromImage ( converted_image_data )
        self.image_viewer = widget_viewer_2d.widget_viewer_2d ( )
        self.image_viewer.opened.connect ( self.register_image_widget )
        self.image_viewer.closed.connect ( self.deregister_image_widget )
        self.image_viewer.set_QPixmap ( self.canvas_2d )
        self.addDockWidget ( PyQt4.QtCore.Qt.LeftDockWidgetArea, self.image_viewer )

    def register_image_widget ( self, cache_key_string ):
        self.open_images_list.append ( cache_key_string )
        self.log ( "Image opened. Current list of QPixmap.cacheKey's:" )
        self.log ( str ( self.open_images_list ) )

    def deregister_image_widget ( self, cache_key_string ):
        self.open_images_list.remove ( cache_key_string )
        self.log ( "Image opened. Current list of QPixmap.cacheKey's:" )
        self.log ( str ( self.open_images_list ) )

def main ( ):
    tuna_log = zmq_client.zmq_client ( )
    app = PyQt4.QtGui.QApplication ( sys.argv )
    main_widget = tuna_viewer_2d ( tuna_log, app.desktop ( ) )
    sys.exit ( app.exec_ ( ) )

if __name__ == "__main__":
    main ( )
