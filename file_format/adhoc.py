import os
import numpy
import numpy as np
from scipy import constants as cst
import pyfits as pf
from pyfits import Column
from time import sleep
import matplotlib as mpl
from matplotlib import pyplot as plt
from sys import path
path.append ( "/home/nix/sync/tuna/" )
from github.file_format import file_format
#from PyQt.QtGui import QPixmap
#import codecs

#verifier l'organisation des cubes fits si on les ouvre en python
#faire un programme readad qui voit l'extension pour savoir comment ouvir (soit ad2, ad3, ad1...)
#gestion des NaN a inclure (input/output)!!!


class adhoc ( file_format.file_format ):
    """
    Class for reading files in one of the ADHOC file formats (AD2 or AD3).

    First implemented by Benoît Epinat from LAM.
    The ADHOC file formats were developed for use with the ADHOC software solution,
    developed at LAM by Jacques Boulesteix.
    The source code for this software is not open (or at least not available at the
    time of this writing).
    Please check the file adhoc_file_format.eml for documentation regarding this format.
    """

    def __init__ ( self, adhoc_type = None, adhoc_trailer = None, file_name = None, image_ndarray = None ):
        self.__adhoc_type = adhoc_type
        self.__adhoc_trailer = adhoc_trailer
        self.__file_name = file_name
        self.__image_ndarray = image_ndarray
        self.__file_object = None
        super ( adhoc, self ).__init__ ( )

    def discover_adhoc_type ( self ):
        if self.__file_name:
            if self.__file_object:
                self.__file_object.close ( )
            self.__file_object = open ( self.__file_name, "rb" )
            self.__file_object.seek ( 0, os.SEEK_END )
            self._image_ndarray_size = ( self.__file_object.tell ( ) - 256 ) / 4  
            self.__file_object.close ( )

            adhoc_file_type = numpy.dtype ( [ ( 'image_data', numpy.float32, self._image_ndarray_size ),
                                              ( 'trailer', 
                                                [ ( 'number_of_dimensions', numpy.int32, 1 ),
                                                  ( 'parameters', numpy.int8, 252 ) ] ) ] )
            adhoc_file = numpy.fromfile ( self.__file_name, dtype = adhoc_file_type )
            #print ( adhoc_file['trailer']['number_of_dimensions'] )
            if adhoc_file['trailer']['number_of_dimensions'] not in ( [2], [3], [-3] ):
                print ( "Unrecognized number of dimensions." )
                return
            self.__adhoc_type = adhoc_file['trailer']['number_of_dimensions'][0]            

    def get_ndarray ( self ):
        if self.__file_name == None:
            return
        if self.__adhoc_type == None:
            self.discover_adhoc_type ( )
            if self.__adhoc_type == None:
                return
        if self.__file_object:
            self.__file_object.close ( )

        self.__file_object = open ( self.__file_name, "rb" )

        if self._image_ndarray_size == None:
            self._image_ndarray_size = ( self.__file_object.tell ( ) - 256 ) / 4  

        if self.__adhoc_type == 2:
            self.read_adhoc_2d ( )

        if self.__adhoc_type == 3 or self.__adhoc_type == -3:
            self.read_adhoc_3d ( )
        return self.__image_ndarray

    def read ( self ):
        self.get_ndarray ( )
        return self.convert_from_ndarray_into_QPixmap_list ( self.__image_ndarray )

    def read_adhoc_2d ( self ):
        """
        Attempts to read the contents of __file_object as a 2D ADHOC file.

        """

        adhoc_2d_file_type = numpy.dtype ( [ ( 'data', np.float32, self._image_ndarray_size ), 
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
            print ( 'Error: lx or ly seems to be invalid: (' 
                    + numpy.str ( numpy_data['trailer']['lx'][0] ) + ', ' 
                    + numpy.str ( numpy_data['trailer']['ly'][0] ) + ')' )
            print ( 'If you want to allow arrays as large as this, modify the code!' )
            return

        try:
            self.__image_ndarray = numpy_data['data'][0].reshape ( numpy_data['trailer']['ly'], 
                                                                   numpy_data['trailer']['lx'] )
        except ValueError as e:
            print ( "ValueError exception during NumPy reshape() (probably trying to open a 3d object with a 2d method).")
            raise e
    
        self.__image_ndarray[numpy.where ( numpy_data == -3.1E38 )] = numpy.nan
        self.__adhoc_trailer = numpy_data['trailer']

        print ( "Successfully read file as adhoc 2d object." )

    def read_adhoc_3d ( self, xyz = True ):
        """
        Parameters
        ----------
        filename: string, Name of the input file
        xyz = True: boolean (optional)
              False to return data in standard zxy adhoc format
              True  to return data in xyz format (default)
        """

        data = self.__file_object
        data.seek ( 0, 2 )
        sz = ( data.tell ( ) - 256 ) / 4
            
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
            print('Error: lx or ly or lz seems to be invalid: (' + 
                  np.str(ad3['trailer']['lx'][0]) + ', ' + 
                  np.str(ad3['trailer']['ly'][0]) + ', ' + 
                  np.str(ad3['trailer']['lz'][0]) + ')')
            print('If you want to allow arrays as large as this, modify the code!')
            return

        if ad3['trailer']['nbdim'] == -3:  # nbdim ?
            data = ad3['data'][0].reshape(ad3['trailer']['lz'], ad3['trailer']['ly'], ad3['trailer']['lx'])  #
        else:
            data = ad3['data'][0].reshape(ad3['trailer']['ly'], ad3['trailer']['lx'], ad3['trailer']['lz'])

        if xyz & (ad3['trailer']['nbdim'] == 3):
            #return the data ordered in z, y, x
            data = data.transpose(2, 0, 1)

        if (not xyz) & (ad3['trailer']['nbdim'] == -3):
            #return data ordered in y, x, z
            data = data.transpose(1, 2, 0)

        data[np.where(data == -3.1E38)] = np.nan
        #ad3 = dtu(data, ad3['trailer'][0], filename)
        self.__image_ndarray = data
        self.__trailer = ad3['trailer'][0]
        print ( "Successfully read adhoc 3d object." )

    def get_trailer ( self ):
        return self.__trailer

    def read_ada ( self, xsize, ysize ):
        """
        Parameters
        ----------
        filename: string
            Name of the input ada file
        xsize: float
            Size of the final image along x-axis
        ysize: float
            Size of the final image along y-axis

        Returns
        -------
        out: ndarray
            Image corresponding to the ada
        """

        #Initialization of the image
        im = np.zeros((ysize, xsize))
        #We read the ada file
        ada = np.fromfile(filename, dtype=np.int16)
        #We reshape the data since we know the file is organize with y,x,y,x,y,x...
        data = ada.reshape(ada.size / 2, 2)
        plt.ion()
        image = plt.imshow(im)
        #we loop on each photon to create the image
        for i in range(data.shape[0]):
            #we check the location of each photon is inside the image
            if (data[i][0] < ysize) & (data[i][1] < xsize) & (data[i][0] >= 0) & (data[i][1] >= 0):
                im[data[i][0], data[i][1]] += 1
                image.set_data(im)
                #plt.draw()
                #sleep(0.1)
        plt.draw()
        return im
        #it seems that the first frame is duplicated
        #it would be nice to be able to display the creation of the image photon by photon
