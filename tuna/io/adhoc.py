# -*- coding: utf-8 -*-
"""This module scope covers ADHOC files' operations. 

ADHOC files typically have the .AD2 (for two-dimensional data) and .AD3 (for 
tri-dimensional data).

It is based on a module provided by Benoît Epinat, and integrated into Tuna in 
2015.
"""
__version__ = "0.2.1"
__changelog = {
    '0.2.1': {"Tuna": "0.16.5", "Change": "PEP8 and PEP257 compliance."},
    '0.2.0': {"Tuna": "0.14.0", "Change": "improved docstrings."},
    '0.1.2': {"Change": "Doc: module, class and function docstrings."}, 
    '0.1.1': {"Change": "Improved docstrings."},
    '0.1.0': {"Change": "Initial changelog."}
}

import logging
import os
import numpy
import numpy as np
import sys
from time import sleep
import types

from .file_reader import FileReader
import tuna
import IPython
import math
import warnings

import matplotlib.pyplot as plt

#verifier l'organisation des cubes fits si on les ouvre en python
#faire un programme readad qui voit l'extension pour savoir comment ouvir (soit
#ad2, ad3, ad1...)
#gestion des NaN a inclure (input/output)!!!

class Adhoc(FileReader):
    """This class' responsibilities include: reading files in one of the ADHOC 
    file formats (AD2 or AD3).

    First implemented by Benoit Epinat from LAM.
    The ADHOC file formats were developed for use with the ADHOC software 
    solution, developed at LAM by Jacques Boulesteix.

    It inherits from :ref:`tuna_io_file_reader_label`.

    Its constructor has the following signature:

    Parameters:

    * adhoc_type : int : defaults to None.
        Valid types are 2 and 3.

    * adhoc_trailer : numpy.ndarray : defaults to None.
        The trailer of an ADHOC file are the last 256 bytes of the file, and 
        contain metadata.

    * file_name : string : defaults to None.
        Must correspond to an existing ADHOC file.

    * array : numpy.ndarray : defaults to None.
        Will be read from the file, and its size is the file size minus 256 
        bytes, and each field has 32 bytes and is encoded as a float.

    Example usage::

        import tuna
        raw = tuna.io.Adhoc ( file_name = "tuna/tuna/test/unit/unit_io/" \
            + "adhoc.ad3" )
        raw.read ( )
        raw.get_array ( )
        raw.get_trailer ( )
    """

    def __init__(self, 
                 adhoc_type = None, 
                 adhoc_trailer = None, 
                 file_name = None, 
                 array = None):
        super(Adhoc, self).__init__()
        self.log = logging.getLogger(__name__)
        self.log.setLevel(logging.INFO)

        self.__adhoc_type = adhoc_type
        self.__adhoc_trailer = adhoc_trailer
        self.__adhoc_list_element = None
        self.__file_name = file_name
        self.__array = array
        self.__file_object = None
        self.__array_size= None

        self.__photons = {}

    def get_file_name(self):
        """Return the input filename.

        Returns:

        * self.__file_name : file_name

        """

        return self.__file_name

    def _discover_adhoc_type(self):
        """This method's goal is to open the file named file_name, get the 
        first 256 bytes as its trailer, and cast its remaining contents into
        a numpy array of numpy.float32 values.
        Since the trailer contains information regarding the dimensionality 
        of the data, this information is also retrieved from the file.
        """
        self.log.debug(tuna.log.function_header())

        if self.__file_name:
            try:
                self.__file_object = open(self.__file_name, "rb")
            except OSError as e:
                self.log.error("OSError: %s" % str(e))
                raise

            self.__file_object.seek(0, os.SEEK_END)
            if self.__file_object.tell() < 256:
                self.log.error("File does not contain valid numpy array.")
                self.__adhoc_type = None
                self.__file_object.close ( ) # New add by Julien Penguen 13/09/2017
                return
            self.__array_size = int((self.__file_object.tell() - 256) / 4)
            self.__file_object.close()

            if self.__array_size > int ( self.__array_size ):
                self.log.warning ( "Array size is not an integer value!" )
                self.__adhoc_type = None
                return

            try: 
                adhoc_file_type = numpy.dtype([(
                    'image_data', numpy.float32, self.__array_size ),
                    ('trailer', 
                     [('number_of_dimensions', numpy.int32, 1),
                      ('parameters', numpy.int8, 252)])])
            except ValueError as e:
                self.log.error("ValueError: %s." % str(e))
                self.log.warning("Impossible to guess adhoc type from file.")
                self.__adhoc_type = None
                return

            adhoc_file = numpy.fromfile(
                self.__file_name, dtype = adhoc_file_type)
            if adhoc_file['trailer']['number_of_dimensions'] not in (
                    [2], [3], [-3]):
                self.log.warning("Unrecognized number of dimensions in file" \
                                 + " %s." % str(self.__file_name))
                return
            self.__adhoc_type = adhoc_file['trailer']['number_of_dimensions'][0]

    def get_adhoc_type(self):
        """Return the current value of the adhoc_type.

        Returns:

        * self.__adhoc_type : adhoc_file['trailer']['number_of_dimensions'][0]

        """
        return self.__adhoc_type
    
    def set_adhoc_type(self, param):
        """Return the current value of the adhoc_type.

        Returns:

        * self.__adhoc_type : adhoc_file['trailer']['number_of_dimensions'][0]

        """
        self.__adhoc_type = param

        return self.__adhoc_type

    def get_array(self):
        """Return the current value of the data array.

        Returns:

        * self.__array : numpy.ndarray
            Containing the current data array.
        """
        return self.__array

    def get_array_size ( self ):
        """Return the current value of the data array.

        Returns:

        * self.__array : numpy.ndarray
            Containing the current data array.
        """
        return self.__array_size

    def get_element_array ( self, x=None, y=None, z=None ):
        """Return the current value of the element in data array.

        Returns:

        * self.__array[z][y][x]
            with x, y, z datas input
        """

        try:

            #-----test fichier ad2-----#
            if self.__adhoc_type == 2:

                if (x==None) or (y==None):
                    raise ValueError
                if (type(x) is not int) or (type(y) is not int):
                    raise TypeError
                if (x >= (self.get_array().shape[1])) or \
                   (y >= (self.get_array().shape[0])):
                    raise IndexError

                if (x <= ((self.get_array().shape[1])-1)) and \
                   (y <= ((self.get_array().shape[0])-1)):
                    return self.__array[y][x]

            #-----test fichier ad3-----#
            else:
                if (x==None) or (y==None) or (z==None):
                    raise ValueError
                if (type(x) is not int) or \
                   (type(y) is not int) or \
                   (type(z) is not int):
                    raise TypeError

                if (x > ((self.get_array().shape[2])-1)) or \
                   (y > ((self.get_array().shape[1])-1)) or \
                   (z > ((self.get_array().shape[0])-1)):
                    raise IndexError
                if (x <= ((self.get_array().shape[2])-1)) and \
                   (y <= ((self.get_array().shape[1])-1)) and \
                   (z <= ((self.get_array().shape[0])-1)):
                    return self.__array[z][y][x]

        except ValueError as e:
            self.log.error("ValueError: missing argument(s)")
        except IndexError as f:
            self.log.error("IndexError: Index out of bound")
        except TypeError as g:
            self.log.error("TypeError: x, y or z is not integer")

    def read(self, facteur_xyz = True):
        """Discover the ADHOC type (which corresponds to the data array 
        dimensionality), and when possible call the appropriate method 
        to read its contents.
        """
        self.log.debug(tuna.log.function_header())

        if self.__file_name == None:
            self.log.error("No file name selected, aborting read operation.")
            return

        if self.__adhoc_type == None:
            self._discover_adhoc_type()
            if self.__adhoc_type == None:
                self._is_readable = False
                return
            else:
                self._is_readable = True

        if self.__file_object:
            self.__file_object.close()

        self.__file_object = open(self.__file_name, "rb")

        if self.__array_size == None:
            self.__array_size = (self.__file_object.tell() - 256) / 4  

        if self.__adhoc_type == 2:
            self._read_adhoc_2d()

        if self.__adhoc_type == 3 or self.__adhoc_type == -3:
            if facteur_xyz == True:
                self._read_adhoc_3d()
            else:
                self._read_adhoc_3d(xyz=False)

    def _read_adhoc_2d(self):
        """Read the contents of self.__file_object as a 2D ADHOC file.
        """
        self.log.debug(tuna.log.function_header())

        adhoc_2d_file_type = numpy.dtype([('data',
                                           np.float32, int(self.__array_size)),
                                          ('trailer',
                                           [('nbdim', np.int32),
                                            ('id', np.int8, 8),
                                            ('lx', np.int32),
                                            ('ly', np.int32),
                                            ('lz', np.int32),
                                            ('scale', np.float32),
                                            ('ix0', np.int32),
                                            ('iy0', np.int32),
                                            ('zoom', np.float32),
                                            ('modevis', np.int32),
                                            ('thrshld', np.float32),
                                            ('step', np.float32),
                                            ('nbiso', np.int32),
                                            ('pal', np.int32),
                                            ('cdelt1', np.float64),
                                            ('cdelt2', np.float64),
                                            ('crval1', np.float64),
                                            ('crval2', np.float64),
                                            ('crpix1', np.float32),
                                            ('crpix2', np.float32),
                                            ('crota2', np.float32),
                                            ('equinox', np.float32),
                                            ('x_mirror', np.int8),
                                            ('y_mirror', np.int8),
                                            ('was_compressed', np.int8),
                                            ('none2', np.int8, 1),
                                            ('none', np.int32, 4),
                                            ('comment', np.int8, 128)])])

        numpy_data = numpy.fromfile(self.__file_name,
                                    dtype = adhoc_2d_file_type)

        if (numpy_data['trailer']['lx'] >= 32768) \
           | (numpy_data['trailer']['ly'] >= 32768):
            self.log.debug('critical: lx or ly seems to be invalid: ('
                           + numpy.str(numpy_data['trailer']['lx'][0]) + ', '
                           + numpy.str(numpy_data['trailer']['ly'][0]) + ')')
            self.log.debug('critical: If you want to allow arrays as large as ' \
                           'this, modify the code!' )
            self.log.info('critical: If you want to allow arrays as large as ' \
                          'this, modify the code!' )
            return

        try:
            self.__array = numpy_data['data'][0].reshape(
                int(numpy_data['trailer']['ly']),
                int(numpy_data['trailer']['lx']))
        except ValueError as e:
            self.log.debug("%s" % str(e))
            raise e

        self.__array[numpy.where(numpy_data == -3.1E38)] = numpy.nan
        self.__adhoc_trailer = numpy_data['trailer']

        self.__adhoc_list_element = adhoc_2d_file_type['trailer'].names

        self.log.info("Successfully read adhoc 2d object from file %s." % str(
            self.__file_name))

        for y in range(self.__array.shape[0]):
            for x in range(self.__array.shape[1]):
                if self.__array[y][x] != 0:
                    s_key = str(x) + ":" + str(y)
                    if s_key not in self.__photons.keys ( ):
                        photon = {}
                        photon['x'] = x
                        photon['y'] = y
                        photon['photons'] = self.__array[y][x]
                        self.__photons[s_key] = photon

        self.log.info("Successfully photon recovery from file %s." % str(
            self.__file_name))

    def _read_adhoc_3d(self, xyz = True):
        """Read the contents of self.__file_object as a tri-dimensional ADHOC
        file.

        Parameters:

        * xyz : boolean : defaults to True.
            False to return data in standard zxy adhoc format,
            True  to return data in xyz format (default).
        """
        self.log.debug(tuna.log.function_header())

        data = self.__file_object
        data.seek(0, 2)
        sz = (data.tell() - 256) / 4
        sz = int(sz)

        dt = np.dtype([('data', np.float32, sz),
                       ('trailer',
                        [('nbdim', np.int32),
                         ('id', np.int8, 8),
                         ('lx', np.int32),
                         ('ly', np.int32),
                         ('lz', np.int32),
                         ('scale', np.float32),
                         ('ix0', np.int32),
                         ('iy0', np.int32),
                         ('zoom', np.float32),
                         ('xl1', np.float32),
                         ('xi1', np.float32),
                         ('vr0', np.float32),
                         ('corrv', np.float32),
                         ('p0', np.float32),
                         ('xlp', np.float32),
                         ('xl0', np.float32),
                         ('vr1', np.float32),
                         ('xik', np.float32),
                         ('cdelt1', np.float64),
                         ('cdelt2', np.float64),
                         ('crval1', np.float64),
                         ('crval2', np.float64),
                         ('crpix1', np.float32),
                         ('crpix2', np.float32),
                         ('crota2', np.float32),
                         ('equinox', np.float32),
                         ('x_mirror', np.int8),
                         ('y_mirror', np.int8),
                         ('was_compressed', np.int8),
                         ('none2', np.int8, 1),
                         ('comment', np.int8, 128)])])

        ad3 = np.fromfile(self.__file_name, dtype = dt)

        if (ad3['trailer']['lx'][0] \
            * ad3['trailer']['ly'][0] \
            * ad3['trailer']['lz'][0] >= 250 * 1024 * 1024):
            self.log.debug('critical: lx or ly or lz seems to be invalid: (' +
                           np.str(ad3['trailer']['lx'][0]) + ', ' +
                           np.str(ad3['trailer']['ly'][0]) + ', ' +
                           np.str(ad3['trailer']['lz'][0]) + ')')
            self.log.debug('critical: If you want to allow arrays as large as ' \
                           'this, modify the code!')
            return

        if ad3['trailer']['nbdim'] == -3:  # nbdim ?
            data = ad3['data'][0].reshape(
                int(ad3['trailer']['lz']),
                int(ad3['trailer']['ly']),
                int(ad3['trailer']['lx']))
        else:
            data = ad3['data'][0].reshape(
                int(ad3['trailer']['ly']),
                int(ad3['trailer']['lx']),
                int(ad3['trailer']['lz']))

        if xyz & (ad3['trailer']['nbdim'] == 3):
            #return the data ordered in z, y, x
            data = data.transpose(2, 0, 1)

        self.log.debug("ad3['trailer']['nbdim'] = {}".format(
            ad3['trailer']['nbdim']))
        self.log.debug('xyz={}'.format(xyz))

        if (not xyz) & (ad3['trailer']['nbdim'] == -3):
            #return data ordered in y, x, z
            data = data.transpose(1, 2, 0)

        data[np.where(data == -3.1E38)] = np.nan

        self.__array = data

        self.__adhoc_list_element = dt['trailer'].names
        self.log.info("Successfully read adhoc 3d object from file %s." % str(
            self.__file_name))

        self.__adhoc_trailer=dict(zip(dt['trailer'].names,ad3['trailer'][0]))

        for channel in range(data.shape[0]):
            for y in range(data.shape[1]):
                for x in range(data.shape[2]):
                    if data[channel][y][x] != 0:
                        s_key = str(channel) + ":" + str(x) + ":" + str(y)
                        if s_key not in self.__photons.keys():
                            photon = {}
                            photon['channel'] = channel
                            photon['x'] = x
                            photon['y'] = y
                            photon['photons'] = data[channel][y][x]
                            self.__photons[s_key] = photon

        self.log.info("Successfully photon recovery from file %s." % str(
            self.__file_name))

    def get_photons ( self ):
        """Return a photon table corresponding to the data read.

        Returns:

        * self.__photons : dictionary
            A dictionary containing a row for each photon count.
        """
        return self.__photons

    def get_trailer ( self ):
        """Return the current trailer.

        Returns:

        * self.__trailer : numpy.ndarray
            Containing the current values for the trailer.
        """
        return self.__adhoc_trailer

    def get_element_trailer ( self, param ):
        """Return the value of a current trailer parameter.

        Parameters:

        * param : parameter of the current trailer

        Returns:

        * self.__trailer : numpy.ndarray
            Containing the current values for the trailer.
        """
        try:
            if param in self.__adhoc_list_element:
                if self.__adhoc_type == 2:
                    return self.__adhoc_trailer[param][0]
                else:
                    return self.__adhoc_trailer[param]

            else:
                print("The parameter ", param, " does not exist.")
                raise OSError

        except OSError as e:
            self.log.error ( "OSError: %s" % str ( e ) )

    def get_list_element_trailer ( self ):
        """Return the value of a current trailer parameter.

        Parameters:

        * param : parameter of the current trailer

        Returns:

        * self.__trailer : numpy.ndarray
            Containing the current values for the trailer.
        """
        return self.__adhoc_list_element
