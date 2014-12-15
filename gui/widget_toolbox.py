from PyQt4.QtGui import QDockWidget, QGridLayout, QPushButton, QWidget
from sys import path
path.append ( '/home/sync/tuna' )
from github.gui import widget_tool

class toolbox ( QDockWidget ):
    def __init__ ( self, *args, **kwargs ):
        self.hbox_layout = QGridLayout ( )
        self.master_bias_calculate_button = QPushButton ( "Calculate master bias" )
        self.hbox_layout.addWidget ( self.master_bias_calculate_button )
        self.canvas = QWidget ( )
        self.canvas.setLayout ( self.hbox_layout )
        super ( toolbox, self ).__init__ ( *args, **kwargs )
        self.setFloating ( True )
        self.setWidget ( self.canvas )
