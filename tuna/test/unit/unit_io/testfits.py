import sys
sys.path.insert(0,'/home/jpenguen/Bureau/PROJETS/TUNA/DOCS/JULIEN/virtual_tuna_juju/tuna')

import astropy.io.fits as astrofits
import copy
import logging
import os
import numpy
import numpy as np
from numpy import shape
from os import listdir
from os.path import dirname, isfile, join
import re
import tuna as progtuna
import IPython
import math
import warnings

import unittest

class testfits(unittest.TestCase):
    """Test Processor for unit tests of the fits module."""

    def setUp(self):
        """

        """
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.DEBUG )
        self.tests_files_directory="/home/jpenguen/Bureau/PROJETS/TUNA/DOCS/JULIEN/virtual_tuna_juju/tuna/tuna/test/unit/inputfiles_example/"

        #------#
        self.file_name_fits=self.tests_files_directory +'fichiers/partial.fits'

        self.array = None
        self.metadata = { }
        self.photons = { }
        self.hdu_list_info=None

        #------#
        try:
            with warnings.catch_warnings ( ):
                warnings.simplefilter ( "error" )
                hdu_list = astrofits.open ( self.file_name_fits )
            self.log.debug ( "File %s opened as a FITS file." % self.file_name_fits )

            # The file might have many HDU lists. If there are no arrays, then the file is invalid.
            hdu_info = hdu_list.info ( output = False )
            self.hdu_list_info=hdu_info #new add by Julien Penguen 24/07/2017
            self.log.debug ( "hdu_info = {}".format ( hdu_info ) )
            if len ( hdu_info ) == 1:
                self.array = hdu_list [ 0 ].data
                found = True

            invalid_flag = True
            for entry in hdu_info:
                if entry [ 4 ] != ( ):
                    invalid_flag = False
                    break
            if not found and invalid_flag:
                self.log.error ( "File is invalid: no dimensions found in its HDU list." )
                return

            # If the file has a single array, that is its data.
            possible_arrays = [ ]
            for entry_index in range ( len ( hdu_info ) ):
                if hdu_info [ entry_index ] [ 4 ] != ( ):
                    possible_arrays.append ( entry_index )
            if len ( possible_arrays ) == 1:
                self.array = hdu_list [ possible_arrays [ 0 ] ].data

            # If the file has several arrays, then possibly a mosaic is its data.
            if not found and len ( possible_arrays ) % 4 == 0:
                mosaic = True
                common_ndims = hdu_info [ possible_arrays [ 0 ] ] [ 4 ]
                for entry_index in possible_arrays:
                    if hdu_info [ entry_index ] [ 4 ] != common_ndims:
                        self.log.info ( "Cannot build a mosaic since HDU lists have different sizes." )
                        mosaic = False
                if mosaic:
                    self.log.debug ( "Creating a mosaic from the multiple HDU lists of the file." )
                    multiplier = math.sqrt ( len ( possible_arrays ) )
                    cols = common_ndims [ 1 ] * multiplier
                    rows = common_ndims [ 0 ] * multiplier
                    self.array = numpy.zeros ( shape = ( cols, rows ) )
                    cursor_col = 0
                    cursor_row = 0
                    for entry in possible_arrays:
                        self.log.debug ( "Adding HDU list {} to position ( {}, {} ).".format (
                            entry, cursor_col, cursor_row ) )
                        self.log.debug ( "Splicing array {} into {}, {}".format (
                            hdu_list [ entry ].data.shape, cursor_col, cursor_row ) )
                        self.array [ cursor_col : cursor_col + common_ndims [ 1 ],
                                       cursor_row : cursor_row + common_ndims [ 0 ] ] = hdu_list [ entry ].data
                        cursor_row += common_ndims [ 0 ]
                        if cursor_row >= common_ndims [ 0 ] * multiplier:
                            cursor_row = 0
                            cursor_col += common_ndims [ 1 ]

            if type ( self.array ) == None:
                if len ( possible_arrays ) > 1:
                    self.log.error ( "File has several distinct entries for data, and Tuna doesn't know how to parse it." )
                self.log.error ( "Data section of the file is None!" )
            else:
                self.log.debug ( "Assigned data section of first HDU as the image ndarray." )
                self.log.debug ( "self.array.ndim == %d" % self.array.ndim )

            metadata = { }
            for entry in possible_arrays:
                self.log.debug ( "Processing header for hdu_list [ {} ].".format ( entry ) )
                for key in hdu_list [ entry ].header.keys ( ):
                    metadata_value   = hdu_list [ entry ].header [ key ]
                    metadata_comment = hdu_list [ entry ].header.comments [ key ]
                    if key in list ( self.metadata.keys ( ) ):
                        if ( metadata_value, metadata_comment ) == self.metadata [ key ]:
                            self.log.debug ( "Ignoring duplicated metadata entry with key {}.".format ( key ) )
                            continue
                        else:
                            self.log.warning ( "Replacing metadata {} : ( {}, {} ) with new entry ( {}, {} ).".format ( key, self.metadata [ key ] [ 0 ], self.metadata [ key ] [ 1 ], metadata_value, metadata_comment ) )
                    self.metadata [ key ] = ( metadata_value, metadata_comment )
                    self.log.debug ( "{}: value = {}, comment = {}.".format ( key, metadata_value, metadata_comment ) )

            #self._is_readable = True
        except OSError as e:
            self.log.error ( "OSError: %s." % e )
            #self._is_readable = False

        #------------------------------------#
        #new add by Julien Penguen 13/09/2017

        ###################
        #case 2D data file#
        ###################
        if len(self.array.shape) ==2:

            for y in range(self.array.shape[0]):
                for x in range(self.array.shape[1]):
                    if (self.array[y][x]).all() != 0:
                    #print (data[channel][x][y])
                        s_key = str ( x ) + ":" + str ( y )
                        if s_key not in self.photons.keys ( ):
                            photon = { }
                            photon [ 'x'       ] = x
                            photon [ 'y'       ] = y
                            photon [ 'photons' ] = self.array[y][x]
                            self.photons [ s_key ] = photon

        ###################
        #case 3D data file#
        ###################
        if len(self.array.shape) ==3:

            for channel in range(self.array.shape[0]):
                for y in range(self.array.shape[1]):
                    for x in range(self.array.shape[2]):
                        if self.array[channel][y][x] != 0:
                        #print (data[channel][x][y])
                            s_key = str ( channel ) + ":" + str ( x ) + ":" + str ( y )
                            if s_key not in self.photons.keys ( ):
                                photon = { }
                                photon [ 'channel' ] = channel
                                photon [ 'x'       ] = x
                                photon [ 'y'       ] = y
                                photon [ 'photons' ] = self.array[channel][y][x]
                                self.photons [ s_key ] = photon


        self.log.info ( "Successfully photon recovery from file %s." % str ( self.file_name_fits ) )






    def test_nonexisting_file ( self ):
        """test function read"""
        #file_name = self.tests_files_directory + "fichiers/nonexistingfile.fits"
        #self.assertRaises ( OSError, lambda: progtuna.tuna.io.fits().read())
        self.assertIsNone( progtuna.tuna.io.fits().read())
    #
    # def test_empty_file ( self ):
    #     """test function read"""
    #     file_name=self.tests_files_directory +"fichiers_julien/fake_fits.fits"
    #     self.assertIsNone(progtuna.tuna.io.fits(file_name=file_name).read())

    def test_get_file_name(self):
        """Test function get_file_name"""
        test_object_fits=progtuna.tuna.io.fits(file_name=self.file_name_fits)
        test_object_fits.read()
        self.assertEqual(test_object_fits.get_file_name(),self.file_name_fits)

    def test_get_hdu_list_info(self):
        """Test function get_hdu_list_info"""
        test_object_fits=progtuna.tuna.io.fits(file_name=self.file_name_fits)
        test_object_fits.read()
        self.assertEqual(test_object_fits.get_hdu_list_info(),self.hdu_list_info)

    def test_get_array(self):
        """Test function get_array"""
        test_object_fits=progtuna.tuna.io.fits(file_name=self.file_name_fits)
        test_object_fits.read()
        self.assertEqual(np.all(test_object_fits.get_array()),np.all(self.array))

    def test_get_metadata(self):
        """Test function get_metadata"""
        test_object_fits=progtuna.tuna.io.fits(file_name=self.file_name_fits)
        test_object_fits.read()
        self.assertEqual(np.all(test_object_fits.get_metadata()),np.all(self.metadata))

    def test_get_photons(self):
        """Test function get_photons"""
        test_object_fits=progtuna.tuna.io.fits(file_name=self.file_name_fits)
        test_object_fits.read()
        self.assertEqual(np.all(test_object_fits.get_photons()),np.all(self.photons))
