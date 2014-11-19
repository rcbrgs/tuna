#!/usr/bin/env python3

"""tuna_viewer_2d docstring
Basic viewer widget for 2d images. As standalone, minimal GUI for opening FITS files.
"""

import sys
sys.path.append ( '/home/nix/cloud_essential2/temp/btfi/tuna2/tuna_logging' )

import tuna_logging

def main ( ):
    tuna_log = tuna_logging.tuna_log_client ( )
    log = tuna_log.log
    #log ( b'test' )

if __name__ == "__main__":
    main ( )
