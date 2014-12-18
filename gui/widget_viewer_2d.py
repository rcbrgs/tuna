"""
widget_viewer_2d displays 2d images in a dock.

It is composed of a QDockWidget that displays a QPixMap. Eventually, more image-related functions will be added here.
"""

from PyQt4.QtGui import QDockWidget, QGridLayout, QLabel, QPalette, QPixmap, QScrollArea
from PyQt4.QtCore import pyqtSignal, QSize

class widget_viewer_2d ( QDockWidget ):
    opened = pyqtSignal ( str )
    closed = pyqtSignal ( str )
    def __init__ ( self, *args, **kwargs ):
        super ( widget_viewer_2d, self ).__init__ ( *args, **kwargs )
        self.setFloating ( True )
        
    def set_QPixmap ( self, image_pixmap = QPixmap ):
        self.__image_canvas = image_pixmap
        self.opened.emit ( str ( self.__image_canvas.cacheKey ( ) ) )

    def set_title ( self, title = str ):
        self.__title = title 

    def display ( self ):
        self.__title_label = QLabel ( self.__title )
        self.__canvas_label = QLabel ( self )
        self.__canvas_label.setPixmap ( self.__image_canvas )

        self.__layout = QGridLayout ( )	
        self.__layout.addWidget ( self.__title_label )
        self.__layout.addWidget ( self.__canvas_label )

        self.__scroll_area = QScrollArea ( )
        self.__scroll_area.setBackgroundRole ( QPalette.Dark )
        #self.__scroll_area.setWidget ( self.__canvas_label )
        self.__scroll_area.setLayout ( self.__layout )

        self.setWidget ( self.__scroll_area )

    def closeEvent ( self, event ):
        self.closed.emit ( str ( self.__image_canvas.cacheKey ( ) ) )
        super ( widget_viewer_2d, self ).closeEvent ( event )

    #def sizeHint ( self ):
    #    if self.__scroll_area:
    #        height = self.__title_label.sizeHint ( ).height ( ) + self.__canvas_label.sizeHint ( ).height ( )
    #        width  = self.__title_label.sizeHint ( ).width  ( ) + self.__canvas_label.sizeHint ( ).width  ( )
    #        return QSize ( width, height )
