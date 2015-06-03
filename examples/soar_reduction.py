#!/bin/env ipython3

# Import all modules and classes relevant to a user:
import tuna

tuna.log.set_path ( "soar_025.log" )

file_name = "/home/nix/sync/tuna/sample_data/soar_015_3D.fits"
file_name_unpathed = file_name.split ( "/" ) [ -1 ]
file_name_prefix = file_name_unpathed.split ( "." ) [ 0 ]
can = tuna.io.read ( file_name )

high_res = tuna.tools.phase_map.high_resolution_pipeline ( beam = 2000,
                                                           calibration_wavelength = 6598.9529,
                                                           finesse = 18.79,
                                                           focal_length = 0.1,
                                                           free_spectral_range = 10.886574473319262,
                                                           gap = 2000,
                                                           interference_order = 606.156773751181,
                                                           interference_reference_wavelength = 6598.9529,
                                                           noise_mask_radius = 1,
                                                           scanning_wavelength = 6598.9529,
                                                           tuna_can = can )

tuna.write ( file_name   = file_name_prefix + '_00_original.fits',
             array       = can.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_01_continuum.fits',
             array       = high_res.continuum.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_02_discontinuum.fits',
             array       = high_res.discontinuum.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_03_wrapped_phase_map.fits',
             array       = high_res.wrapped_phase_map.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_04_noise.fits',
             array       = high_res.noise.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_05_borders_to_center_distances.fits',
             array       = high_res.borders_to_center_distances.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_06_order_map.fits',
             array       = high_res.order_map.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_07_unwrapped_phase_map.fits',
             array       = high_res.unwrapped_phase_map.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_08_parabolic_fit.fits',
             array       = high_res.parabolic_fit.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_09_airy_fit.fits',
             array       = high_res.airy_fit.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_09_airy_fit_residue.fits',
             array       = high_res.airy_fit_residue.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_10_substituted_channels.fits',
             array       = high_res.substituted_channels.array,
             file_format = 'fits' )    
tuna.write ( file_name   = file_name_prefix + '_11_wavelength_calibrated.fits',
             array       = high_res.wavelength_calibrated.array,
             file_format = 'fits' )    

interesting_pixels = [ #( 548, 488 ),
    #( 473, 561 ) ]
]
for pixel in interesting_pixels:
    print ( "Profile for pixel %d, %d:" % ( pixel [ 0 ], pixel [ 1 ] ) )
    profile = tuna.tools.phase_map.profile_processing_history ( high_res, ( pixel [ 0 ], pixel [ 1 ] ) )
    for key in profile.keys ( ):
        print ( "step %2d: %s" % ( key, str ( profile [ key ] ) ) )
