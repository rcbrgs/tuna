"""
simple_gui is a standalone, minimal GUI for Tuna.

This module should be run a an app by end users that want a GUI frontend to Tuna tools and pipelines. 
Also, some facilities do not make sense outside of the standalone app, such as the pipeline editor.
"""

import numpy
import PyQt4.QtGui
from PyQt4.QtGui import QAction, QMainWindow
import PyQt4.QtCore
from PyQt4.QtCore import Qt
import astropy.io.fits

#import sys
#sys.path.append ( '/home/nix/cloud_essential2/tuna' )
#from github.zmq import zmq_client
from zeromq import zmq_client
from gui import widget_viewer_2d
from file_format import adhoc, fits
from tools.phase_map_creation import high_resolution_Fabry_Perot_phase_map_creation

class simple_gui ( QMainWindow ):
#    def __init__ ( self, tuna_log_client = None, desktop_widget = None ):
    def __init__ ( self, desktop_widget = None ):
        super ( simple_gui, self ).__init__ ( )
        self.__gui_zmq_client = zmq_client.zmq_client ( )
        self.logger = self.__gui_zmq_client.log
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
        action_create_phase_map = QAction ( '&Create phase map...', self )
        action_create_phase_map.setShortcut ( 'Ctrl+C' )
        action_create_phase_map.setStatusTip ( 'Starts the process of creating a phase map.' )
        action_create_phase_map.triggered.connect ( self.create_phase_map )
        
        # Menu
        bar_menu = self.menuBar ( ) 
        menu_file = bar_menu.addMenu ( '&File' )
        menu_file.addAction ( action_exit )
        menu_file.addAction ( action_open_file )
        # Toolbar
        self.toolbar = self.addToolBar ( "" )
        self.toolbar.addAction ( action_exit )
        self.toolbar.addAction ( action_open_file )
        self.toolbar.addAction ( action_create_phase_map )
        # Main window
        self.log ( 'Configuring main window.')
        self.background = PyQt4.QtGui.QLabel ( )
        self.setCentralWidget ( self.background )
        desktop_rect = self.desktop_widget.availableGeometry ( )
        self.log ( 'Desktop height = ' + str ( desktop_rect.height ( ) ) )
        self.log ( 'Desktop width  = ' + str ( desktop_rect.width ( ) ) )
        self.setGeometry ( 300, 300, 250,150 )
        self.setWindowTitle ( 'Tuna' )
        self.statusBar ( ).showMessage ( 'Waiting for command.' )
        self.show ( )
        # Toolboxes
        #self.instrument_calibration_toolbox = widget_toolbox.toolbox ( )
        #self.addDockWidget ( PyQt4.QtCore.Qt.LeftDockWidgetArea, self.instrument_calibration_toolbox )
        #self.phase_map_creation_toolbox = widget_toolbox.toolbox ( )
        #self.addDockWidget ( PyQt4.QtCore.Qt.LeftDockWidgetArea, self.instrument_calibration_toolbox )

    def log ( self, msg ):
        self.statusBar ( ) . showMessage ( msg )
        self.logger ( bytes ( msg, 'utf-8' ) )

    def open_file ( self ):
        self.log ( "Opening getOpenFileName dialog." )
        file_name = PyQt4.QtGui.QFileDialog.getOpenFileName ( self, 'Open file ...', '.', 'All known types (*.fits *.FITS *.ad2 *.AD2 *.ad3 *.AD3);;FITS files (*.fits *.FITS);;ADHOC files (*.ad2 *.AD2 *.ad3 *.AD3)' )
        self.log ( "File selected: %s." % file_name )

        fits_file = fits.fits ( file_name = file_name, log = self.log )
        fits_file.read ( )
        if fits_file.is_readable ( ):
            image_ndarray = fits_file.get_image_ndarray ( )
        else: 
            adhoc_file = adhoc.adhoc ( file_name = file_name, log = self.log )
            adhoc_file.read ( )
            if adhoc_file.is_readable ( ):
                image_ndarray = adhoc_file.get_image_ndarray ( )
            else:
                self.log ( "Unable to open file %s." % file_name )
                return

        image_viewer = widget_viewer_2d.widget_viewer_2d ( log = self.log )
        image_viewer.set_image_ndarray ( image_ndarray )
        image_viewer.select_slice ( 0 )
        image_viewer.set_title ( file_name )
        image_viewer.display ( )
        self.addDockWidget ( Qt.LeftDockWidgetArea, image_viewer )

    def register_image_widget ( self, cache_key_string ):
        self.open_images_list.append ( cache_key_string )
        self.log ( "Image opened. Current list of QPixmap.cacheKey's:" )
        self.log ( str ( self.open_images_list ) )

    def deregister_image_widget ( self, cache_key_string ):
        self.open_images_list.remove ( cache_key_string )
        self.log ( "Image opened. Current list of QPixmap.cacheKey's:" )
        self.log ( str ( self.open_images_list ) )

    def create_phase_map ( self ):
        self.log ( "Opening getOpenFileName dialog." )
        file_name = PyQt4.QtGui.QFileDialog.getOpenFileName ( self, 'Open file ...', '.', 'All known types (*.fits *.FITS *.ad2 *.AD2 *.ad3 *.AD3);;FITS files (*.fits *.FITS);;ADHOC files (*.ad2 *.AD2 *.ad3 *.AD3)' )
        self.log ( "File selected: %s." % file_name )
        self.phase_map_tool = high_resolution_Fabry_Perot_phase_map_creation.high_resolution_Fabry_Perot_phase_map_creation ( file_name = file_name, log = self.log )
        self.phase_map = self.phase_map_tool.get_image_ndarray ( )
        self.image_viewer = widget_viewer_2d.widget_viewer_2d ( log = self.log )
        self.image_viewer.opened.connect ( self.register_image_widget )
        self.image_viewer.closed.connect ( self.deregister_image_widget )
        self.image_viewer.set_image_ndarray ( self.phase_map )
        self.image_viewer.select_slice ( 0 )
        self.image_viewer.set_title ( file_name )
        self.image_viewer.display ( )
        self.addDockWidget ( Qt.LeftDockWidgetArea, self.image_viewer )

def main ( ):
    app = PyQt4.QtGui.QApplication ( sys.argv )
    main_widget = simple_gui ( tuna_log, app.desktop ( ) )
    sys.exit ( app.exec_ ( ) )

if __name__ == "__main__":
    main ( )
