
"""
This module 's goal is to generate adhoc files.

"""
import logging
import os
import numpy
import numpy as np
import IPython
import math
import warnings
import tuna


class adhocfile ( object ):
    """
    This class' responsibilities include: generating input file in one
    of the ADHOC file formats (AD2 or AD3).

    """

    def __init__ ( self,
                   adhoc_type = None,
                   file_name = None,
                   array = None,lx=None,ly=None,lz=None,dim=None):
        """

        """
        super ( adhocfile, self ).__init__ ( )
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )

        self.__adhoc_type = adhoc_type
        #self.__adhoc_trailer = adhoc_trailer
        self.__file_name = file_name

        self.__lx=lx
        self.__ly=ly
        self.__lz=lz
        self.__dim=dim

        self.__array = np.random.rand(1,1)
        #self.__array_size=self.lx*self.ly

        self.testarray=array

    def create(self):
        """

        This method's goal is to create input file

        """

        #---------------------------------#
        #     traitement fichier ad2      #
        #---------------------------------#


        if self.__adhoc_type == 2:
            if self.testarray == None:
                self.__array_size=0
            else:
                self.__array_size=self.__lx*self.__ly

            #self.__array_size=self.__lx*self.__ly
            adhoc_file_type=np.dtype ( [ ( 'data', np.float32,int(self.__array_size)),
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

            with open(self.__file_name,"wb") as fich:
                donnees=np.array(self.__array,dtype=adhoc_file_type)

                donnees['trailer']['nbdim']=self.__adhoc_type
                donnees['trailer']['lx']=self.__lx
                donnees['trailer']['ly']=self.__ly

                donnees.tofile(fich)

        #---------------------------------#
        #     traitement fichier ad3      #
        #---------------------------------#

        if self.__adhoc_type == 3:

            self.__array_size=self.__lx*self.__ly*self.__lz
            adhoc_file_type = np.dtype ( [ ( 'data', np.float32, int(self.__array_size) ),
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




            with open(self.__file_name,"wb") as fich:
                donnees=np.array(self.__array,dtype=adhoc_file_type)

                if self.__dim == None:
                    donnees['trailer']['nbdim']=self.__adhoc_type
                else:
                    donnees['trailer']['nbdim']=-3

                donnees['trailer']['lx']=self.__lx
                donnees['trailer']['ly']=self.__ly
                donnees['trailer']['lz']=self.__lz

                donnees.tofile(fich)

        #---------------------------------#
        #  verification creation fichier  #
        #---------------------------------#

        self.__file_object = open ( self.__file_name, "rb" )
        self.__file_object.seek ( 0, os.SEEK_END )
        self.__array_size = ( self.__file_object.tell ( ) - 256 ) / 4

        print("TEST self.__file_object.tell=",self.__file_object.tell())
        print("TEST self.__array_size=",self.__array_size)

        self.__file_object.close ( )
