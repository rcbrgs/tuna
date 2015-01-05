"""
widget_viewer_3d displays 3d images in a dock.
"""

#from OpenGL.GL import *
from PyQt4.QtGui import ( QDockWidget,
                          QGLContext )
from PyQt4.QtCore import ( pyqtSignal )

class widget_viewer_3d ( QDockWidget ):
    opened = pyqtSignal ( str )
    closed = pyqtSignal ( str )
    def __init__ ( self, *args, **kwargs ):
        super ( widget_viewer_2d, self ).__init__ ( *args, **kwargs )
        self.setFloating ( True )
        
#    def set_QPixmap ( self, image_pixmap = PyQt4.QtGui.QPixmap ):
#        self.image_canvas = image_pixmap
#        self.canvas_label = PyQt4.QtGui.QLabel ( self )
#        self.canvas_label.setPixmap ( self.image_canvas )
#        self.setWidget ( self.canvas_label )
#        self.opened.emit ( str ( self.image_canvas.cacheKey ( ) ) )

    def set_QGLContext ( self, volume_context = QGLContext ):
        pass

    def closeEvent ( self, event ):
        self.closed.emit ( str ( self.image_canvas.cacheKey ( ) ) )
        super ( widget_viewer_2d, self ).closeEvent ( event )
