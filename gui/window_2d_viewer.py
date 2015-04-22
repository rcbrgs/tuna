"""
window_2d_viewer.py

A standalone, minimal viewer for 2d images.
"""

import numpy
import PyQt4.QtGui
from PyQt4.QtGui import QAction, QMainWindow
import PyQt4.QtCore
from PyQt4.QtCore import Qt
import sys
import threading
from tuna.zeromq import zmq_client
from tuna.gui import widget_viewer_2d
from tuna.io import adhoc, fits
import tuna

class window_2d_viewer ( threading.Thread ):
    def __init__ ( self, 
                   log = print,
                   array = numpy.ndarray ):
        super ( window_2d_viewer, self ).__init__ ( )
        self.log = log
        self.array = array

    def run ( self ):
        self.app = PyQt4.QtGui.QApplication ( sys.argv )
        self.main_widget = window_2d_viewer_gui ( log = self.log, 
                                                  desktop_widget = self.app.desktop ( ), 
                                                  array = self.array )
        sys.exit ( self.app.exec_ ( ) )

    def update ( self,
                 o_data = numpy.ndarray ):
        self.main_widget.update_data ( o_data = o_data )
        
class window_2d_viewer_gui ( QMainWindow ):
    def __init__ ( self, 
                   desktop_widget = None, 
                   array = numpy.ndarray, 
                   log = None ):
        super ( window_2d_viewer_gui, self ).__init__ ( )
        if log == None:
            self.log = print
        else:
            self.log = log

        self.array = array

        self.__gui_zmq_client = tuna.zeromq.zmq_client ( )
        self.logger = self.__gui_zmq_client.log
        self.desktop_widget = desktop_widget
        self.open_images_list = [ ]
        self.init_gui ( )

        self.image_viewer = widget_viewer_2d.widget_viewer_2d ( log = self.log )
        self.image_viewer.set_image_ndarray ( array )
        self.image_viewer.select_slice ( 0 )
        file_name = ""
        self.image_viewer.set_title ( file_name )
        self.image_viewer.display ( )
        self.addDockWidget ( Qt.LeftDockWidgetArea, 
                             self.image_viewer )

    def init_gui ( self ):
        """
        Create initial GUI elements and display them.
        """
        self.log ( 'debug: Creating GUI elements.' )
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
        self.toolbar = self.addToolBar ( "" )
        self.toolbar.addAction ( action_exit )
        self.toolbar.addAction ( action_open_file )
        # Main window
        self.log ( 'debug: Configuring main window.')
        self.background = PyQt4.QtGui.QLabel ( )
        self.setCentralWidget ( self.background )
        desktop_rect = self.desktop_widget.availableGeometry ( )
        self.log ( 'debug: Desktop height = ' + str ( desktop_rect.height ( ) ) )
        self.log ( 'debug: Desktop width  = ' + str ( desktop_rect.width ( ) ) )
        self.log ( "debug: Image width = %d" % self.array.shape [ 1 ] )
        self.log ( "debug: Image height = %d" % self.array.shape [ 0 ] )
        self.setGeometry ( 300, 300, self.array.shape [ 1 ] + 100, self.array.shape [ 0 ] + 150 )
        self.setWindowTitle ( 'Tuna' )
        self.statusBar ( ).showMessage ( 'Waiting for command.' )
        self.show ( )

    def log ( self, msg ):
        self.statusBar ( ) . showMessage ( msg )
        self.logger ( bytes ( msg, 'utf-8' ) )

    def open_file ( self ):
        self.log ( "debug: Opening getOpenFileName dialog." )
        file_name = PyQt4.QtGui.QFileDialog.getOpenFileName ( self, 'Open file ...', '.', 'All known types (*.fits *.FITS *.ad2 *.AD2 *.ad3 *.AD3);;FITS files (*.fits *.FITS);;ADHOC files (*.ad2 *.AD2 *.ad3 *.AD3)' )
        self.log ( "info: File selected: %s." % file_name )

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
                self.log ( "warning: Unable to open file %s." % file_name )
                return

        image_viewer = widget_viewer_2d.widget_viewer_2d ( log = self.log )
        image_viewer.set_image_ndarray ( image_ndarray )
        image_viewer.select_slice ( 0 )
        image_viewer.set_title ( file_name )
        image_viewer.display ( )
        self.addDockWidget ( Qt.LeftDockWidgetArea, image_viewer )

    def register_image_widget ( self, cache_key_string ):
        self.open_images_list.append ( cache_key_string )
        self.log ( "debug: Image opened. Current list of QPixmap.cacheKey's:" )
        self.log ( "debug: %s" % str ( self.open_images_list ) )

    def deregister_image_widget ( self, cache_key_string ):
        self.open_images_list.remove ( cache_key_string )
        self.log ( "debug: Image opened. Current list of QPixmap.cacheKey's:" )
        self.log ( "debug: %s" % str ( self.open_images_list ) )

    def create_phase_map ( self ):
        self.log ( "debug: Opening getOpenFileName dialog." )
        file_name = PyQt4.QtGui.QFileDialog.getOpenFileName ( self, 'Open file ...', '.', 'All known types (*.fits *.FITS *.ad2 *.AD2 *.ad3 *.AD3);;FITS files (*.fits *.FITS);;ADHOC files (*.ad2 *.AD2 *.ad3 *.AD3)' )
        self.log ( "info: File selected: %s." % file_name )
        self.phase_map_tool = high_resolution_Fabry_Perot_phase_map_creation.high_resolution_Fabry_Perot_phase_map_creation ( file_name = file_name, log = self.log )
        self.phase_map = self.phase_map_tool.get_image_ndarray ( )
        #self.image_viewer = widget_viewer_2d.widget_viewer_2d ( log = self.log )
        self.image_viewer = widget_viewer_3d.widget_viewer_3d ( log = self.log, image_ndarray = self.phase_map )
        self.image_viewer.opened.connect ( self.register_image_widget )
        self.image_viewer.closed.connect ( self.deregister_image_widget )
        #self.image_viewer.set_image_ndarray ( self.phase_map )
        #self.image_viewer.select_slice ( 0 )
        self.image_viewer.set_title ( file_name )
        self.image_viewer.display ( )
        self.addDockWidget ( Qt.LeftDockWidgetArea, self.image_viewer )

    def update_data ( self,
                      o_data = numpy.ndarray ):
        self.image_viewer.set_image_ndarray ( o_data )
