#!/usr/bin/env python3

"""tuna_viewer_2d docstring
Basic viewer widget for 2d images. As standalone, minimal GUI for opening FITS files.
"""

import sys
sys.path.append ( '/home/nix/cloud_essential2/temp/btfi/tuna2/tuna_logging' )
import tuna_logging

import PyQt4.QtGui
import PyQt4.QtCore


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
        action_open_file.triggered.connect ( self.show_open_file_dialog )
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

    def show_open_file_dialog ( self ):
        self.log ( "Opening getOpenFileName dialog." )
        file_name = PyQt4.QtGui.QFileDialog.getOpenFileName ( self, 'Open file ...', '.', 'FITS files (*.fits *.FITS);;ADHOC files (*.ad2 *.AD2)' )
        self.log ( "File selected: %s." % file_name )


def main ( ):
    tuna_log = tuna_logging.tuna_log_client ( )
    log = tuna_log.log

    app = PyQt4.QtGui.QApplication ( sys.argv )
    main_widget = tuna_viewer_2d ( tuna_log )
    log ( b"Entering PyQt4 app.exec_ loop." )
    sys.exit ( app.exec_ ( ) )
    log ( b"Exited PyQt4 app.exec_ loop." )

if __name__ == "__main__":
    main ( )
