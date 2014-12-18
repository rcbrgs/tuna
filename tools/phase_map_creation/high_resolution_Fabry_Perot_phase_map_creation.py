import numpy
from sys import path
path.append ( '/home/nix/sync/tuna' )
from github.file_format import adhoc, file_format, fits
from github.gui         import widget_viewer_2d

class high_resolution_Fabry_Perot_phase_map_creation ( object ):
    def __init__ ( self, file_name = str, *args, **kwargs ):
        super ( high_resolution_Fabry_Perot_phase_map_creation, self ).__init__ ( *args, **kwargs )
        try:
            fits_file = fits.fits ( file_name = file_name )
            self.image_ndarray = fits_file.get_ndarray ( )
        except OSError as e:
            print ( "Could not open file as FITS file." )
            print ( "OSError: %s." % e )
            adhoc_file = adhoc.adhoc ( file_name = file_name )
            self.image_ndarray = adhoc_file.get_ndarray ( )
            print ( "File opened as an ADHOC 2D or 3D file." )

        index_intensity = 0
        index_slice = 1
        if self.image_ndarray.ndim == 3:
            self.max_slice = numpy.ndarray ( shape = ( 2, self.image_ndarray.shape[1], 
                                                          self.image_ndarray.shape[2] ) )
            for x in range ( self.image_ndarray.shape[1] ):
                for y in range ( self.image_ndarray.shape[2] ):
                    for slice in range ( self.image_ndarray.shape[0] ):
                        if  self.max_slice[index_intensity][x][y] < self.image_ndarray[slice][x][y]:
                            self.max_slice[index_intensity][x][y] = self.image_ndarray[slice][x][y]
                            self.max_slice[index_slice][x][y] = slice
        else:
            return

        self.phase_map_ndarray = numpy.ndarray ( shape = ( self.image_ndarray.shape[1], self.image_ndarray.shape[2] ) )

        for x in range ( self.image_ndarray.shape[1] ):
            for y in range ( self.image_ndarray.shape[2] ):
                self.phase_map_ndarray[x][y] = self.max_slice[index_slice][x][y]

        phase_map = file_format.file_format ( )
        self.phase_map_qpixmap = phase_map.pack_ndarray_slice_into_QPixmap ( image_ndarray_slice = self.phase_map_ndarray,
                                                                        image_height = self.image_ndarray.shape[1],
                                                                        image_width = self.image_ndarray.shape[2] )

        #self.image_viewer_2d = widget_viewer_2d.widget_viewer_2d ( )
        #self.image_viewer_2d.set_QPixmap ( phase_map_qpixmap )
        #self.image_viewer_2d.set_title ( "Phase map" )
        #self.image_viewer_2d.display ( )

    def get_qpixmap ( self ):
        return self.phase_map_qpixmap
