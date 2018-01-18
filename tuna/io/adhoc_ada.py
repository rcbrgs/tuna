# -*- coding: utf-8 -*-
"""
This module's scope covers operations related to ADHOC ADA files.
"""
import os
from .file_reader import file_reader

import logging
import numpy
from numpy import shape
from os import listdir
from os.path import dirname, isfile, join
import re
import tuna
import IPython
import math
import warnings
import matplotlib.pyplot as plt

class ada ( file_reader ):
    """
    This class's responsibility is to read files in ADHOC format ADA.

    The ADHOC file formats were developed for use with the ADHOC software solution, developed at LAM by Jacques Boulesteix.

    Its constructor has the following signature:

    Parameters:

    * array : numpy.ndarray : defaults to None
        An array containing the image data; this parameter is useful to convert a known array to a photon table.

    * file_name : string : defaults to None
        To obtain data from a file, it must contain the path to a valid ADT file, which will contain the metadata and the names for the individual ADA files.

    Example usage::

        import tuna
        raw = tuna.io.ada ( file_name = "tuna/tuna/test/unit/unit_io/G093/G093.ADT" )
        raw.read ( )
        raw.get_array ( )
        raw.get_metadata ( )
    """

    def __init__ ( self,
                   array = None,
                   file_name = None ):
        self.__version__ = "0.3.0"
        self.__changelog = {
            "0.3.0" : "add news functions + corrections.",
            "0.2.0" : "Tuna 0.14.0 : improved docstrings.",
            "0.1.1" : "Updated docstrings to new style documentation.",
            '0.1.0' : "Initial changelogged version."
            }
        super ( ada, self ).__init__ ( )
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )

        self.__file_name = file_name
        self.__array = array
        self.__metadata = { }
        self.__photons = { }
        self.__file_path = dirname(file_name)

    def get_array ( self ):
        """
        This method's goal is to return the input array.

        Returns:

        * self.__array : numpy.ndarray
            The array containing the current data.
        """
        return self.__array

    def get_metadata ( self ):
        """
        This method's goal is to return the metadata structure.

        Returns:

        * self.__metadata : dictionary
            A dictionary containing the metadata as read from the file.
        """
        return self.__metadata

    def get_photons ( self ):
        """
        This method's goal is to Return a photon table corresponding to the data read.

        Returns:

        * self.__photons : dictionary
            A dictionary containing a row for each photon count.
        """
        return self.__photons

    def read(self, channel_test = 1):
        """
        This method's goal is to validate input and start the reading procedure.
        """
        self.log.debug ( tuna.log.function_header ( ) )

        if self.__file_name:

            try:
                self.__file_object = open ( self.__file_name, "r" )
                self.__file_object.seek ( 0, os.SEEK_END )
                if self.__file_object.tell ( ) < 256:
                    self.log.error ( "File does not contain valid numpy array." )
                    return
                self.__file_object.close ( )

            except OSError as e:
                self.log.error ( "OSError: %s" % str ( e ) )
                raise

            if ( self.__file_name.lower ( ).startswith ( ".adt", -4 ) ):
                #self._read_adt ( )
                self._read_adt (channel_test= channel_test)
            else:
                self.log.warning ( "File name %s does not have .ADT or .adt suffix, aborting." % ( self.__file_name ) )
                return

    def _read_adt ( self,channel_test=1 ):
        """
        This method's goal is to read a file as an ADT file.
        """
        self.log.debug ( tuna.log.function_header ( ) )

        self.__file_path = dirname ( self.__file_name )
        self.log.debug ( "self.__file_path = %s." % ( self.__file_path ) )

        self._read_adt_metadata ( )

        adt = open ( self.__file_name, "r" )

        number_of_channels = len ( set ( self.__metadata [ 'channel' ] [ 0 ] ) )
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
        file_list = listdir ( self.__file_path )
        for file_name in file_list:
            if isfile ( join ( self.__file_path, file_name ) ):
                if ( file_name.startswith ( ".ADA", -4 ) or
                     file_name.startswith ( ".ada", -4 ) ):
                    photon_files.append ( file_name )

        photon_files.sort ( )
        self.log.debug ( "len ( photon_files ) = %d." % ( len ( photon_files ) ) )

        self.__array = numpy.zeros ( shape = ( number_of_channels,
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

            if channel_test == -1:
                file_result = self._read_ada ( file_name = file_name_entry, channel = channel_test )
            else:

                file_result = self._read_ada ( file_name = file_name_entry, channel = channel )

            files_processed += 1

    def _read_ada ( self, channel = -1, file_name = None ):
        """
        This method's goal is to read an ADHOC .ADA file containing photon counts.

        Originally developed by Benoît Epinat, modified by Renato Borges.

        Parameters:

        * channel : integer : defaults to -1
            An ADA file will often encode the photon counts for a given channel. This channel number must be specified so that the photon table can be constructed with this information. If the default value of -1 is used, the method will return immediately.

        * file_name : string : defaults to None
            The file_name must represent a valid ADA file.
        """
        self.log.debug ( tuna.log.function_header ( ) )

        if channel == -1:
            return

        file_path = join ( self.__file_path, file_name )

        photon_positions = numpy.fromfile ( file_path, dtype = numpy.int16 )

        # We know the file is organized with y,x,y,x,y,x...
        # So the file will have size / 2 photons.

        photon_hits = photon_positions.reshape ( int(photon_positions.size / 2), 2 )

        for photon in range ( photon_hits.shape[0] ):
            x = photon_hits[photon][0]
            y = photon_hits[photon][1]
            self.__array[channel][x][y] += 1

            # photons table:
            s_key = str ( channel ) + ":" + str ( x ) + ":" + str ( y )
            if s_key not in self.__photons.keys ( ):
                photon = { }
                photon [ 'channel' ] = channel
                photon [ 'x'       ] = x
                photon [ 'y'       ] = y
                photon [ 'photons' ] = 1
                self.__photons [ s_key ] = photon
            else:
                self.__photons [ s_key ] [ 'photons' ] += 1

        #it seems that the first frame is duplicated
        #it would be nice to be able to display the creation of the image photon by photon

    def _read_adt_metadata ( self ):
        """
        This method's goal is to extract metadata from an ADT file.
        """
        self.log.debug ( tuna.log.function_header ( ) )

        adt = open ( self.__file_name, "r" )

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

            self.__metadata [ parameter ] = ( parameter_ordered_list, "" )
            #self.log.debug ( "self.__metadata = %s" % ( str ( self.__metadata ) ) )
