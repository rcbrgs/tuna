from .adhoc import adhoc
from .adhoc_ada import ada
from .fits import fits
from os.path import dirname, isfile, join

import logging
import numpy
import sys
import time
import tuna
import IPython
import math
import warnings

try:
    with warnings.catch_warnings ( ):
        warnings.simplefilter ( "ignore" )
        import matplotlib.pyplot as plt
except ImportError:
    raise ImportError ( "Tuna requires matplotlib. Please install it." )

class user_interface(object):
    """
    New class add by Julien Penguen  13/09/2017

    This class' responsability is to operate on ADT (ADA),ADHOC and FITS files.

    It's constructors.

    Parameters:

    * file_name: string
      Contains a valid path for a ADT (ADA),ADHOC and FITS file.

    Example::

        import tuna
        FITS_file=tuna.io.user_interface(file_name='tuna/tuna/test/unit/unit_io/partial_3_planes.fits')
        FITS_file.get_array()
        FITS_file.info()
        FITS_file.get_metadata()
        FITS_file.get_photons()
        FITS_file.plot()
        etc...

        or

        import tuna
        ADHOC2D_file=tuna.io.user_interface(file_name='tuna/tuna/test/unit/unit_io/adhoc.ad2')
        ADHOC2D_file.info()
        ADHOC2D_file.get_array()
        ADHOC2D_file.get_metadata()
        ADHOC2D_file.get_photons()
        ADHOC2D_file.plot()
        etc...


        import tuna
        ADA_file=tuna.io.user_interface(file_name='tuna/tuna/test/unit/unit_io/G093/G093.ADT')
        ADA_file.info()
        ADA_file.get_array()
        ADA_file.get_metadata()
        ADA_file.get_photons()
        ADA_file.plot()
        etc...



    """

    def __init__(self, file_name=None):

        self.__file_name = file_name
        self.__file_path=dirname(file_name)

        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )
        self.log.debug ( tuna.log.function_header ( ) )

        if self.__file_name:

            #####################
            #case file ADA & ADT#
            #####################
            if ( self.__file_name.startswith ( ".ADT", -4 ) or
                 self.__file_name.startswith ( ".adt", -4 ) ):


                ada_object = ada ( file_name = self.__file_name )
                ada_object.read ( )
                self.__array = ada_object.get_array ( )
                self.__metadata = ada_object.get_metadata ( )
                self.__photons = ada_object.get_photons ( )
                self.__file_type = "ada"
                self.__ndim=self.__array.ndim
                self.__shape = self.__array.shape
                self.__color="Greys"

                if self.__ndim == 3:
                    self.__planes = self.__array.shape [ 0 ]
                    self.__rows   = self.__array.shape [ 1 ]
                    self.__cols   = self.__array.shape [ 2 ]
                elif self.__ndim == 2:
                    self.__planes = 1
                    self.__rows   = self.__array.shape [ 0 ]
                    self.__cols   = self.__array.shape [ 1 ]
                if ( self.__ndim < 2 or
                self.__ndim > 3 ):
                    print ( "ndarray has either less than 2 or more than 3 dimensions." )

                #super(user_interface, self).__init__()

            ################
            #case file FITS#
            ################
            elif ( self.__file_name.startswith ( ".fits", -5 ) or
                   self.__file_name.startswith ( ".FITS", -5 ) ):

                fits_object = fits ( file_name = self.__file_name )
                fits_object.read()
                self.__array = fits_object.get_array()
                self.__metadata = fits_object.get_metadata()
                self.__photons = fits_object.get_photons()
                self.__hdu_list_info=fits_object.get_hdu_list_info()
                self.__file_type = "fits"
                self.__ndim=self.__array.ndim
                self.__shape = self.__array.shape
                self.__color="Blues"

                if self.__ndim == 3:
                    self.__planes = self.__array.shape [ 0 ]
                    self.__rows   = self.__array.shape [ 1 ]
                    self.__cols   = self.__array.shape [ 2 ]
                elif self.__ndim == 2:
                    self.__planes = 1
                    self.__rows   = self.__array.shape [ 0 ]
                    self.__cols   = self.__array.shape [ 1 ]
                if ( self.__ndim < 2 or
                self.__ndim > 3 ):
                    print ( "ndarray has either less than 2 or more than 3 dimensions." )

                #super(user_interface, self).__init__()

            #################
            #case file ADHOC#
            #################
            elif ( self.__file_name.startswith ( ".ad2", -4 ) or
                   self.__file_name.startswith ( ".AD2", -4 ) or
                   self.__file_name.startswith ( ".ad3", -4 ) or
                   self.__file_name.startswith ( ".AD3", -4 ) ):

                adhoc_object = adhoc ( file_name = self.__file_name )
                adhoc_object.read ( )
                self.__array = adhoc_object.get_array ( )
                self.__metadata = adhoc_object.get_trailer()
                self.__file_type = "adhoc"
                self.__ndim=self.__array.ndim
                self.__shape = self.__array.shape
                self.__color="Reds"

                self.__photons = adhoc_object.get_photons ( )

                if self.__ndim == 3:
                    self.__planes = self.__array.shape [ 0 ]
                    self.__rows   = self.__array.shape [ 1 ]
                    self.__cols   = self.__array.shape [ 2 ]
                elif self.__ndim == 2:
                    self.__planes = 1
                    self.__rows   = self.__array.shape [ 0 ]
                    self.__cols   = self.__array.shape [ 1 ]
                if ( self.__ndim < 2 or
                self.__ndim > 3 ):
                    print ( "ndarray has either less than 2 or more than 3 dimensions." )

                #super(user_interface, self).__init__()




    def get_file_name(self):
        """
        New function add by Julien Penguen  13/09/2017
        available for ADHOC,ADA,FITS

        This method's goal is to return the input filename.

        Returns:

        * self.__file_name : file_name
        """
        return self.__file_name

    def get_file_path(self):
        """
        New function add by Julien Penguen  13/09/2017
        available for ADHOC,ADA,FITS

        This method's goal is to return the input file path.

        Returns:

        * self.__file_path

        """
        return self.__file_path

    def get_array ( self, ind=None ):
        """
        New function add by Julien Penguen  13/09/2017
        available for ADHOC,ADA,FITS

        This method's goal is to return the input array.

        Parameters:

        * ind : integer
        Specifies an existing planes.


        Returns:

        * self._array : numpy.ndarray
            The array containing the current data.

        or if ind not None

        *  self._array[ind]
            The array containing the current data for ind planes.

        """
        if ind == None:
            return self.__array
        else:
            return self.__array[ind]


    def get_metadata ( self,param=None ):
        """
        New function add by Julien Penguen  13/09/2017
        available for ADHOC,ADA,FITS

        This method's goal is to return the metadata structure.

        Parameters:

        * param : string
        Specifies an existing parameters (key of dictionary).
        objectname.get_metadata().keys() to get the list
        of dictionary keys

        Returns:

        * self.__metadata : dictionary
            A dictionary containing the metadata as read from the file.

        or if param not None

        * self.__metadata[param] : dictionary
            A dictionary containing the metadata as read from the file for the parameter param.
        """

        if param == None:
            return self.__metadata
        else:
            return self.__metadata[param]


    def info ( self ):
        """

        New function add by Julien Penguen  13/09/2017
        available for ADHOC,ADA,FITS

        This method's goal is to output to the current logging.info handler some metadata about the current file.

        """
        self.log.debug ( tuna.log.function_header ( ) )

        self.log.info ( "file_name = %s" % self.__file_name )
        self.log.info ( "shape = %s" % str ( self.__shape ) )
        self.log.info ( "file_type = %s" % str ( self.__file_type ) ) #new add by Julien Penguen 28/07/2017
        self.log.info ( "ndim = %d" % self.__ndim )
        self.log.info ( "planes = %d" % self.__planes )
        self.log.info ( "rows = %d" % self.__rows )
        self.log.info ( "cols = %d" % self.__cols )

        if self.__file_type == "fits":
            self.log.info ("hdu_list_info = %s" % self.__hdu_list_info)



    def plot ( self, subplot_number=None,cmap = "Reds", ipython = None):
        """
        New function add by Julien Penguen  13/09/2017
        available for ADHOC,ADA,FITS

        This function's goal is to plot a numpy ndarray argument.
        on  a mosaic .

        Parameters:

        *subplot_number: integer
            The number of the slot to display

        * cmap : str : "Reds"
            The colormap to be passed to matplotlib.

        * ipython : object
            A reference to the running ipython environment.

        Returns:

            Display all the data slots

            or if  subplot_number is not None:

            Display the data for the subplot_number slot


        """

        if not ipython:
            ipython = IPython.get_ipython()
            if ipython == None:
                print ( "Could not get ipython reference, aborting plot." )
            ipython.magic ( "matplotlib qt" )


        ###################
        #case 3D data file#
        ###################

        if  len(self.__shape)  == 3:

            if subplot_number == None:
                subplots=self.__shape[0]
                print( "subplots = {}".format ( subplots ) )

                dimensions = math.ceil ( math.sqrt ( subplots ) )
                print( "should create mosaic of {} x {} slots.".format ( dimensions, dimensions ) )

                figure, axes = plt.subplots ( dimensions, dimensions, sharex='col', sharey='row' )

                figure.suptitle ( "{}".format(self.__file_name) )

                for plane in range ( subplots):
                    image = axes.flat [ plane ] .imshow ( self.__array[plane], cmap = cmap )
                    axes.flat[plane].set_title("Channel {}".format(plane))

                figure.subplots_adjust( hspace=0.3, right = 0.8 )

                colorbar_axe = figure.add_axes ( [ 0.85, 0.15, 0.05, 0.7 ] )
                figure.colorbar ( image, cax=colorbar_axe )

            else:

                figure, axe = plt.subplots ( 1, 1, sharex='col', sharey='row' )
                figure.suptitle ( "channel {} of {}".format(subplot_number,self.get_file_name()) )
                image = axe.imshow(self.get_array()[subplot_number], cmap = cmap)
                figure.subplots_adjust( hspace=0.3, right = 0.8 )
                colorbar_axe = figure.add_axes ( [ 0.85, 0.15, 0.05, 0.7 ] )
                figure.colorbar ( image, cax=colorbar_axe )


            return

        ###################
        #case 2D data file#
        ###################
        if len ( self.__shape) == 2:
            fig = plt.figure ( )
            plt.imshow ( self.get_array(), cmap = cmap )
            plt.colorbar ( orientation = "horizontal" )
            plt.title ( self.get_file_name() )



    def list_function(self):
        """
        New function add by Julien Penguen  13/09/2017
        available for ADA,ADHOC,FITS
        This method's goal is to obtain a list of available functions
        for the user_interface class

        """
        method_list = [func for func in dir(self) if callable(getattr(self, func)) and not func.startswith("__")]
        return method_list

    def get_photons ( self,channel=None ):
        """
        New function add by Julien Penguen  13/09/2017
        available for ADA,ADHOC,FITS

        This method's goal is to Return a photon table corresponding to the data read.

        Returns:

        * self.__photons : dictionary
            A dictionary containing a row for each photon count.

        or if  channel is not None:

            A dictionary containing a row for each photon count
            for the selected channel.


        """
        if channel == None:
            return self.__photons
        else:

            if self.__ndim == 2:
                print("ok toto")
                return self.__photons

            else:

                result = [(key, value) for key, value in self.__photons.items() if key.startswith(str(channel)+":")]
                return result
