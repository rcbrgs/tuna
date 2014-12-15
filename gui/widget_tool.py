from PyQt4.QtGui import QPushButton, QWidget

class tuna_tool ( QWidget ):
    def __init__ ( self, name = str, *args, **kwargs ):
        self.button = QPushButton ( text = name )
        super ( tuna_tool, self).__init__ ( *args, **kwargs )
