.. _example_30_Doradus_SOAR_March_2015:

30 Doradus SOAR March 2015
==========================

This data was acquired on March 2015 by Claudia Mendes de Oliveira, Philipe Amram, S. Torres and Bruno Quint.

The full set contains 35 data-taking runs, some of which are calibration and some are observation, according to the run notes::
  
  # Folder     Source   Filter    Image/Channel   # Sweeps   Binsize    z0:dz:nz  exptime  comments
  
  001          NeLamp  6600/20-BTFI      1            1        4x4      663:12:62    1    header for filter is incorrect, the correct filter is 6600/20 and not 6563/75 as the header says
  002          NeLamp  6600/20-BTFI      1            1        4x4      843:6:62      1    header for filter is incorrect, same as above
  003          NeLamp  6600/20-BTFI      1            1        4x4      842:6:62      1    header for filter is incorrect
  004          NeLamp  6600/20-BTFI      1            1        4x4      840:6:62      1    same as above
  005          NeLamp  6600/20-BTFI      1            1        4x4      836:6:62      1    same as above
  006          NeLamp  6600/20-BTFI      1            1        4x4     1229:7:62      1    same as above - BCV go down from 1229 to 809
  007          NeLamp  6600/20-BTFI      1            1        4x4     1203:7:62      1    same as above 
  008          NeLamp  6600/20-BTFI      1            1        4x4     1200:6:62      1    same as above
  009          NeLamp  6600/20-BTFI      1            1        4x4     1198:6:62      1    same as above
  010
  011          Bias                      1           40        4x4                    0    observation title is wrong - header says Calibration lamp - Ne but it is bias
  012          NeLamp  6600/20-BTFI      1            1        4x4     1200:6:42      1    now header is correct
  013          Neon Bulb 6600/20-BTFI    1            1        4x4     1200:6:46      1  
  014          NeLamp  6600/20-BTFI      1            1        4x4     1200:6:38      1
  015          NeLamp  6600/20-BTFI      1            1        4x4     1200:9:40      1
  016  12 5min darks
  017 8 x 8 
  018 skyflats 6568-20 1s exposures median counts = 30000 40 images
  019 skyflats 6578-19 1s exposures median counts = 35000 40 images - strange jet in the middle
  020 skyflats 6600-19 1s exposures median counts = 20000 40 images - strange crossed jets in the middle
  021 skyflats circular88 1s exposures
  022 skyflats 6578-19 1s 3000 counts still the same pattern
  023 skyflats 6578-19 3s
  024          30Dor    6568-20-2x2       1          1         4x4                  120.0 
  stopped the laser in frame 24
  stopped at frame 36 re-started the script (36b is bad given that it has high dark current)
  Finished with airmass 1.5
  025         NeLamp  6568/20-2x2      1            1        4x4     1200:9:40      1 we used the wrong filter - no lines
  026         Arp 244-Antennae 6600/20    1          1        4x4     1200:9:40     150.0  we stopped at the end of 8 given that there was an event and the laser had to be stopped
  027         Ne lamp 6600/20-BTFI        1          1        4x4     1200:9:40      1 wrong title
  T 03:15 UT03:31 cirrus AM final = 1.07
  028        Ne lamp 6600/20-BTFI         1          1        4x4     1200:9:40     1
  029        N3621  6578-19              1          1        4x4     1200:9:40     150.0 wrong title (it says pointing)
  030        N3621 - sky  6578-19        1          1        4x4     1200:9:40     10.0 wrong title
  4 arcminutes west of the galaxy
  031        NeLamp 6600/20-BTFI         1          1        4x4     1200:9:40     1   
  032        M17         6568-20         1          1        4x4     1200:9:40     80  wrong title
  033        NeLamp for M17 6600-19      1          1        4x4     1200:9:40     1  wrong ttle
  034        N10  Halpha image
  034        N10  R image
  035        flats for 6578-19 and 6600-19 (probably only last 2 are 6600-19)

