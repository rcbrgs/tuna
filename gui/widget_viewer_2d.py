"""
widget_viewer_2d displays 2d images in a dock.

It is composed of a QDockWidget that displays a QPixMap. Eventually, more image-related functions will be added here.
"""

import PyQt4.QtGui
import PyQt4.QtCore

class widget_viewer_2d ( PyQt4.QtGui.QDockWidget ):
    opened = PyQt4.QtCore.pyqtSignal ( str )
    closed = PyQt4.QtCore.pyqtSignal ( str )
    def __init__ ( self, *args, **kwargs ):
        super ( widget_viewer_2d, self ).__init__ ( *args, **kwargs )
        self.setFloating ( True )
        
    def set_QPixmap ( self, image_pixmap = PyQt4.QtGui.QPixmap ):
        self.image_canvas = image_pixmap
        self.canvas_label = PyQt4.QtGui.QLabel ( self )
        self.canvas_label.setPixmap ( self.image_canvas )
        self.setWidget ( self.canvas_label )
        self.opened.emit ( str ( self.image_canvas.cacheKey ( ) ) )

    def closeEvent ( self, event ):
        self.closed.emit ( str ( self.image_canvas.cacheKey ( ) ) )
        super ( widget_viewer_2d, self ).closeEvent ( event )
