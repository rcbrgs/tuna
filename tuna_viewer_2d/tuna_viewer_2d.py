#!/usr/bin/env python3

"""tuna_viewer_2d docstring
Basic viewer widget for 2d images. As standalone, minimal GUI for opening FITS files.
"""

import sys
sys.path.append ( '/home/nix/cloud_essential2/temp/btfi/tuna2/tuna_logging' )
import tuna_logging

#from PyQt4 import QtGui
import PyQt4.QtGui

def main ( ):
    tuna_log = tuna_logging.tuna_log_client ( )
    log = tuna_log.log

    app = PyQt4.QtGui.QApplication ( sys.argv )
    w = PyQt4.QtGui.QWidget ( )
    w.resize ( 250, 150 )
    w.move ( 300, 300 )
    w.setWindowTitle ( 'Simple' )
    w.show ( )
    sys.exit ( app.exec_ ( ) )

if __name__ == "__main__":
    main ( )