The authors also provided the following parameters for the calibration::

  ## Based on cube015.fits at [153,578] (center)
  Wavelength: 6598.9529 A
  FSR_channel: 40.00 channels
  GFWHM_channels: 2.39 channels
  Center_channels: 18.67 channels
  
  ## Fabry-Perot information
  Gap size: 200 um = 2000000 A
  
  ## Order determination
  m(6598) = (2 * 200 um) / 6598.9529 A
  m(6598) = 606.156773751181
  
  ## FSR_wavelength
  FSR_wavelength = 6598.9529 A / m(6598)
  FSR_wavelength = 6598.9529 A / 606.156773751181
  FSR_wavelength = 10.886544844104602 A
  
  ## Sampling 
  Sampling = FSR_wavelength / FSR_channels = 10.886544844104602 A / 40 channels
  Sampling = 0.27216362110261505
  header['CRPIX3'] = 0.27216362110261505
  header['CD3_3'] = 0.27216362110261505
  header['C3_3'] = 0.27216362110261505
  
  ## Reference Pixel
  header['CRPIX3'] = round(Center_channels) = 19
  
  ## Reference Pixel value
  header['CRVAL3'] = 6598.9529 A +/- m * FSR_wavelength
  header['CRVAL3'] = 6598.9529 A - 3 * FSR_wavelength 
  header['CRVAL3'] = 6566.293265467686 A
  
  ## With this, we have the wavelength calibration:
  header['DISPAXIS']=3
  header['CRPIX3']  = 19
  header['CRVAL3']  = 6566.293265467686 A
  header['CRPIX3']  = 0.27216362110261505
  header['CD3_3']   = 0.27216362110261505
  header['C3_3']    = 0.27216362110261505

Run #001
--------

This run is a Neon lamp calibration, according to the notes.

The values for the parameter in the calibration ( calibration_wavelength, free_spectral_range, interference_order, interference_reference_wavelength, pixel_size, and scanning_wavelength ) were obtained from the parameter file.

The reduction was made using Tuna version 0.16.0. The code to reduce the image was::

    import numpy
    import time
    import tuna
    
    tuna.log.set_path ( "/home/nix/example_Dor30_SOAR.log" )
    tuna.log.verbose ( "file", "DEBUG" )
    tuna.log.verbose ( "console", "INFO" )

    # 1. Create a dictionary with the file names associated with each channel
    
    path = "/home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001"
    counter = 277
    channels_files = { }
    for channel_index in range ( 62 ):
        file_index = channel_index + 1
	file_name = path + "/fp_sami_C0{:02d}".format ( file_index ) + "." + str ( counter + file_index ) + ".fits"
	channels_files [ channel_index ] = file_name

    # 2. Reduce the raw cube.

    def reduce_calibration ( file_names_per_channel ):
        start = time.time ( )
	reducer = tuna.pipelines.soar_sami_calibration_lamp.reducer (
	    calibration_wavelength = 6566.293265467686,
	    file_names_per_channel = file_names_per_channel,
	    finesse = 12,
	    free_spectral_range = 10.886544844104602,
	    interference_order = 606.156773751181,
	    interference_reference_wavelength = 6598.9529,
	    min_rings = 2,
	    pixel_size = 19,
	    scanning_wavelength = 6598.9529,
	    channel_subset = [ ],
	    continuum_to_FSR_ratio = 0.125,
	    noise_mask_radius = 8,
	    dont_fit = False,
	    unwrapped_only = False,
	    verify_center = None )
	reducer.join ( )
	print ( "Tuna took {:.1f}s to reduce.".format ( time.time ( ) - start ) )
	reducer.plot ( )
	return reducer

    pipeline_result = reduce_calibration ( channels_files )
  
