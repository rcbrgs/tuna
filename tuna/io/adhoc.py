# -*- coding: utf-8 -*-
"""
This module scope coves ADHOC files' operations. 

ADHOC files typically have the .AD2 (for two-dimensional data) and .AD3 (for tri-dimensional data).

It is based on a module provided by Benoît Epinat, and integrated into Tuna in 2015.
"""

import logging
import os
import numpy
import numpy as np
import pyfits as pf
from pyfits import Column
import sys
from time import sleep

from .file_reader import file_reader
import tuna

#verifier l'organisation des cubes fits si on les ouvre en python
#faire un programme readad qui voit l'extension pour savoir comment ouvir (soit ad2, ad3, ad1...)
#gestion des NaN a inclure (input/output)!!!

class adhoc ( file_reader ):
    """
    This class' responsibilities include: reading files in one of the ADHOC file formats (AD2 or AD3).

    First implemented by Benoit Epinat from LAM.
    The ADHOC file formats were developed for use with the ADHOC software solution, developed at LAM by Jacques Boulesteix.

    It inherits from :ref:`tuna_io_file_reader_label`.

    Its constructor has the following signature:

    Parameters:

    * adhoc_type : int : defaults to None.
        Valid types are 2 and 3.

    * adhoc_trailer : numpy.ndarray : defaults to None.
        The trailer of an ADHOC file are the last 256 bytes of the file, and contain metadata.

    * file_name : string : defaults to None.
        Must correspond to an existing ADHOC file.

    * array : numpy.ndarray : defaults to None.
        Will be read from the file, and its size is the file size minus 256 bytes, and each field has 32 bytes and is encoded as a float.

    Example usage::

        import tuna
        raw = tuna.io.adhoc ( file_name = "tuna/tuna/test/unit/unit_io/adhoc.ad3" )
        raw.read ( )
        raw.get_array ( )
        raw.get_trailer ( )
    """

    def __init__ ( self, 
                   adhoc_type = None, 
                   adhoc_trailer = None, 
                   file_name = None, 
                   array = None ):
        super ( adhoc, self ).__init__ ( )
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )
        self.__version__ = "0.2.0"
        self.changelog = {
            '0.2.0' : "Tuna 0.14.0 : improved docstrings.",
            '0.1.2' : "Documentation: module, class and function docstrings.", 
            '0.1.1' : "Improved docstrings.",
            '0.1.0' : "Initial changelog."
            }

        self.__adhoc_type = adhoc_type
        self.__adhoc_trailer = adhoc_trailer
        self.__file_name = file_name
        self.__array = array
        self.__file_object = None

    def _discover_adhoc_type ( self ):
        """
        This method's goal is to open the file named file_name, get the first 256 bytes as its trailer, and cast its remaining contents into a numpy array of numpy.float32 values.
        Since the trailer contains information regarding the dimensionality of the data, this information is also retrieved from the file.
        """
        self.log.debug ( tuna.log.function_header ( ) )

        if self.__file_name:

            try:
                self.__file_object = open ( self.__file_name, "rb" )
            except OSError as e:
                self.log.error ( "OSError: %s" % str ( e ) )
                raise

            self.__file_object.seek ( 0, os.SEEK_END )
            if self.__file_object.tell ( ) < 256:
                self.log.error ( "File does not contain valid numpy array." )
                self.__adhoc_type = None
                return
            self.__array_size = int ( ( self.__file_object.tell ( ) - 256 ) / 4 )
            self.__file_object.close ( )

            try: 
                adhoc_file_type = numpy.dtype ( [ ( 'image_data', numpy.float32, self.__array_size ),
                                                  ( 'trailer', 
                                                    [ ( 'number_of_dimensions', numpy.int32, 1 ),
                                                      ( 'parameters', numpy.int8, 252 ) ] ) ] )
            except ValueError as e:
                self.log.error ( "ValueError: %s." % str ( e ) )
                self.log.warning ( "Impossible to guess adhoc type from file." )
                self.__adhoc_type = None
                return

            adhoc_file = numpy.fromfile ( self.__file_name, dtype = adhoc_file_type )
            if adhoc_file['trailer']['number_of_dimensions'] not in ( [2], [3], [-3] ):
                self.log.warning ( "Unrecognized number of dimensions in file %s." % str ( self.__file_name ) )
                return
            self.__adhoc_type = adhoc_file['trailer']['number_of_dimensions'][0]            

    def get_array ( self ):
        """
        This method's goal is to return the current value of the data array.

        Returns:

        * self.__array : numpy.ndarray
            Containing the current data array.
        """
        return self.__array

    def read ( self ):
        """
        This method's goal is to discover the ADHOC type (which corresponds to the data array dimensionality), and when possible call the appropriate method to read its contents.
        """
        self.log.debug ( tuna.log.function_header ( ) )

        if self.__file_name == None:
            self.log.error ( "No file name selected, aborting read operation." )
            return

        if self.__adhoc_type == None:
            self._discover_adhoc_type ( )
            if self.__adhoc_type == None:
                self._is_readable = False
                return
            else:
                self._is_readable = True

        if self.__file_object:
            self.__file_object.close ( )

        self.__file_object = open ( self.__file_name, "rb" )

        if self.__array_size == None:
            self.__array_size = ( self.__file_object.tell ( ) - 256 ) / 4  

        if self.__adhoc_type == 2:
            self._read_adhoc_2d ( )

        if self.__adhoc_type == 3 or self.__adhoc_type == -3:
            self._read_adhoc_3d ( )

    def _read_adhoc_2d ( self ):
        """
        This method's goal is to read the contents of self.__file_object as a 2D ADHOC file.
        """
        self.log.debug ( tuna.log.function_header ( ) )

        adhoc_2d_file_type = numpy.dtype ( [ ( 'data', np.float32, self.__array_size ), 
                                             ( 'trailer', 
                                               [ ( 'nbdim', np.int32 ), 
                                                 ( 'id', np.int8, 8 ), 
                                                 ( 'lx', np.int32 ), 
                                                 ( 'ly', np.int32 ), 
                                                 ( 'lz', np.int32 ), 
                                                 ( 'scale', np.float32 ), 
                                                 ( 'ix0', np.int32 ), 
                                                 ( 'iy0', np.int32 ), 
                                                 ( 'zoom', np.float32 ), 
                                                 ( 'modevis', np.int32 ), 
                                                 ( 'thrshld', np.float32 ), 
                                                 ( 'step', np.float32 ), 
                                                 ( 'nbiso', np.int32 ), 
                                                 ( 'pal', np.int32 ), 
                                                 ( 'cdelt1', np.float64 ), 
                                                 ( 'cdelt2', np.float64 ), 
                                                 ( 'crval1', np.float64 ), 
                                                 ( 'crval2', np.float64 ), 
                                                 ( 'crpix1', np.float32 ), 
                                                 ( 'crpix2', np.float32 ), 
                                                 ( 'crota2', np.float32 ), 
                                                 ( 'equinox', np.float32 ), 
                                                 ( 'x_mirror', np.int8 ), 
                                                 ( 'y_mirror', np.int8 ), 
                                                 ( 'was_compressed', np.int8 ), 
                                                 ( 'none2', np.int8, 1 ), 
                                                 ( 'none', np.int32, 4 ),
                                                 ( 'comment', np.int8, 128 ) ] ) ] )
        
        numpy_data = numpy.fromfile ( self.__file_name, dtype = adhoc_2d_file_type )
        
        if ( numpy_data['trailer']['lx'] >= 32768 ) |  ( numpy_data['trailer']['ly'] >= 32768 ):
            self.log.debug ( 'critical: lx or ly seems to be invalid: (' 
                    + numpy.str ( numpy_data['trailer']['lx'][0] ) + ', ' 
                    + numpy.str ( numpy_data['trailer']['ly'][0] ) + ')' )
            self.log.debug ( 'critical: If you want to allow arrays as large as this, modify the code!' )
            return

        try:
            self.__array = numpy_data['data'][0].reshape ( numpy_data['trailer']['ly'][0], 
                                                           numpy_data['trailer']['lx'][0] )
        except ValueError as e:
            self.log.debug ( "%s" % str ( e ) )
            raise
    
        self.__array [ numpy.where ( numpy_data == -3.1E38 ) ] = numpy.nan
        self.__adhoc_trailer = numpy_data['trailer']

        self.log.info ( "Successfully read adhoc 2d object from file %s." % str ( self.__file_name ) )

    def _read_adhoc_3d ( self, xyz = True ):
        """
        This method's goal is to read the contents of self.__file_object as a tri-dimensional ADHOC file.

        Parameters:

        * xyz : boolean : defaults to True.
            False to return data in standard zxy adhoc format,
            True  to return data in xyz format (default).
        """
        self.log.debug ( tuna.log.function_header ( ) )

        data = self.__file_object
        data.seek ( 0, 2 )
        sz = int ( ( data.tell ( ) - 256 ) / 4 )
            
        dt = np.dtype ( [ ( 'data', np.float32, sz ),
                          ( 'trailer', 
                            [ ( 'nbdim', np.int32 ), 
                              ( 'id', np.int8, 8 ), 
                              ( 'lx', np.int32 ), 
                              ( 'ly', np.int32 ), 
                              ( 'lz', np.int32 ), 
                              ( 'scale', np.float32 ), 
                              ( 'ix0', np.int32 ), 
                              ( 'iy0', np.int32 ), 
                              ( 'zoom', np.float32 ), 
                              ( 'xl1', np.float32 ), 
                              ( 'xi1', np.float32 ), 
                              ( 'vr0', np.float32), 
                              ( 'corrv', np.float32 ), 
                              ( 'p0', np.float32 ), 
                              ( 'xlp', np.float32 ), 
                              ( 'xl0', np.float32 ), 
                              ( 'vr1', np.float32 ), 
                              ( 'xik', np.float32 ), 
                              ( 'cdelt1', np.float64 ), 
                              ( 'cdelt2', np.float64 ), 
                              ( 'crval1', np.float64 ), 
                              ( 'crval2', np.float64 ), 
                              ( 'crpix1', np.float32 ), 
                              ( 'crpix2', np.float32 ), 
                              ( 'crota2', np.float32 ), 
                              ( 'equinox', np.float32 ), 
                              ( 'x_mirror', np.int8 ), 
                              ( 'y_mirror', np.int8 ), 
                              ( 'was_compressed', np.int8 ), 
                              ( 'none2', np.int8, 1 ), 
                              ( 'comment', np.int8, 128 ) ] ) ] )

        ad3 = np.fromfile ( self.__file_name, dtype = dt )

        if ( ad3['trailer']['lx'][0] * ad3['trailer']['ly'][0] * ad3['trailer']['lz'][0] >= 250 * 1024 * 1024 ):
            self.log.debug ( 'critical: lx or ly or lz seems to be invalid: (' + 
                  np.str(ad3['trailer']['lx'][0]) + ', ' + 
                  np.str(ad3['trailer']['ly'][0]) + ', ' + 
                  np.str(ad3['trailer']['lz'][0]) + ')')
            self.log.debug ( 'critical: If you want to allow arrays as large as this, modify the code!')
            return

        if ad3['trailer']['nbdim'] == -3:  # nbdim ?
            data = ad3['data'][0].reshape(ad3['trailer']['lz'][0], ad3['trailer']['ly'][0], ad3['trailer']['lx'][0])  #
        else:
            data = ad3['data'][0].reshape(ad3['trailer']['ly'][0], ad3['trailer']['lx'][0], ad3['trailer']['lz'][0])

        if xyz & (ad3['trailer']['nbdim'] == 3):
            #return the data ordered in z, y, x
            data = data.transpose(2, 0, 1)

        if (not xyz) & (ad3['trailer']['nbdim'] == -3):
            #return data ordered in y, x, z
            data = data.transpose(1, 2, 0)

        data[np.where(data == -3.1E38)] = np.nan
        #ad3 = dtu(data, ad3['trailer'][0], filename)
        self.__array = data
        self.__trailer = ad3['trailer'][0]
        self.log.info ( "Successfully read adhoc 3d object from file %s." % str ( self.__file_name ) )

    def get_trailer ( self ):
        """
        This method's goal is to return the current trailer.

        Returns:

        * self.__trailer : numpy.ndarray
            Containing the current values for the trailer.
        """
        return self.__trailer
