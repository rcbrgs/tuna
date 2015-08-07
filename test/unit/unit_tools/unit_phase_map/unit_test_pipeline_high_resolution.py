import logging
import numpy
import os
import tuna
import unittest

class unit_test_pipeline_high_resolution ( unittest.TestCase ):
    def setUp ( self ):
        tuna.log.set_path ( "nose.log" )

    def test_pipeline ( self ):
        #file_name = "test/unit/unit_io/partial_4_planes.fits"
        file_name = "test/unit/unit_io/adhoc_3_planes.fits"
        file_name_unpathed = file_name.split ( "/" ) [ -1 ]
        file_name_prefix = file_name_unpathed.split ( "." ) [ 0 ]

        can = tuna.io.read ( file_name )
        from tuna.tools.phase_map import barycenter_fast
        tuna.log.verbose ( "console", "INFO" )
        high_res = tuna.tools.phase_map.high_resolution ( calibration_wavelength = 6598.953125,
                                                          finesse = 15.,
                                                          free_spectral_range = 8.36522123894,
                                                          interference_order = 791,
                                                          interference_reference_wavelength = 6562.7797852,
                                                          pixel_size = 9,
                                                          noise_mask_radius = 1,
                                                          scanning_wavelength = 6616.89,
                                                          tuna_can = can,
                                                          wrapped_algorithm = barycenter_fast,
                                                          dont_fit = True )
        high_res.join ( )
        log = logging.getLogger ( __name__ )
        log.info ( "high_res.discontinuum.array [ 0 ] = %s" % str ( high_res.discontinuum.array [ 0 ] ) )
        log.info ( "high_res.wavelength_calibrated.array [ 0 ] [ 0 ] == %f" % high_res.wavelength_calibrated.array [ 0 ] [ 0 ] )
        self.assertTrue ( high_res.wavelength_calibrated.array [ 0 ] [ 0 ] > 25. )
        self.assertTrue ( high_res.wavelength_calibrated.array [ 0 ] [ 0 ] < 30. )
        log.info ( "high_res.rings_center ==%s" % str ( high_res.rings_center ) )
        self.assertTrue ( high_res.rings_center [ 0 ] > 220 )
        self.assertTrue ( high_res.rings_center [ 0 ] < 240 )
        self.assertTrue ( high_res.rings_center [ 1 ] > 190 )
        self.assertTrue ( high_res.rings_center [ 1 ] < 210 )

    def tearDown ( self ):
        pass

if __name__ == '__main__':
    unittest.main ( )
