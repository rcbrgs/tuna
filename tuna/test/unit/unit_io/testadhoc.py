import sys
sys.path.insert(0,'/home/jpenguen/Bureau/PROJETS/TUNA/DOCS/JULIEN/virtual_tuna_juju/tuna')

import logging
import os
import numpy
import numpy as np
import tuna as progtuna
import IPython
import math
import warnings

import unittest


class testadhoc(unittest.TestCase):
    """Test Processor for unit tests of the adhoc module."""

    def setUp(self):

        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.DEBUG )
        self.tests_files_directory="/home/jpenguen/Bureau/PROJETS/TUNA/DOCS/JULIEN/virtual_tuna_juju/tuna/tuna/test/unit/inputfiles_example/"

        #----definition ad2----#
        self.file_name_ad2=self.tests_files_directory +'fichiers/adhoc.ad2'

        self.file_object_ad2 = open ( self.file_name_ad2, "rb" )
        self.file_object_ad2.seek ( 0, os.SEEK_END )
        array_size_ad2 = ( self.file_object_ad2.tell ( ) - 256 ) / 4


        self.datatype_ad2=np.dtype ( [ ( 'data', np.float32, int(array_size_ad2)),
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


        self.data_ad2=np.fromfile ( self.file_name_ad2, self.datatype_ad2)

        try:
            self.array_ad2 = self.data_ad2['data'][0].reshape ( int(self.data_ad2['trailer']['ly']),int(self.data_ad2['trailer']['lx']) )
        except ValueError as e:
            #self.log.debug ( "%s" % str ( e ) )
            raise

        self.array_ad2[ np.where ( self.data_ad2 == -3.1E38 ) ] = np.nan
        self.photons_ad2={ }

        for y in range(self.array_ad2.shape[0]):
            for x in range(self.array_ad2.shape[1]):
                if self.array_ad2[y][x] != 0:
                    s_key = str ( x ) + ":" + str ( y )
                    if s_key not in self.photons_ad2.keys ( ):
                        photon = { }
                        photon [ 'x'       ] = x
                        photon [ 'y'       ] = y
                        photon [ 'photons' ] = self.array_ad2[y][x]
                        self.photons_ad2 [ s_key ] = photon


        #----definition ad3----#

        self.file_name_ad3=self.tests_files_directory +'fichiers_julien/test_adhocOK.ad3'

        self.file_object_ad3 = open ( self.file_name_ad3, "rb" )
        self.file_object_ad3.seek ( 0, os.SEEK_END )
        array_size_ad3 = ( self.file_object_ad3.tell ( ) - 256 ) / 4

        self.datatype_ad3 = np.dtype ( [ ( 'data', np.float32, int(array_size_ad3) ),
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




        self.data_ad3=np.fromfile ( self.file_name_ad3, dtype =self.datatype_ad3)

        self.xyz=True

        if ( self.data_ad3['trailer']['lx'][0] * self.data_ad3['trailer']['ly'][0] * self.data_ad3['trailer']['lz'][0] >= 250 * 1024 * 1024 ):
            self.log.debug ( 'critical: lx or ly or lz seems to be invalid: (' +
                  np.str(self.data_ad3['trailer']['lx'][0]) + ', ' +
                  np.str(self.data_ad3['trailer']['ly'][0]) + ', ' +
                  np.str(self.data_ad3['trailer']['lz'][0]) + ')')
            self.log.debug ( 'critical: If you want to allow arrays as large as this, modify the code!')
            return

        if self.data_ad3['trailer']['nbdim'] == -3:  # nbdim ?
            self.file_object_ad3 = self.data_ad3['data'][0].reshape(int(self.data_ad3['trailer']['lz']), int(self.data_ad3['trailer']['ly']), int(self.data_ad3['trailer']['lx']))  #
        else:
            self.file_object_ad3 = self.data_ad3['data'][0].reshape(int(self.data_ad3['trailer']['ly']), int(self.data_ad3['trailer']['lx']), int(self.data_ad3['trailer']['lz'])) #new add by Julien Penguen 17/07/2017

        if self.xyz & (self.data_ad3['trailer']['nbdim'] == 3):
            #return the data ordered in z, y, x
            self.file_object_ad3 = self.file_object_ad3.transpose(2, 0, 1)
            pass

        if (not self.xyz) & (self.data_ad3['trailer']['nbdim'] == -3):
            #return data ordered in y, x, z
            self.file_object_ad3 = self.file_object_ad3.transpose(1, 2, 0)
            pass



        self.file_object_ad3 [ np.where ( self.data_ad3 == -3.1E38 ) ] = np.nan
        self.array_ad3=self.file_object_ad3

        self.adhoc_trailer=dict(zip(self.datatype_ad3['trailer'].names,self.data_ad3['trailer'][0]))

        self.photons_ad3={ }

        for channel in range(self.file_object_ad3.shape[0]):
            for y in range(self.file_object_ad3.shape[1]):
                for x in range(self.file_object_ad3.shape[2]):
                    if self.file_object_ad3[channel][y][x] != 0:
                        s_key = str ( channel ) + ":" + str ( x ) + ":" + str ( y )
                        if s_key not in self.photons_ad3.keys ( ):
                            photon = { }
                            photon [ 'channel' ] = channel
                            photon [ 'x'       ] = x
                            photon [ 'y'       ] = y
                            photon [ 'photons' ] = self.file_object_ad3[channel][y][x]
                            self.photons_ad3 [ s_key ] = photon


        #--------------------#
        #----definition ad3 dim -3----#

        self.file_name_ad3_OTHER=self.tests_files_directory +'fichiers_julien/test_adhoc_dim-3.ad3'

        self.file_object_ad3_OTHER = open ( self.file_name_ad3_OTHER, "rb" )
        self.file_object_ad3_OTHER.seek ( 0, os.SEEK_END )
        array_size_ad3_OTHER = ( self.file_object_ad3_OTHER.tell ( ) - 256 ) / 4

        self.datatype_ad3_OTHER = np.dtype ( [ ( 'data', np.float32, int(array_size_ad3_OTHER) ),
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


        self.data_ad3_OTHER=np.fromfile ( self.file_name_ad3_OTHER, dtype =self.datatype_ad3_OTHER)

        self.xyz=False

        if ( self.data_ad3_OTHER['trailer']['lx'][0] * self.data_ad3_OTHER['trailer']['ly'][0] * self.data_ad3_OTHER['trailer']['lz'][0] >= 250 * 1024 * 1024 ):
            self.log.debug ( 'critical: lx or ly or lz seems to be invalid: (' +
                  np.str(self.data_ad3_OTHER['trailer']['lx'][0]) + ', ' +
                  np.str(self.data_ad3_OTHER['trailer']['ly'][0]) + ', ' +
                  np.str(self.data_ad3_OTHER['trailer']['lz'][0]) + ')')
            self.log.debug ( 'critical: If you want to allow arrays as large as this, modify the code!')
            return

        if self.data_ad3_OTHER['trailer']['nbdim'] == -3:  # nbdim ?
            self.file_object_ad3_OTHER = self.data_ad3_OTHER['data'][0].reshape(int(self.data_ad3_OTHER['trailer']['lz']),int(self.data_ad3_OTHER['trailer']['ly']), int(self.data_ad3_OTHER['trailer']['lx']))  #new add by Julien Penguen 03/10/2017
        else:
            self.file_object_ad3_OTHER = self.data_ad3_OTHER['data'][0].reshape(int(self.data_ad3_OTHER['trailer']['ly']), int(self.data_ad3_OTHER['trailer']['lx']), int(self.data_ad3_OTHER['trailer']['lz'])) #new add by Julien Penguen 17/07/2017

        if self.xyz & (self.data_ad3_OTHER['trailer']['nbdim'] == 3):
            #return the data ordered in z, y, x
            print('coucou test!')
            self.file_object_ad3_OTHER = self.file_object_ad3_OTHER.transpose(2, 0, 1)
            pass

        if (not self.xyz) & (self.data_ad3_OTHER['trailer']['nbdim'] == -3):
            #return data ordered in y, x, z
            self.file_object_ad3_OTHER = self.file_object_ad3_OTHER.transpose(1, 2, 0)
            print('test OK pour xyz')
            pass



        self.file_object_ad3_OTHER [ np.where ( self.data_ad3_OTHER == -3.1E38 ) ] = np.nan
        self.array_ad3_OTHER=self.file_object_ad3_OTHER

        self.adhoc_trailer_OTHER=dict(zip(self.datatype_ad3_OTHER['trailer'].names,self.data_ad3_OTHER['trailer'][0]))

        self.photons_ad3_OTHER={ }

        for channel in range(self.file_object_ad3_OTHER.shape[0]):
            for y in range(self.file_object_ad3_OTHER.shape[1]):
                for x in range(self.file_object_ad3_OTHER.shape[2]):
                    if self.file_object_ad3_OTHER[channel][y][x] != 0:
                        s_key = str ( channel ) + ":" + str ( x ) + ":" + str ( y )
                        if s_key not in self.photons_ad3_OTHER.keys ( ):
                            photon = { }
                            photon [ 'channel' ] = channel
                            photon [ 'x'       ] = x
                            photon [ 'y'       ] = y
                            photon [ 'photons' ] = self.file_object_ad3_OTHER[channel][y][x]
                            self.photons_ad3_OTHER [ s_key ] = photon


        #--------------------#


        pass


    def test_nonexisting_file ( self ):
        """test function read"""
        file_name = self.tests_files_directory + "fichiers/nonexistingfile.ad2"
        self.assertRaises ( OSError, lambda: progtuna.tuna.io.adhoc(file_name=file_name).read())

    def test_empty_file ( self ):
        """test function read"""
        file_name=self.tests_files_directory +"fichiers/fake_adhoc.ad2"
        self.assertIsNone(progtuna.tuna.io.adhoc(file_name=file_name).read())

    def test_get_file_name(self):
        """Test function get_file_name"""
        test_object_ad2=progtuna.tuna.io.adhoc(file_name=self.file_name_ad2)
        test_object_ad2.read()
        self.assertEqual(progtuna.tuna.io.adhoc(file_name=self.file_name_ad2).get_file_name(),self.file_name_ad2)


    def test_get_trailer(self):
        """Test function get_trailer"""

        #-----test fichier ad2-----#
        test_object_ad2=progtuna.tuna.io.adhoc(file_name=self.file_name_ad2)
        test_object_ad2.read()
        list_ad2=test_object_ad2.get_list_element_trailer()
        succes_ad2=0

        for i in list_ad2:
            print("boucle:",i)

            if i in self.datatype_ad2['trailer'].names:
                paramOK=True

                if (np.all(test_object_ad2.get_element_trailer(i)) == np.all(self.data_ad2['trailer'][i][0])):

                    succes_ad2=succes_ad2+1

            else:
                paramOK=False
                print( "The parameter ",i," does not exist.")


        if (succes_ad2 ==len(list_ad2)):
            self.assertEqual(test_object_ad2.get_trailer(),self.data_ad2['trailer'])



        #-----test fichier ad3-----#
        test_object_ad3=progtuna.tuna.io.adhoc(file_name=self.file_name_ad3)
        test_object_ad3.read()

        list_ad3=test_object_ad3.get_list_element_trailer()
        succes_ad3=0

        for i in list_ad3:
            print("boucle:",i)

            if i in self.datatype_ad3['trailer'].names:
                paramOK=True
                if (np.all(test_object_ad3.get_element_trailer(i)) == np.all(self.data_ad3['trailer'][i])):
                    succes_ad3=succes_ad3+1

            else:
                paramOK=False
                print( "The parameter ",i," does not exist.")

        if (succes_ad3 ==len(list_ad3)):
            self.assertEqual(np.all(test_object_ad3.get_trailer()),np.all(test_object_ad3.get_trailer()))

        #-------------------------#


    def test_get_list_element_trailer(self):
        """Test function get_list_element_trailer"""

        #---------------------------------#
        test_object_ad2=progtuna.tuna.io.adhoc(file_name=self.file_name_ad2)
        test_object_ad2.read()
        self.assertEqual(test_object_ad2.get_list_element_trailer(),self.datatype_ad2['trailer'].names)
        print("get_list_element_trailer ok for ad2!!")
        #---------------------------------#
        test_object_ad3=progtuna.tuna.io.adhoc(file_name=self.file_name_ad3)
        test_object_ad3.read()
        self.assertEqual(test_object_ad3.get_list_element_trailer(),self.datatype_ad3['trailer'].names)
        print("get_list_element_trailer ok for ad3!!")
        #---------------------------------#

    def test_get_element_trailer(self):
        """Test function get_element_trailer"""
        #--------------------------------#
        test_object_ad2=progtuna.tuna.io.adhoc(file_name=self.file_name_ad2)
        test_object_ad2.read()

        param_ad2=["was_compressed","lx","toto",12,"",None]

        for i in param_ad2:
            print("boucle:",i)

            if i in test_object_ad2.get_list_element_trailer():
                paramOK=True
            else:
                paramOK=False
                print( "The parameter ",i," does not exist.")
                pass

            if paramOK == True:
                self.assertEqual(test_object_ad2.get_element_trailer(i),self.data_ad2['trailer'][i][0])

            else:
                self.assertRaises ( OSError, test_object_ad2.get_element_trailer(i))

        #--------------------------------#
        test_object_ad3=progtuna.tuna.io.adhoc(file_name=self.file_name_ad3)
        test_object_ad3.read()

        param_ad3=["was_compressed","lx","toto",12,"lz"]

        for j in param_ad3:
            print("boucle ad3:",j)

            if j in test_object_ad3.get_list_element_trailer():
                paramOK=True
            else:
                paramOK=False
                print( "The parameter ",j," does not exist.")
                pass

            print("paramOK=",paramOK)
            if paramOK == True:
                print("test1")
                print("test_object_ad3.get_element_trailer(j)=",test_object_ad3.get_element_trailer(j))
                print("self.data_ad3['trailer'][j][0]=",self.data_ad3['trailer'][j])
                self.assertEqual(test_object_ad3.get_element_trailer(j),self.data_ad3['trailer'][j])
                print("test2")
            else:
                self.assertRaises ( OSError, test_object_ad3.get_element_trailer(j))

        #--------------------------------#


    def test_get_adhoc_type(self):
        """Test function get_adhoc_type"""
        #--------------------------------#
        test_object_ad2=progtuna.tuna.io.adhoc(file_name=self.file_name_ad2)
        test_object_ad2.read()
        adhoc_type_ad2=self.data_ad2['trailer']['nbdim'][0]
        self.assertEqual(test_object_ad2.get_adhoc_type(),adhoc_type_ad2)

        #--------------------------------#
        test_object_ad3=progtuna.tuna.io.adhoc(file_name=self.file_name_ad3)
        test_object_ad3.read()
        adhoc_type_ad3=self.data_ad3['trailer']['nbdim']
        self.assertEqual(test_object_ad3.get_adhoc_type(),adhoc_type_ad3)
        #--------------------------------#

    def test_get_array(self):
        """Test function get_array"""
        #--------------------------------#
        test_object_ad2=progtuna.tuna.io.adhoc(file_name=self.file_name_ad2)
        test_object_ad2.read()
        self.assertEqual(np.all(test_object_ad2.get_array()),np.all(self.array_ad2))

        #--------------------------------#
        test_object_ad3=progtuna.tuna.io.adhoc(file_name=self.file_name_ad3)
        test_object_ad3.read()
        self.assertEqual(np.all(test_object_ad3.get_array()),np.all(self.array_ad3))
        #--------------------------------#


    def test_get_element_array(self):
        """Test function get_element_array"""
        #--------------------------------#
        test_object_ad2=progtuna.tuna.io.adhoc(file_name=self.file_name_ad2)
        test_object_ad2.read()

        self.assertEqual(test_object_ad2.get_element_array(10,5),self.array_ad2[5][10])
        self.assertRaises(ValueError,test_object_ad2.get_element_array())
        self.assertRaises(IndexError,test_object_ad2.get_element_array(10000,1))
        self.assertRaises(TypeError,test_object_ad2.get_element_array("test",1))

        #--------------------------------#
        test_object_ad3=progtuna.tuna.io.adhoc(file_name=self.file_name_ad3)
        test_object_ad3.read()
        self.assertEqual(test_object_ad3.get_element_array(10,20,1),self.array_ad3[1][20][10])
        self.assertRaises(ValueError,test_object_ad3.get_element_array())
        self.assertRaises(IndexError,test_object_ad3.get_element_array(10000,1,1))
        self.assertRaises(TypeError,test_object_ad3.get_element_array("test",1,1))
        #--------------------------------#

    def test_read(self):
        """Test function read"""
        #--------------------------------#
        test_object_ad2=progtuna.tuna.io.adhoc()
        test_object_ad2.read()

        self.assertIsNone(test_object_ad2.get_file_name())

        #--------------------------------#

        test2_object_ad2=progtuna.tuna.io.adhoc(file_name=self.tests_files_directory +"fichiers/fake_adhoc.ad2")
        test2_object_ad2.read()
        print("test2_object_ad2.get_array_size()=",test2_object_ad2.get_array_size())
        self.assertIsNone(test2_object_ad2.get_array_size())

    def test_read_adhoc_2d(self):
        """Test function read_adhoc_2D"""
        #--------------------------------#
        test_object_ad2=progtuna.tuna.io.adhoc(file_name=self.tests_files_directory +"fichiers_julien/test_adhoc_outlimit.ad2")
        test_object_ad2.read()

        self.assertIsNone(test_object_ad2.get_array())

        #--------------------------------#
        self.log.debug('=> noreshape fonction read_adhoc_2d en cours...' )

        test2_object_ad2=progtuna.tuna.io.adhoc(file_name=self.tests_files_directory +"fichiers_julien/test_adhoc_noreshape.ad2")

        self.assertRaises(ValueError,test2_object_ad2.read())

        self.log.debug('=> noreshape fonction read_adhoc_2d OK' )

    def test_read_adhoc_3d(self):
        """Test function read_adhoc_3D"""
        #------------INFOS--------------------#
        #tuna.generator.adhocfile.adhocfile(adhoc_type=3,
        #file_name='/home/jpenguen/Bureau/PROJETS/TUNA/DOCS/JULIEN/
        #virtual_tuna_juju/tuna/tuna/test/unit/inputfiles_example/
        #fichiers_julien/test_adhoc_outlimit.ad3',
        #array=0,lx=250,ly=1024,lz=1024)
        #-------------------------------------#
        test_object_ad3=progtuna.tuna.io.adhoc(file_name=self.tests_files_directory +"fichiers_julien/test_adhoc_outlimit.ad3")
        test_object_ad3.read()

        self.assertIsNone(test_object_ad3.get_array())

        #------------INFOS--------------------#
        #tuna.generator.adhocfile.adhocfile(adhoc_type=3,
        #file_name='/home/jpenguen/Bureau/PROJETS/TUNA/DOCS/JULIEN/
        #virtual_tuna_juju/tuna/tuna/test/unit/inputfiles_example/
        #fichiers_julien/test_adhoc_dim-3.ad3',
        #array=0,lx=10,ly=10,lz=2,dim=1)
        #-------------------------------------#

        test2_object_ad3=progtuna.tuna.io.adhoc(file_name=self.file_name_ad3_OTHER)
        test2_object_ad3.read(facteur_xyz=False)

        self.assertEqual(np.all(test2_object_ad3.get_array()),np.all(self.array_ad3_OTHER))



    def test_get_photons(self):
        """Test function get_photons"""

        #--------------------------------#
        test_object_ad2=progtuna.tuna.io.adhoc(file_name=self.file_name_ad2)
        test_object_ad2.read()

        self.assertEqual(test_object_ad2.get_photons(),self.photons_ad2)

        #--------------------------------#
        test_object_ad3=progtuna.tuna.io.adhoc(file_name=self.file_name_ad3)
        test_object_ad3.read()

        self.assertEqual(test_object_ad3.get_photons(),self.photons_ad3)

        #--------------------------------#

    def test_discover_adhoc_type(self):
        """Test function __discover_adhoc_type"""

        #--------------------------------#
        test_object_ad2FAKE=progtuna.tuna.io.adhoc(file_name=self.tests_files_directory +"fichiers/adhoc_3_planes.fits")
        test_object_ad2FAKE.read()

        self.assertIsNone(test_object_ad2FAKE.read())

        #--------------------------------#
    def test_set_adhoc_type(self):
        """Test function __discover_adhoc_type"""

        #--------------------------------#
        test_object_ad2=progtuna.tuna.io.adhoc(file_name=self.file_name_ad2)
        test_object_ad2.read()

        self.assertEqual(test_object_ad2.set_adhoc_type(5),5)

        #--------------------------------#


if __name__ == '__main__':
    unittest.main()
