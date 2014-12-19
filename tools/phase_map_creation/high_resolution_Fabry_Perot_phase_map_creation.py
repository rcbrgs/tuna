import numpy
from sys import path
path.append ( '/home/nix/sync/tuna' )
from github.file_format import adhoc, file_format, fits
from github.gui         import widget_viewer_2d

class high_resolution_Fabry_Perot_phase_map_creation ( object ):
    def __init__ ( self, file_name = str, log = None, *args, **kwargs ):
        super ( high_resolution_Fabry_Perot_phase_map_creation, self ).__init__ ( *args, **kwargs )
        if log:
            self.log = log
        else:
            self.log = print

        fits_file = fits.fits ( file_name = file_name, log = self.log )
        fits_file.read ( )
        if fits_file.is_readable ( ):
            self.image_ndarray = fits_file.get_image_ndarray ( )
            current_file = fits_file
        else:
            adhoc_file = adhoc.adhoc ( file_name = file_name, log = self.log )
            adhoc_file.read ( )
            if adhoc_file.is_readable ( ):
                self.image_ndarray = adhoc_file.get_image_ndarray ( )
                current_file = adhoc_file
            else:
                self.log ( "Unable to open file %s." % file_name )
                return

        index_intensity = 0
        index_slice = 1
        if self.image_ndarray.ndim == 3:
            self.max_slice = numpy.ndarray ( shape = ( 2, self.image_ndarray.shape[1], 
                                                          self.image_ndarray.shape[2] ) )
            max_x = self.image_ndarray.shape[1]
            last_printed = 0
            for x in range ( self.image_ndarray.shape[1] ):
                percentage_done = int ( 100 * x / max_x )
                if not percentage_done == last_printed:
                    self.log ( "Finding spectral peak %2d" % percentage_done + '%' )
                    last_printed = percentage_done
                for y in range ( self.image_ndarray.shape[2] ):
                    for slice in range ( self.image_ndarray.shape[0] ):
                        if  self.max_slice[index_intensity][x][y] < self.image_ndarray[slice][x][y]:
                            self.max_slice[index_intensity][x][y] = self.image_ndarray[slice][x][y]
                            self.max_slice[index_slice][x][y] = slice
        else:
            self.log ( "Image does not have 3 dimensions, aborting." )
            return

        self.phase_map_ndarray = numpy.ndarray ( shape = ( self.image_ndarray.shape[1], self.image_ndarray.shape[2] ) )
        
        self.log ( "Extracting phase map image from phase map table." )
        for x in range ( self.image_ndarray.shape[1] ):
            for y in range ( self.image_ndarray.shape[2] ):
                self.phase_map_ndarray[x][y] = self.max_slice[index_slice][x][y]

    def get_image_ndarray ( self ):
        return self.phase_map_ndarray
