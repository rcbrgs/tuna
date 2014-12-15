"""
widget_viewer_2d displays 2d images in a dock.

It is composed of a QDockWidget that displays a QPixMap. Eventually, more image-related functions will be added here.
"""

import PyQt4.QtGui
import PyQt4.QtCore

class widget_viewer_2d ( PyQt4.QtGui.QDockWidget ):
    def __init__ ( self, image_pixmap=PyQt4.QtGui.QPixmap, *args, **kwargs ):
        self.image_canvas = image_pixmap
        super ( widget_viewer_2d, self ).__init__ ( *args, **kwargs )
        self.canvas_label = PyQt4.QtGui.QLabel ( self )
        self.canvas_label.setPixmap ( self.image_canvas )
        self.setWidget ( self.canvas_label )
        self.setFloating ( True )
        #self.setAllowedAreas ( PyQt4.QtCore.Qt.LeftDockWidgetArea )
        #self.show ( )
