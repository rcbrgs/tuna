.. _example_t251norm_label:

Calibration lamp T251 (normalized)
==================================

This data cube was supplied by Benoît Epinat and corresponds to the calibration lamp imaged before data aquisition in a run made to observe T251. The image was normalized (flattened).

The reduction was made using Tuna version 0.16.4. The code to reduce the image was::

  import time
  import tuna
  tuna.log.set_path ( "test.log" )
  tuna.log.verbose ( "file", "DEBUG" )
  
  def reduce_test ( file_name ):
    file_object = tuna.io.read ( file_name )
    start = time.time ( )
    reducer = tuna.pipelines.calibration_lamp_high_resolution.reducer (
      calibration_wavelength = 6598.953125,
      finesse = 12,
      free_spectral_range = 8.36522123894,
      interference_order = 791,
      interference_reference_wavelength = 6562.7797852,
      pixel_size = 9,
      scanning_wavelength = 6616.89,
      tuna_can = file_object,
      channel_subset = [ 0, 1, 2, 5 ],
      continuum_to_FSR_ratio = 0.125,
      noise_mask_radius = 8,
      dont_fit = False,
      unwrapped_only = False,
      verify_center = None )
    reducer.join ( )
    print ( "Tuna took {:.1f}s to reduce.".format ( time.time ( ) - start ) )
    return reducer
  
  test = reduce_test ( "/home/nix/cold_store/fpdata_T251_Benoit_Epinat_2015-07-22/T251_norm.fits" )
  tuna.tools.plot_high_res ( test )

Output from ipython was::

  Log file set to test.log.
  Handler <logging.FileHandler object at 0x7fbf76580860> set to 10.
  Starting tuna.pipelines.calibration_lamp_high_resolution pipeline.
  Continuum array created.
  Barycenter done.
  Noise map created with lower_value = 18615.99609375.
  Searching for concentric rings in plane 0.
  Could not find intersection between thertiary_chord and concurrent_line. Will attempt to recursively find another set of segments, removing one of the points from current set.
  Concentric rings structure: ((241.08484490127751, 244.08963239387131), [214.18521084339031, 106.81156850738181], [2, 3])
  Ring structure obtained from plane where borders occupy 50% of the array.
  sorted_radii = ['106.81', '214.19']
  inital_gap = 2.61e+06 microns
  channel_gap = 29.176824392052367 microns.
  Airy <|residue|> = 80.3 photons / pixel
  sorted_distances == [100.90803532938621, 211.26671576925855, 270.282645933774]
  Phase map unwrapped.
  Wavelength calibration done.
  Parabolic model fitted.
  Tuna took 157.7s to reduce.
  /home/nix/vtuna/lib/python3.4/site-packages/matplotlib/pyplot.py:516: RuntimeWarning: More than 20 figures have been opened. Figures created through the pyplot interface (`matplotlib.pyplot.figure`) are retained until explicitly closed and may consume too much memory. (To control this warning, see the rcParam `figure.max_open_warning`).
  max_open_warning, RuntimeWarning)

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
.. image:: images/example_t251norm_14.png
.. image:: images/example_t251norm_15.png
.. image:: images/example_t251norm_16.png
.. image:: images/example_t251norm_17.png
.. image:: images/example_t251norm_18.png
.. image:: images/example_t251norm_19.png
.. image:: images/example_t251norm_20.png
.. image:: images/example_t251norm_21.png
.. image:: images/example_t251norm_22.png
.. image:: images/example_t251norm_23.png
