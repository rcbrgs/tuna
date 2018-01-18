import sys
sys.path.insert(0,'/home/jpenguen/Bureau/PROJETS/TUNA/DOCS/JULIEN/virtual_tuna_juju/tuna')

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

class testadhoc_ada(unittest.TestCase):
    """Test Processor for unit tests of the adhoc_ada module."""

    def setUp(self):
        """

        """

        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.DEBUG )

        self.tests_files_directory="/home/jpenguen/Bureau/PROJETS/TUNA/DOCS/JULIEN/virtual_tuna_juju/tuna/tuna/test/unit/inputfiles_example/"
        #self.file_name_adt=self.tests_files_directory +'fichiers/G093/G093.ADT'
        self.file_name_adt=self.tests_files_directory +'fichiers/G057/G057.ADT'
        self.metadata = { }
        self.array=None
        self.file_path=dirname ( self.file_name_adt )
        self.photons = { }
        adt = open ( self.file_name_adt, "r" )

        adt_header_lines = []
        for line in adt:
            if line.startswith ( "-----------------------------------------------------------------------------" ):
                break
            adt_header_lines.append ( line )

        adt_notes_lines = []
        for line in adt:
            if line.startswith ( "==>" ):
                break
            adt_notes_lines.append ( line )

        adt_parameters = { }
        for line in adt_header_lines:
            pair_regex = re.search ( "=", line )
            if pair_regex != None:
                pair = line.split ( "=" )
                key = pair[0].replace ( "\n", "" ).strip ( )
                value = pair[1].replace ( "\n", "" ).strip ( )
                adt_parameters [ key ] = [ key, value, "" ]
            else:
                adt_parameters_dict = { }
                key = line.strip ( ).replace ( "\t", " " )
                value = ""
                comment = ""
                adt_parameters [ key ] = [ key, value, comment ]

        adt_notes = ""
        for line in adt_notes_lines:
            adt_notes += line.strip ( ).replace ( "\n", "" )

        adt_parameters_dict = { }
        key = "ADT notes"
        value = adt_notes
        comment = ""
        adt_parameters [ key ] = [ key, value, comment ]

        cycle_parameters = { }
        adt.seek ( 0 )
        for line in adt:
            if line.startswith ( "==>" ):
                split_1 = line.split ( "==>  Beginning channel=" )
                split_2 = split_1[1].split ( " at " )
                acquisition_channel = split_2[0]
                acquisition_start_time = split_2[1]
                next_line = adt.readline ( )
                split_1 = next_line.split ( "Was acquired at " )
                split_2 = split_1[1].split ( ": ch=" )
                acquisition_end_time = split_2[0]
                split_3 = split_2[1].split ( "  cy=" )
                #acquisition_channel = split_3[0]
                split_4 = split_3[1].split ( " QGval=" )
                acquisition_cycle = split_4[0]
                split_5 = split_4[1].split ( "  ph=" )
                acquisition_queensgate_value = split_5[0]
                split_6 = split_5[1].split ( "  fr=" )
                acquisition_photon_count = split_6[0]
                acquisition_fr = split_6[1]

                next_line = adt.readline ( )
                split_1 = next_line.split ( "Cumulated exp=" )
                split_2 = split_1[1].split ( "  phot=" )
                acquisition_cumulated_exposure = split_2[0]
                split_3 = split_2[1].split ( " efficiency=" )
                acquisition_cumulated_photons = split_3[0]
                split_4 = split_3[1].split ( " %  disk=" )
                acquisition_efficiency = split_4[0]
                split_5 = split_4[1].split ( " Mb" )
                acquisition_disk_usage = split_5[1]

                next_line = adt.readline ( )
                split_1 = next_line.split ( "THT=" )
                split_2 = split_1[1].split ( "v  shutter=" )
                acquisition_THT = split_2[0]
                split_3 = split_2[1].split ( "  discri=" )
                acquisition_shutter = split_3[0]
                split_4 = split_3[1].split ( " BlackLevel=" )
                acquisition_discri = split_4[0]
                split_5 = split_4[1].split ( " Whitelevel=" )
                acquisition_blacklevel = split_5[0]
                acquisition_whitelevel = split_5[1]

                cycle = int ( acquisition_cycle.strip ( ) )
                if cycle in cycle_parameters.keys ( ):
                    old_parameters_dict = cycle_parameters [ cycle ]
                    #self.log.debug ( "debug: old_parameters_dict == %s" % str ( old_parameters_dict ) )
                    adt_parameters_dict = { }
                    adt_parameters_dict["cycle"]              = cycle
                    adt_parameters_dict["channel"]            = old_parameters_dict["channel"] + \
                                                                [ int ( acquisition_channel.strip ( ) ) ]
                    adt_parameters_dict["start time"]         = old_parameters_dict["start time"] + \
                                                                [ acquisition_start_time.strip ( ) ]
                    adt_parameters_dict["end time"]           = old_parameters_dict["end time"] + \
                                                                [ acquisition_end_time.strip ( ) ]
                    adt_parameters_dict["Queensgate value"]   = old_parameters_dict["Queensgate value"] + \
                                                                [ int ( acquisition_queensgate_value.strip ( ) ) ]
                    adt_parameters_dict["photon count"]       = old_parameters_dict["photon count"] + \
                                                                [ int ( acquisition_photon_count.strip ( ) ) ]
                    adt_parameters_dict["fr"]                 = old_parameters_dict["fr"] + \
                                                                [ int ( acquisition_fr.strip ( ) ) ]
                    adt_parameters_dict["cumulated exposure"] = old_parameters_dict["cumulated exposure"] + \
                                                                [ acquisition_cumulated_exposure.strip ( ) ]
                    adt_parameters_dict["cumulated photons"]  = old_parameters_dict["cumulated photons"] + \
                                                                [ int ( acquisition_cumulated_photons.strip ( ) ) ]
                    adt_parameters_dict["efficiency"]         = old_parameters_dict [ "efficiency" ] +\
                                                                [ int ( acquisition_efficiency.strip ( ) ) ]
                    adt_parameters_dict["disk usage"]         = old_parameters_dict["disk usage"] + \
                                                                [ acquisition_disk_usage.strip ( ) ]
                    adt_parameters_dict["THT"]                = old_parameters_dict["THT"] + \
                                                                [ int ( acquisition_THT.strip ( ) ) ]
                    adt_parameters_dict["shutter"]            = old_parameters_dict["shutter"] + \
                                                                [ acquisition_shutter.strip ( ) ]
                    adt_parameters_dict["discri"]             = old_parameters_dict["discri"] + \
                                                                [ int ( acquisition_discri.strip ( ) ) ]
                    adt_parameters_dict["blacklevel"]         = old_parameters_dict["blacklevel"] + \
                                                                [ int ( acquisition_blacklevel.strip ( ) ) ]
                    adt_parameters_dict["whitelevel"]         = old_parameters_dict["whitelevel"] + \
                                                                [ int ( acquisition_whitelevel.strip ( ) ) ]
                    #self.log.debug ( "debug: adt_parameters_dict == %s" % str ( adt_parameters_dict ) )
                    cycle_parameters [ cycle ] = adt_parameters_dict
                else:
                    adt_parameters_dict = { }
                    adt_parameters_dict["cycle"]              = cycle
                    adt_parameters_dict["channel"]            = [ int ( acquisition_channel.strip ( ) ) ]
                    adt_parameters_dict["start time"]         = [ acquisition_start_time.strip ( ) ]
                    adt_parameters_dict["end time"]           = [ acquisition_end_time.strip ( ) ]
                    adt_parameters_dict["Queensgate value"]   = [ int ( acquisition_queensgate_value.strip ( ) ) ]
                    adt_parameters_dict["photon count"]       = [ int ( acquisition_photon_count.strip ( ) ) ]
                    adt_parameters_dict["fr"]                 = [ int ( acquisition_fr.strip ( ) ) ]
                    adt_parameters_dict["cumulated exposure"] = [ acquisition_cumulated_exposure.strip ( ) ]
                    adt_parameters_dict["cumulated photons"]  = [ int ( acquisition_cumulated_photons.strip ( ) ) ]
                    adt_parameters_dict["efficiency"]         = [ int ( acquisition_efficiency.strip ( ) ) ]
                    adt_parameters_dict["disk usage"]         = [ acquisition_disk_usage.strip ( ) ]
                    adt_parameters_dict["THT"]                = [ int ( acquisition_THT.strip ( ) ) ]
                    adt_parameters_dict["shutter"]            = [ acquisition_shutter.strip ( ) ]
                    adt_parameters_dict["discri"]             = [ int ( acquisition_discri.strip ( ) ) ]
                    adt_parameters_dict["blacklevel"]         = [ int ( acquisition_blacklevel.strip ( ) ) ]
                    adt_parameters_dict["whitelevel"]         = [ int ( acquisition_whitelevel.strip ( ) ) ]
                    cycle_parameters[cycle] = adt_parameters_dict

        parameters = [ "channel",
                       "start time",
                       "end time",
                       "Queensgate value",
                       "photon count",
                       "fr",
                       "cumulated exposure",
                       "cumulated photons",
                       "efficiency",
                       "disk usage",
                       "THT",
                       "shutter",
                       "discri",
                       "blacklevel",
                       "whitelevel" ]

        for parameter in parameters:
            parameter_ordered_list = [ ]
            for cycle in cycle_parameters.keys ( ):
                parameter_ordered_list += cycle_parameters [ cycle ] [ parameter ]
            adt_parameters_dict = { }
            l_elements = [ parameter, parameter_ordered_list, "" ]
            adt_parameters [ parameter ] = l_elements

            self.metadata [ parameter ] = ( parameter_ordered_list, "" )
            #self.log.debug ( "self.__metadata = %s" % ( str ( self.__metadata ) ) )

        adt.close()

        adt = open ( self.file_name_adt, "r" )


        number_of_channels = len ( set ( self.metadata [ 'channel' ] [ 0 ] ) )
        self.log.debug ( "number_of_channels = %s." % ( number_of_channels ) )

        for line in adt:
            if line.startswith ( "X and Y dimensions : 00512 00512" ):
                dimensions_string = line.split ( " : " )[1]
                dimensions = [ int ( dimensions_string.split ( " " )[0] ),
                               int ( dimensions_string.split ( " " )[1] ) ]
                break
        self.log.debug ( "dimensions = %s." % ( dimensions ) )

        data_files = 0
        adt.seek ( 0 )
        for line in adt:
            if line.startswith ( "==>" ):
                data_files += 1
        self.log.debug ( "data_files = %d." % ( data_files ) )

        photon_files = []
        file_list = listdir ( self.file_path )
        for file_name in file_list:
            if isfile ( join ( self.file_path, file_name ) ):
                if ( file_name.startswith ( ".ADA", -4 ) or
                     file_name.startswith ( ".ada", -4 ) ):
                    photon_files.append ( file_name )

        photon_files.sort ( )
        self.log.debug ( "len ( photon_files ) = %d." % ( len ( photon_files ) ) )


        self.array = numpy.zeros ( shape = ( number_of_channels,
                                                       dimensions[0],
                                                       dimensions[1] ) )
        files_processed = 0
        last_printed = 0
        for element in range ( len ( photon_files ) ):
            file_name_entry = photon_files[element]
            channel = element % number_of_channels
            percentage_done = int ( 10 * files_processed / len ( photon_files ) )
            if last_printed < percentage_done:
                self.log.info ( "Adding photon counts into numpy array: %3d" % ( percentage_done * 10 ) + '%')
                last_printed = percentage_done

            #file_result = self._read_ada ( file_name = file_name_entry, channel = channel )
            #---------------------#
            if channel == -1:
                return

            file_path = join ( self.file_path, file_name_entry)

            photon_positions = numpy.fromfile ( file_path, dtype = numpy.int16 )


            # We know the file is organized with y,x,y,x,y,x...
            # So the file will have size / 2 photons.

            #photon_hits = photon_positions.reshape ( photon_positions.size / 2, 2 )
            photon_hits = photon_positions.reshape ( int(photon_positions.size / 2), 2 ) #correction add by Julien Penguen 12/07/2017

            for photon in range ( photon_hits.shape[0] ):
                x = photon_hits[photon][0]
                y = photon_hits[photon][1]
                self.array[channel][x][y] += 1
            # photons table:
                s_key = str ( channel ) + ":" + str ( x ) + ":" + str ( y )
                if s_key not in self.photons.keys ( ):
                    photon = { }
                    photon [ 'channel' ] = channel
                    photon [ 'x'       ] = x
                    photon [ 'y'       ] = y
                    photon [ 'photons' ] = 1
                    self.photons [ s_key ] = photon
                else:
                    self.photons [ s_key ] [ 'photons' ] += 1


            #---------------------#
            files_processed += 1

        pass


    def test_nonexisting_file ( self ):
        """test if inputfile is non existing"""
        file_name = self.tests_files_directory + "fichiers/nonexistingfile.ADT"
        self.assertRaises ( OSError, lambda: progtuna.tuna.io.ada(file_name=file_name).read())

    def test_empty_file ( self ):
        """test if inputfile is empty"""
        file_name=self.tests_files_directory +"fichiers_julien/G000/G000.ADT"
        self.assertIsNone(progtuna.tuna.io.ada(file_name=file_name).read())
        print("test if inputfile is empty ok!")


    def test_read( self ):
        """test function read"""
        file_name=self.tests_files_directory +"fichiers_julien/test_adhoc_dim-3.ad3"
        file_name2=self.tests_files_directory +"fichiers/G093/G093.ADT"
        self.assertIsNone(progtuna.tuna.io.ada(file_name=file_name).read())
        self.assertIsNone(progtuna.tuna.io.ada(file_name=file_name2).read(channel_test=-1))


    def test_get_metadata( self ):
        """test function _read_adt_metadata"""

        test_object_ADT=progtuna.tuna.io.ada(file_name=self.file_name_adt)
        test_object_ADT.read()
        self.assertEqual(test_object_ADT.get_metadata(),self.metadata)
        print("get_metadata ok for adt!!")

    def test_get_array( self ):
        """test function get_array"""

        file_name=self.tests_files_directory +"fichiers/G093/G093.ADT"
        test_object_ADT=progtuna.tuna.io.ada(file_name=file_name)
        test_object_ADT.read()
        self.assertEqual(np.all(test_object_ADT.get_array()),np.all(self.array))
        print("get_array ok for adt!!")

    def test_get_photons( self ):
        """test function get_photons"""


        test_object_ADT=progtuna.tuna.io.ada(file_name=self.file_name_adt)
        test_object_ADT.read()
        self.assertEqual(np.all(test_object_ADT.get_photons()),np.all(self.photons))
        print("get_photons ok for adt!!")