Output from ipython was::

  Log file set to /home/nix/example_Dor30_SOAR.log.
  Handler <logging.FileHandler object at 0x7fb9200128d0> set to 10.
  Handler <logging.StreamHandler object at 0x7fb91c6a26d8> set to 20.
  Starting tuna.pipelines.soar_sami_calibration_lamp pipeline.
  Data from 'SOAR' observatory, 'SOAR telescope' telescope, 'SAM' instrument.
  Processing channel 0 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C001.278.fits.
  Processing channel 1 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C002.279.fits.
  Processing channel 2 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C003.280.fits.
  Processing channel 3 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C004.281.fits.
  Processing channel 4 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C005.282.fits.
  Processing channel 5 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C006.283.fits.
  Processing channel 6 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C007.284.fits.
  Processing channel 7 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C008.285.fits.
  Processing channel 8 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C009.286.fits.
  Processing channel 9 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C010.287.fits.
  Processing channel 10 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C011.288.fits.
  Processing channel 11 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C012.289.fits.
  Processing channel 12 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C013.290.fits.
  Processing channel 13 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C014.291.fits.
  Processing channel 14 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C015.292.fits.
  Processing channel 15 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C016.293.fits.
  Processing channel 16 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C017.294.fits.
  Processing channel 17 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C018.295.fits.
  Processing channel 18 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C019.296.fits.
  Processing channel 19 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C020.297.fits.
  Processing channel 20 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C02[71/8823]s.
  Processing channel 21 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C022.299.fits.
  Processing channel 22 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C023.300.fits.
  Processing channel 23 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C024.301.fits.
  Processing channel 24 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C025.302.fits.
  Processing channel 25 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C026.303.fits.
  Processing channel 26 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C027.304.fits.
  Processing channel 27 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C028.305.fits.
  Processing channel 28 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C029.306.fits.
  Processing channel 29 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C030.307.fits.
  Processing channel 30 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C031.308.fits.
  Processing channel 31 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C032.309.fits.
  Processing channel 32 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C033.310.fits.
  Processing channel 33 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C034.311.fits.
  Processing channel 34 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C035.312.fits.
  Processing channel 35 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C036.313.fits.
  Processing channel 36 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C037.314.fits.
  Processing channel 37 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C038.315.fits.
  Processing channel 38 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C039.316.fits.
  Processing channel 39 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C040.317.fits.
  Processing channel 40 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C041.318.fits.
  Processing channel 41 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C042.319.fits.
  Processing channel 42 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C043.320.fits.
  Processing channel 43 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C044.321.fits.
  Processing channel 44 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C045.322.fits.
  Processing channel 45 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C046.323.fits.
  Processing channel 46 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C047.324.fits.
  Processing channel 47 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C048.325.fits.
  Processing channel 48 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C049.326.fits.
  Processing channel 49 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C050.327.fits.
  Processing channel 50 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C051.328.fits.
  Processing channel 51 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C052.329.fits.
  Processing channel 52 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C053.330.fits.
  Processing channel 53 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C054.331.fits.
  Processing channel 54 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C055.332.fits.
  Processing channel 55 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C056.333.fits.
  Processing channel 56 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C057.334.fits.
  Processing channel 57 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C058.335.fits.
  Processing channel 58 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C059.336.fits.
  Processing channel 59 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C060.337.fits.
  Processing channel 60 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C061.338.fits.
  Processing channel 61 from raw file /home/nix/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C062.339.fits.
  Continuum array created.
  Barycenter done.
  Noise map created with lower_value = 128204.70999999999.
  len ( pixel_set_intersections ) == 0, falling back to whole pixel_set
  averaged_concentric_rings = ((577.9250117243655, 165.60940932914605), [795.78839923110331, 126.57113826578056], [0, 1
  ])
  sorted_radii = ['126.57', '795.79']
  inital_gap = 1.99e+06 microns
  channel_gap = -2.2900057500078073 microns.
  Airy <|residue|> = 2301.0 photons / pixel
  Phase map unwrapped.
  Wavelength calibration done.
  Parabolic model fitted.
  Tuna took 1224.9s to reduce. 
  
The plots produced in the run were the following:
  
.. image:: images/example_Dor30_SOAR_1.png
.. image:: images/example_Dor30_SOAR_2.png
.. image:: images/example_Dor30_SOAR_3.png
.. image:: images/example_Dor30_SOAR_4.png
.. image:: images/example_Dor30_SOAR_5.png
.. image:: images/example_Dor30_SOAR_6.png
.. image:: images/example_Dor30_SOAR_7.png
.. image:: images/example_Dor30_SOAR_8.png
.. image:: images/example_Dor30_SOAR_9.png
.. image:: images/example_Dor30_SOAR_10.png
.. image:: images/example_Dor30_SOAR_11.png
.. image:: images/example_Dor30_SOAR_12.png
.. image:: images/example_Dor30_SOAR_13.png
.. image:: images/example_Dor30_SOAR_14.png
