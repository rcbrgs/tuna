from .file_reader import file_reader
import numpy
from os import listdir
from os.path import dirname, isfile, join
import re

class ada ( file_reader ):
    """
    Class for reading files in ADHOC format ADA.

    The ADHOC file formats were developed for use with the ADHOC software solution,
    developed at LAM by Jacques Boulesteix.
    """

    def __init__ ( self, array = None, log = print, file_name = None ):
        super ( ada, self ).__init__ ( )
        self.__file_name = file_name
        self.__array = array
        self.__metadata = { }
        self.log = log

    def get_array ( self ):
        return self.__array

    def get_metadata ( self ):
        return self.__metadata

    def read ( self ):
        if self.__file_name != None:
            if ( self.__file_name.startswith ( ".ADT", -4 ) or
                 self.__file_name.startswith ( ".adt", -4 ) ):
                self.read_adt ( )
        else:
            self.log ( "File name %s does not have .ADT or .adt suffix, aborting." % ( self.__file_name ) )

    def read_adt ( self ):
        self.__file_path = dirname ( self.__file_name )
        self.log ( "self.__file_path = %s." % ( self.__file_path ) )
        
        self.read_adt_metadata ( )

        adt = open ( self.__file_name, "r" )
               
        number_of_channels = int ( self.__metadata['Number of channels'] )
        self.log ( "number_of_channels = %s." % ( number_of_channels ) )

        for line in adt:
            if line.startswith ( "X and Y dimensions : 00512 00512" ):
                dimensions_string = line.split ( " : " )[1]
                dimensions = [ int ( dimensions_string.split ( " " )[0] ),
                               int ( dimensions_string.split ( " " )[1] ) ]
                break
        self.log ( "dimensions = %s." % ( dimensions ) )
       
        data_files = 0
        adt.seek ( 0 )
        for line in adt:
            if line.startswith ( "==>" ):
                data_files += 1
        self.log ( "data_files = %d." % ( data_files ) )

        photon_files = []
        file_list = listdir ( self.__file_path )
        for file_name in file_list:
            if isfile ( join ( self.__file_path, file_name ) ):
                if ( file_name.startswith ( ".ADA", -4 ) or
                     file_name.startswith ( ".ada", -4 ) ):
                    photon_files.append ( file_name )

        photon_files.sort ( )
        self.log ( "len ( photon_files ) = %d." % ( len ( photon_files ) ) )

        
        self.__array = numpy.zeros ( shape = ( number_of_channels,
                                                       dimensions[0], 
                                                       dimensions[1] ) )
        files_processed = 0
        last_printed = 0
        for element in range ( len ( photon_files ) ):
            file_name_entry = photon_files[element]
            channel = element % number_of_channels
            percentage_done = int ( 100 * files_processed / len ( photon_files ) )
            if last_printed < percentage_done:
                self.log ( "Adding photon counts into numpy array: %3d" % ( percentage_done ) + '%')
                last_printed = percentage_done

            file_result = self.read_ada ( file_name = file_name_entry, channel = channel )
            files_processed += 1
                
    def read_ada ( self, channel = -1, file_name = None ):
        """
        Attempts to read an ADHOC .ADA file containing photon counts.

        Returns a two-dimensional numpy array.

        Originally developed by Benoît Epinat, modified by Renato Borges.
        """
        
        if channel == -1:
            return

        if file_name == None:
            return
        
        file_path = join ( self.__file_path, file_name )
        photon_positions = numpy.fromfile ( file_path, dtype = numpy.int16 )
        # We know the file is organized with y,x,y,x,y,x... 
        # So the file will have size / 2 photons.
        photon_hits = photon_positions.reshape ( photon_positions.size / 2, 2 )
        for photon in range ( photon_hits.shape[0] ):
            x = photon_hits[photon][0]
            y = photon_hits[photon][1]
            self.__array[channel][x][y] += 1                
        #it seems that the first frame is duplicated
        #it would be nice to be able to display the creation of the image photon by photon

    def read_adt_metadata ( self ):
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
                adt_parameters[key] = value
                #self.log ( "...............%s" % ( line ) )
                #self.log ( "adt_parameters[%s] = %s" % ( key, adt_parameters[key] ) )
            else:
                adt_parameters[line] = ""

        adt_notes = ""
        for line in adt_notes_lines:
            adt_notes += line.strip ( ).replace ( "\n", "" )

        if "ADT notes" not in adt_parameters.keys ( ):
            adt_parameters["ADT notes"] = adt_notes
            
        self.__metadata = adt_parameters
