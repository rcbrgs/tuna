.. _example_t251norm_label:

Calibration lamp T251 (normalized)
==================================

This data cube was supplied by Benoît Epinat and corresponds to the calibration lamp imaged before data aquisition in a run made to observe T251. The image was normalized (flattened).

The reduction was made using Tuna v0.11.0. The code to reduce the image was::

  import time
  import tuna
  tuna.log.set_path ( "test.log" )
  tuna.log.verbose ( "file", "DEBUG" )
  
  def reduce_test ( file_name ):
      file_object = tuna.io.read ( file_name )
      start = time.time ( )
      reducer = tuna.tools.phase_map.high_resolution (
          calibration_wavelength = 65989.53125,
          finesse = 12,
          free_spectral_range = 8.36522123894,
          interference_order = 791,
          interference_reference_wavelength = 65627.797852,
          pixel_size = 9,
          scanning_wavelength = 66168.9,
          tuna_can = file_object,
          wrapped_algorithm = tuna.tools.phase_map.barycenter_fast,
          channel_subset = [ 0, 1, 2, 5 ],
          continuum_to_FSR_ratio = 0.125,
          noise_mask_radius = 8,
          dont_fit = False,
          unwrapped_only = False,
          verify_center = None )
      reducer.join ( )
      print ( "Tuna took {:.1f}s to reduce.".format ( time.time ( ) - start ) )
      reducer.plot ( )
      return reducer
  
  test = reduce_test ( "/home/nix/cold_store/fpdata_T251_Benoit_Epinat_2015-07-22/T251_norm.fits" )

Output from ipython was::

  (vtuna)vtuna $ ipython -i reduce_tests.py
  Continuum array created.
  Barycenter done.
  Noise map created with lower_value = 18615.99609375.
  len ( pixel_set_intersections ) == 0, falling back to whole pixel_set
  Could not find intersection between thertiary_chord and concurrent_line. Will attempt to recursively find another set of segments, removing one of the points from current set.
  averaged_concentric_rings = ((241.17854922347954, 244.66439418626365), [284.61367712165372, 214.18521084339031, 106.81156850738181], [0, 2, 3])
  sorted_radii = ['106.81', '214.19', '284.61']
  b_ratio = 2.711343e-04
  inital_gap = 2.61e+07 microns
  channel_gap = 291.7815009986516 microns.
  Airy <|residue|> = 80.3 photons / pixel
  Phase map unwrapped.
  Wavelength calibration done.
  Parabolic model fitted.
  Tuna took 428.3s to reduce.
  
.. image:: images/example_t251norm_1.png
.. image:: images/example_t251norm_2.png
.. image:: images/example_t251norm_3.png
.. image:: images/example_t251norm_4.png
.. image:: images/example_t251norm_5.png
.. image:: images/example_t251norm_6.png
.. image:: images/example_t251norm_7.png
.. image:: images/example_t251norm_8.png
.. image:: images/example_t251norm_9.png
.. image:: images/example_t251norm_10.png
.. image:: images/example_t251norm_11.png
.. image:: images/example_t251norm_12.png
.. image:: images/example_t251norm_13.png
