"""
This subpackage contains Tuna's file format namespace, io. Its scope is to collect modules that are mainly concerned with file formats, storage and metadata.
"""

from .adhoc           import adhoc
from .adhoc_ada       import ada
from .can             import can
from .convenience     import ( read,
                               write )
from .database        import database
from .file_reader     import file_reader
from .fits            import fits
from .lock            import lock
from .metadata_parser import ( metadata_parser, 
                               get_metadata )
from tuna.io.system   import status
