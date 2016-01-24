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

The reduction was made using Tuna version 0.16.4. The code to reduce the image was::

  import numpy
  import time
  import tuna
  
  tuna.log.set_path ( "/home/nix/example_Dor30_SOAR.log" )
  tuna.log.verbose ( "file", "DEBUG" )
  tuna.log.verbose ( "console", "INFO" )
  
  # 1. Create a dictionary with the file names associated with each channel
  
  path = "/home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001"
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
  Handler <logging.FileHandler object at 0x7f21c24bc908> set to 10.
  Handler <logging.StreamHandler object at 0x7f21c0051e80> set to 20.
  Starting tuna.pipelines.soar_sami_calibration_lamp pipeline.
  Data from 'SOAR' observatory, 'SOAR telescope' telescope, 'SAM' instrument.
  Processing channel 0 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C001.278.fits.
  Processing channel 1 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C002.279.fits.
  Processing channel 2 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C003.280.fits.
  Processing channel 3 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C004.281.fits.
  Processing channel 4 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C005.282.fits.
  Processing channel 5 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C006.283.fits.
  Processing channel 6 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C007.284.fits.
  Processing channel 7 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C008.285.fits.
  Processing channel 8 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C009.286.fits.
  Processing channel 9 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C010.287.fits.
  Processing channel 10 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C011.288.fits.
  Processing channel 11 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C012.289.fits.
  Processing channel 12 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C013.290.fits.
  Processing channel 13 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C014.291.fits.
  Processing channel 14 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C015.292.fits.
  Processing channel 15 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C016.293.fits.
  Processing channel 16 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C017.294.fits.
  Processing channel 17 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C018.295.fits.
  Processing channel 18 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C019.296.fits.
  Processing channel 19 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C020.297.fits.
  Processing channel 20 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C021.298.fits.
  Processing channel 21 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C022.299.fits.
  Processing channel 22 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C023.300.fits.
  Processing channel 23 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C024.301.fits.
  Processing channel 24 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C025.302.fits.
  Processing channel 25 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C026.303.fits.
  Processing channel 26 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C027.304.fits.
  Processing channel 27 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C028.305.fits.
  Processing channel 28 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C029.306.fits.
  Processing channel 29 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C030.307.fits.
  Processing channel 30 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C031.308.fits.
  Processing channel 31 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C032.309.fits.
  Processing channel 32 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C033.310.fits.
  Processing channel 33 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C034.311.fits.
  Processing channel 34 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C035.312.fits.
  Processing channel 35 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C036.313.fits.
  Processing channel 36 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C037.314.fits.
  Processing channel 37 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C038.315.fits.
  Processing channel 38 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C039.316.fits.
  Processing channel 39 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C040.317.fits.
  Processing channel 40 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C041.318.fits.
  Processing channel 41 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C042.319.fits.
  Processing channel 42 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C043.320.fits.
  Processing channel 43 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C044.321.fits.
  Processing channel 44 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C045.322.fits.
  Processing channel 45 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C046.323.fits.
  Processing channel 46 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C047.324.fits.
  Processing channel 47 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C048.325.fits.
  Processing channel 48 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C049.326.fits.
  Processing channel 49 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C050.327.fits.
  Processing channel 50 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C051.328.fits.
  Processing channel 51 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C052.329.fits.
  Processing channel 52 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C053.330.fits.
  Processing channel 53 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C054.331.fits.
  Processing channel 54 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C055.332.fits.
  Processing channel 55 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C056.333.fits.
  Processing channel 56 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C057.334.fits.
  Processing channel 57 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C058.335.fits.
  Processing channel 58 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C059.336.fits.
  Processing channel 59 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C060.337.fits.
  Processing channel 60 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C061.338.fits.
  Processing channel 61 from raw file /home/nix/cold_store/fpdata_2015-09-11_Bruno_Quint_run_de_março/raw/001/fp_sami_C062.339.fits.
  Continuum array created.
  Barycenter done.
  Noise map created with lower_value = 128204.70999999999.
  Could not find rings in plane 19, searching the whole cube.
  Searching for concentric rings in plane 20.
  No concentric rings on plane 20.
  Searching for concentric rings in plane 21.
  No concentric rings on plane 21.
  Searching for concentric rings in plane 22.
  No concentric rings on plane 22.
  Searching for concentric rings in plane 23.
  No concentric rings on plane 23.
  Searching for concentric rings in plane 24.
  No concentric rings on plane 24.
  Searching for concentric rings in plane 25.
  No concentric rings on plane 25.
  Searching for concentric rings in plane 26.
  No concentric rings on plane 26.
  Searching for concentric rings in plane 27.
  No concentric rings on plane 27.
  Searching for concentric rings in plane 28.
  No concentric rings on plane 28.
  Searching for concentric rings in plane 29.
  No concentric rings on plane 29.
  Searching for concentric rings in plane 30.
  Concentric rings structure: ((-25216.500000101078, 244.00077160525024), [26244.624999803407], [0])
  Ring structure in plane 30 is the best so far (1 rings).
  Searching for concentric rings in plane 31.
  Concentric rings structure: ((580.52905368413599, 164.8188091217454), [795.82387348800614, 120.21435449951998], [0, 1])
  Ring structure obtained from plane where borders occupy 5% of the array.
  Ring structure in plane 31 is the best so far (2 rings).
  Searching for concentric rings in plane 32.
  Concentric rings structure: ((580.71855045678035, 168.02101237423338), [782.02727123372972], [0])
  Searching for concentric rings in plane 33.
  Concentric rings structure: ((581.0431355290749, 166.76036657069847), [770.63825798083906], [0])
  Searching for concentric rings in plane 34.
  Concentric rings structure: ((581.2195548207294, 162.99463877261024), [759.55623782110342], [0])
  Searching for concentric rings in plane 35.
  Concentric rings structure: ((580.32122163397241, 168.53903322283878), [741.28585819000762], [0])
  Searching for concentric rings in plane 36.
  Concentric rings structure: ((580.63686032053101, 166.60136245707417), [728.68464768089029], [0])
  Searching for concentric rings in plane 37.
  Concentric rings structure: ((580.40843796425997, 162.82081538530659), [717.90847175227157], [0])
  Searching for concentric rings in plane 38.
  Concentric rings structure: ((580.5224196371945, 164.66648211850108), [702.26633918874711], [0])
  Searching for concentric rings in plane 39.
  Concentric rings structure: ((579.99804362249915, 166.8892201171017), [685.4535159988792], [0])
  Searching for concentric rings in plane 40.
  Concentric rings structure: ((580.27045886906399, 163.92014069140527), [672.36400601164735], [0])
  Searching for concentric rings in plane 41.
  Concentric rings structure: ((579.8628651129967, 162.74035063438029), [658.06192809633183], [0])
  Searching for concentric rings in plane 42.
  Concentric rings structure: ((579.98565570923267, 161.25753954140126), [643.94503708087393], [0])
  Searching for concentric rings in plane 43.
  Concentric rings structure: ((579.78992936462964, 164.37164371403648), [625.54741687373451], [0])
  Searching for concentric rings in plane 44.
  Concentric rings structure: ((578.86319218241033, 166.12540716612435), [607.90746063640904], [0])
  Searching for concentric rings in plane 45.
  Concentric rings structure: ((579.34449168163121, 163.91306677947173), [591.73346054931574], [0])
  Searching for concentric rings in plane 46.
  Concentric rings structure: ((579.48965925202867, 163.03258204167292), [574.68318345339958], [0])
  Searching for concentric rings in plane 47.
  Concentric rings structure: ((579.45159108886878, 162.62584269774595), [557.33743195931311], [0])
  Searching for concentric rings in plane 48.
  Concentric rings structure: ((579.75157160238643, 164.01641683318471), [538.24084341945604], [0])
  Searching for concentric rings in plane 49.
  No concentric rings on plane 49.
  Searching for concentric rings in plane 50.
  No concentric rings on plane 50.
  Searching for concentric rings in plane 51.
  No concentric rings on plane 51.
  Searching for concentric rings in plane 52.
  No concentric rings on plane 52.
  Searching for concentric rings in plane 53.
  No concentric rings on plane 53.
  Searching for concentric rings in plane 54.
  No concentric rings on plane 54.
  Searching for concentric rings in plane 55.
  No concentric rings on plane 55.
  Searching for concentric rings in plane 56.
  No concentric rings on plane 56.
  Searching for concentric rings in plane 57.
  No concentric rings on plane 57.
  Searching for concentric rings in plane 58.
  No concentric rings on plane 58.
  Searching for concentric rings in plane 59.
  No concentric rings on plane 59.
  Searching for concentric rings in plane 60.
  Line to plot parallel (1025) to col axis.
  Concentric rings structure: ((-14025.625, 173.75), [15053.625002076187], [0])
  Searching for concentric rings in plane 61.
  Concentric rings structure: ((-26280.248494229771, 247.75150602486335), [27308.373873856934], [0])
  Searching for concentric rings in plane 0.
  Concentric rings structure: ((577.9250117243655, 165.60940932914605), [795.78839923110331, 126.57113826578056], [0, 1])
  Ring structure obtained from plane where borders occupy 7% of the array.
  Distance between first 2 centers: 221.33332831620228.
  Searching for concentric rings in plane 1.
  Concentric rings structure: ((581.03896920712225, 164.84708440104637), [790.96270665114855], [0])
  Searching for concentric rings in plane 2.
  Concentric rings structure: ((581.06204803566027, 164.24615485257681), [779.02603380133678], [0])
  Searching for concentric rings in plane 3.
  Concentric rings structure: ((580.87479601128928, 166.79512645009322), [762.98657032810297], [0])
  Searching for concentric rings in plane 4.
  Concentric rings structure: ((581.03967908208233, 166.00764289740476), [751.70850551797446], [0])
  Searching for concentric rings in plane 5.
  Concentric rings structure: ((580.81190521173301, 161.06230531385711), [741.42190099333448], [0])
  Searching for concentric rings in plane 6.
  Concentric rings structure: ((580.64833260571038, 162.51451627454247), [725.90155394322449], [0])
  Searching for concentric rings in plane 7.
  Concentric rings structure: ((580.4182756397737, 163.42690452684607), [710.4180459556062], [0])
  Searching for concentric rings in plane 8.
  Concentric rings structure: ((580.28969323865124, 165.43938148106045), [694.79065815030219], [0])
  Searching for concentric rings in plane 9.
  Concentric rings structure: ((580.00366673136261, 166.10954808958269), [679.58078304350988], [0])
  Searching for concentric rings in plane 10.
  Concentric rings structure: ((580.03196943466332, 167.13062765121538), [664.40697352404607], [0])
  Searching for concentric rings in plane 11.
  Concentric rings structure: ((579.91869846279644, 164.43628116135093), [650.04931135518348], [0])
  Searching for concentric rings in plane 12.
  Concentric rings structure: ((579.88581466790868, 165.26587152387705), [633.67044908579419], [0])
  Searching for concentric rings in plane 13.
  Searching for concentric rings in plane 14.
  Concentric rings structure: ((579.50502443371795, 162.46535225190416), [602.66920778502561], [0])
  Searching for concentric rings in plane 15.
  Concentric rings structure: ((579.54186795491137, 164.21152518978624), [583.46993310747109], [0])
  Searching for concentric rings in plane 16.
  Concentric rings structure: ((579.41580093670404, 163.4133550285452), [566.96565273248189], [0])
  Searching for concentric rings in plane 17.
  Concentric rings structure: ((579.61936361235814, 164.01274358784852), [548.31338218252301], [0])
  Searching for concentric rings in plane 18.
  Concentric rings structure: ((578.93049357126995, 163.38500358938293), [528.83460715742694], [0])
  Could not find a plane with two rings on the cube!
  Returning single ring result.
  sorted_radii = ['120.21', '795.82']
  inital_gap = 1.99e+06 microns
  channel_gap = -2.28992113592704 microns.
  Airy <|residue|> = 2301.0 photons / pixel
  sorted_distances == [120.21435449951998, 795.8238734880061]
  Phase map unwrapped.
  Wavelength calibration done.
  Parabolic model fitted.
  Tuna took 4932.2s to reduce.
  
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
