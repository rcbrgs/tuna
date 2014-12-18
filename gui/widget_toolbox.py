from PyQt4.QtGui import QDockWidget, QGridLayout, QPushButton, QWidget
from sys import path
path.append ( '/home/sync/tuna' )
from github.gui import widget_tool

class toolbox ( QDockWidget ):
    def __init__ ( self, *args, **kwargs ):
        super ( toolbox, self ).__init__ ( *args, **kwargs )
        self.setFloating ( True )
        self.canvas = QWidget ( )
        self.hbox_layout = QGridLayout ( )
        self.__tools_list = [ ]

    def add_tool ( self, tool = widget_tool, *args, **kwargs ):
        self.__tools_list.append ( tool )
        self.__refresh ( )

    def __refresh ( self ):
        self.hobx_layout
        for tool in self.__tools_list:
            self.hbox_layout.addWidget ( tool.get_widget ( ) )

        self.canvas.setLayout ( self.hbox_layout )
        self.setWidget ( self.canvas )
