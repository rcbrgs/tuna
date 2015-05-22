import logging
import numpy
import os
import tuna
import unittest

class unit_test_pipeline_high_resolution ( unittest.TestCase ):
    def setUp ( self ):
        tuna.log.set_path ( "../nose.log" )

    def test_pipeline ( self ):
        file_name = "/home/nix/sync/tuna/sample_data/G094.AD3"
        file_name_unpathed = file_name.split ( "/" ) [ -1 ]
        file_name_prefix = file_name_unpathed.split ( "." ) [ 0 ]

        can = tuna.io.read ( file_name )
        high_res = tuna.tools.phase_map.high_resolution_pipeline ( beam = 450,
                                                                   calibration_wavelength = 6598.953125,
                                                                   finesse = 15.,
                                                                   focal_length = 0.1,
                                                                   free_spectral_range = 8.36522123894,
                                                                   gap = 0.01,
                                                                   initial_gap = 1904.,
                                                                   interference_order = 791,
                                                                   interference_reference_wavelength = 6562.7797852,
                                                                   pixel_size = 9,
                                                                   channel_threshold = 1, 
                                                                   bad_neighbours_threshold = 7, 
                                                                   noise_mask_radius = 10,
                                                                   scanning_wavelength = 6616.89,
                                                                   tuna_can = can )

        self.assertTrue ( high_res.wavelength_calibrated.array [ 0 ] [ 0 ] > 95 )
        self.assertTrue ( high_res.wavelength_calibrated.array [ 0 ] [ 0 ] < 105 )
        self.assertTrue ( high_res.rings_center [ 0 ] > 200 )
        self.assertTrue ( high_res.rings_center [ 0 ] < 240 )
        self.assertTrue ( high_res.rings_center [ 1 ] > 230 )
        self.assertTrue ( high_res.rings_center [ 1 ] < 270 )

    def tearDown ( self ):
        pass

if __name__ == '__main__':
    unittest.main ( )
