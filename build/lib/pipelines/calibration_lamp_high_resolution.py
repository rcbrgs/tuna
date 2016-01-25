# -*- coding: utf-8 -*-
"""
This module's scope are the operations required to reduce data from a high resolution spectrograph.

Example::

    >>> import tuna
    >>> file_object = tuna.io.read ( "tuna/test/unit/unit_io/adhoc.ad3" )
    >>> reducer = tuna.pipelines.calibration_lamp_high_resolution.reducer ( \
            calibration_wavelength = 6598.953125, \
            finesse = 12, \
            free_spectral_range = 8.36522123894, \
            interference_order = 791, \
            interference_reference_wavelength = 6562.7797852, \
            pixel_size = 9, \
            scanning_wavelength = 6616.89, \
            tuna_can = file_object, \
            channel_subset = [ 0, 1, 2, 5 ], \
            continuum_to_FSR_ratio = 0.125, \
            min_rings = 2, \
            noise_mask_radius = 8, \
            dont_fit = False, \
            unwrapped_only = False, \
            verify_center = None ); reducer.join ( )
    >>> reducer.wavelength_calibrated.array [ 10 ] [ 10 ]
    103.18638370414156
"""

__version__ = "0.1.2"
__changelog__ = {
    "0.1.2" : { "Tuna" : "0.16.0", "Change" : "Added min_rings parameter for user to specify how many rings per plane are expected in the data cube. Defaults to 1. Refactored to only use keyworded parameters." },
    "0.1.1" : { "Tuna" : "0.15.3", "Change" : "Changed the name of the plots, to be more descriptive." },
    "0.1.0" : { "Tuna" : "0.15.0", "Change" : "Refactored to use detect_noise 'data' argument, to use 'overscan' plugin, 'Airy fit' plugin, 'FSR mapper' plugin." }
    }

import IPython
import logging
import math
import numpy
import random
import threading
import time
import tuna

class reducer ( threading.Thread ):
    """
    Creates and stores an unwrapped phase map, taking as input a raw data cube.

    It inherits from the :ref:`threading_label`.Thread class, and it auto-starts its thread execution. Clients are expected to use its .join ( ) method before using its results.

    Intermediary products are:

    - continuum
    - discontinuum
    - wrapped_phase_map
    - noise
    - borders_to_center_distances
    - order_map
    - unwrapped_phase_map
    - parabolic_fit
    - airy_fit
    - airy_fit_residue
    - substituted_channels
    - wavelength_calibrated

    Its constructor parameters are:

    * calibration_wavelength : float : 0
        Encodes the magnitude of the calibration wavelength, in Angstroms.

    * channel_subset : list of integers : [ ]
        A list of the channels to be substituted by their fitted model's data.

    * continuum_to_FSR_ratio : float : 0.5
        The ratio between the number of channels expected to have a continuum-dominated signal, and the channels expected to have a line-dominated signal. This is used to produce a continuum map; larger ratios means more data belongs to the continuum.

    * dont_fit : bool : False
        Specifies whether to fit models to the data.

    * finesse : float : 1
        Containing the value of the Finesse for this spectrographer.

    * free_spectral_range : float : 1
        Containing the value in Angstroms for the bandwidth that corresponds to one interference order.

    * interference_order : integer : 1
        The order of the interference pattern from the spectrograph for this wavelength, and étalon separation.
    
    * interference_reference_wavelength : float : 0
        The order of the interference pattern for the reference wavelength.

    * min_rings : integer : 1
        The number of rings present in the data cube.

    * noise_mask_radius : integer : 1
        The distance from a noise pixel that will be marked as noise also (size of a circle around each noise pixel);
    
    * noise_threshold : float : None
        The minimal value for a pixel content to be marked as signal, instead of noise. If None, this value will be automatically computed.

    * overscan_removal : dict : { }
        A dictionary of elements that must be removed from the datacube.

    * parameter_file : str : ""
        The path for a text file containing the values for the other parameters needed for this pipeline. The format must be:
        parameter = value

    * pixel_size : float : 1
        The size in micrometers of the separation between each pixel center in the CCD.

    * plot_log : boolean : False
        Specifies whether to matplotlib plot the partial results (which will be always available as ndarrays).

    * ring_minimal_percentile : integer : None
        The value for the minimal percentile that contains some data on the dataset. If None, will be determined automatically.

    * scanning_wavelength : float : 0
        The value in Angstroms for the wavelength used for scanning.

    * tuna_can : can : None
        The raw interferograph data. Must be a :ref:`tuna_io_can_label` object.

    * unwrapped_only : boolean : False
        If True, will avoid computing the model fits and the wavelength calibration.

    * verify_center : tuple of 2 integers : None
        If not None, the center calculated by the pipeline will be validated against the input value.
    """
    def __init__ ( self,
                   calibration_wavelength : float = 0,
                   channel_subset = [ ],
                   continuum_to_FSR_ratio = 0.125,
                   dont_fit = False,
                   finesse : float = 1,
                   free_spectral_range : float = 1,
                   interference_order : int = 1,
                   interference_reference_wavelength : float = 0,
                   min_rings = 1,
                   noise_mask_radius = 1,
                   noise_threshold = None,
                   overscan_removal = { },
                   parameter_file : str = "",
                   pixel_size : float = 1,
                   plot_log = False,
                   ring_minimal_percentile = None,
                   scanning_wavelength : float = 0,
                   tuna_can : tuna.io.can = None,
                   unwrapped_only = False,
                   verify_center = None ):
        super ( self.__class__, self ).__init__ ( )
        self.__version__ = "0.1.19"
        self.changelog = {
            "0.1.19" : "Tuna 0.15.0 : Moved to tuna.pipelines. Refactored to use plugins for noise, continuum, barycenter, ring center finder.",
            "0.1.18" : "Tuna 0.14.0 : updated documentation.",
            '0.1.17' : "Improved docstring for class.",
            '0.1.16' : "Adapted to use refined version of ring finder.",
            '0.1.15' : "Fixed gap 'pulsating' by making gap change monotonic, and using 1st gap fit as seed for plane reconstruction.",
            '0.1.14' : "Fixed gap limits logic for negative channel gap",
            '0.1.13' : "Since the plane gap is calculated, use it to get limits for per-plane airy fit.",
            '0.1.12' : "Adapting pipeline to new ring_find.",
            '0.1.11' : "Adapted sorted_rings to use new ring_find result.",
            '0.1.10' : "Added a plot() function as convenience to plot all subresults.",
            '0.1.9' : "Improved auto Airy by letting intensity and continuum be free.",
            '0.1.8' : "Improved auto Airy fit by priming fitter with channel gap values.",
            '0.1.7' : "Changed method for airy fit to fit separately each plane.",
            '0.1.6' : "Added support for ring_minimal_percentile.",
            '0.1.5' : "Added support for noise threshold parameter.",
            '0.1.4' : "Reverted to simpler method of fitting first 2 planes; works beautifully.",
            '0.1.3' : "Made default less verbose.",
            '0.1.2' : "Refactored to use new ring center finder.",
            '0.1.1' : "Using variables instead of harcoded values for inital b and gap values.",
            '0.1.0' : "Initial changelog."
            }
        self.log = logging.getLogger ( __name__ )
        self.log.setLevel ( logging.INFO )

        if not isinstance ( tuna_can, tuna.io.can ):
            self.log.info ( "array must be a numpy.ndarray or derivative object." )
            return
        try:
            if tuna_can.ndim != 3:
                self.log.warning ( "Image does not have 3 dimensions, aborting." )
                return
        except AttributeError as e:
            self.log.warning ( "%s, aborting." % str ( e ) )
            return
        
        self.log.info ( "Starting {} pipeline.".format ( self.__module__ ) )

        """inputs:"""
        self.calibration_wavelength = calibration_wavelength
        self.channel_subset = channel_subset
        self.continuum_to_FSR_ratio = continuum_to_FSR_ratio
        self.dont_fit = dont_fit
        self.finesse = finesse
        self.free_spectral_range = free_spectral_range
        self.interference_order = interference_order
        self.interference_reference_wavelength = interference_reference_wavelength
        self.min_rings = min_rings
        self.noise_mask_radius = noise_mask_radius
        self.noise_threshold = noise_threshold
        self.overscan_removal = overscan_removal
        self.pixel_size = pixel_size
        self.plot_log = plot_log
        self.ring_minimal_percentile = ring_minimal_percentile
        self.scanning_wavelength = scanning_wavelength
        self.tuna_can = tuna_can
        self.unwrapped_only = unwrapped_only
        self.verify_center = verify_center

        if parameter_file != "":
            self.log.debug ( "Parameter file specified: {}".format ( parameter_file ) )

        """outputs:"""
        self.airy_fit = None
        self.airy_fit_residue = None
        self.borders_to_center_distances = None
        self.continuum = None
        self.discontinuum = None
        self.noise = None
        self.order_map = None
        self.parabolic_fit = None
        self.parabolic_model = None
        self.rings_center = None
        self.substituted_channels = None
        self.unwrapped_phase_map = None
        self.wavelength_calibrated = None
        self.wrapped_phase_map = None

        self.ipython = IPython.get_ipython ( )
        if self.ipython != None:
            self.ipython.magic ( "matplotlib qt" )
        self.start ( )
        
    def run ( self ):
        """
        :ref:`threading_label` method for starting execution.
        """

        self.overscanned = tuna.plugins.run ( "Overscan" ) ( data = self.tuna_can,
                                                             elements_to_remove = self.overscan_removal )
        
        self.continuum = tuna.plugins.run ( "Continuum detector" ) ( self.overscanned,
                                                                     self.continuum_to_FSR_ratio )

        # Discontinuum calculation
        self.discontinuum = tuna.io.can ( array = numpy.ndarray ( shape = self.overscanned.shape ) )
        for plane in range ( self.overscanned.planes ):
            self.discontinuum.array [ plane, : , : ] = numpy.abs ( self.overscanned.array [ plane, : , : ] - self.continuum.array )
        #

        self.wrapped_phase_map = tuna.plugins.run ( "Barycenter algorithm" ) ( data_can = self.discontinuum )
        
        self.noise = tuna.plugins.run ( "Noise detector" ) ( data = self.overscanned,
                                                             wrapped = self.wrapped_phase_map, 
                                                             noise_mask_radius = self.noise_mask_radius,
                                                             noise_threshold = self.noise_threshold )

        self.find_rings = tuna.plugins.run ( "Ring center finder" ) ( data = self.overscanned.array,
                                                                      min_rings = self.min_rings,
                                                                      ipython = self.ipython,
                                                                      plot_log = self.plot_log )
        center = self.find_rings [ 'concentric_rings' ] [ 0 ]
        self.rings_center = center
        
        if self.verify_center != None:
            true_center = self.verify_center [ 0 ]
            threshold = self.verify_center [ 1 ]
            difference = math.sqrt ( ( center [ 0 ] - true_center [ 0 ] ) ** 2 + \
                                     ( center [ 1 ] - true_center [ 1 ] ) ** 2 )
            if difference >= threshold:
                return

        if len ( self.find_rings [ 'concentric_rings' ] [ 1 ] ) < 2 and self.dont_fit == False:
            self.log.error ( "Airy fitting requires at least 2 concentric rings. Blocking request to fit data." )
            self.dont_fit = True
            
        if self.dont_fit == False:
            sorted_radii = sorted ( self.find_rings [ 'concentric_rings' ] [ 1 ] )
            self.log.info ( "sorted_radii = {}".format (
                [ "{:.2f}".format ( radius ) for radius in sorted_radii ] ) )
            
            initial_b_ratio = tuna.tools.estimate_b_ratio ( sorted_radii [ : 2 ],
                                                            [ self.interference_order,
                                                              self.interference_order - 1 ] )
            self.log.debug ( "initial_b_ratio = {}".format ( initial_b_ratio ) )
            initial_gap = self.calibration_wavelength * self.interference_order * \
                          math.sqrt ( 1 + initial_b_ratio**2 * sorted_radii [ 0 ] ** 2 ) / 2
            self.log.info ( "inital_gap = {:.2e} microns".format ( initial_gap ) )
            
            parinfo_initial = [ ]
            parbase = { 'fixed' : False, 'limits' : ( initial_b_ratio * 0.9, initial_b_ratio * 1.1 ) }
            parinfo_initial.append ( parbase )
            parbase = { 'fixed' : False, 'limits' : ( center [ 0 ] - 50,
                                                      center [ 0 ] + 50 ) }
            parinfo_initial.append ( parbase )
            parbase = { 'fixed' : False, 'limits' : ( center [ 1 ] - 50,
                                                      center [ 1 ] + 50 ) }
            parinfo_initial.append ( parbase )
            parbase = { 'fixed' : False }
            parinfo_initial.append ( parbase )
            parbase = { 'fixed' : False, 'limits' : ( self.finesse * 0.9, self.finesse * 1.1 ) }
            parinfo_initial.append ( parbase )
            parbase = { 'fixed' : False, 'limits' : ( initial_gap - self.calibration_wavelength / 4,
                                                      initial_gap + self.calibration_wavelength / 4 ) }
            parinfo_initial.append ( parbase )
            parbase = { 'fixed' : False }
            parinfo_initial.append ( parbase )

            airy_fitter_0 = tuna.plugins.run ( "Airy fit" ) ( b_ratio = initial_b_ratio,
                                                              center_col = center [ 0 ],
                                                              center_row = center [ 1 ],
                                                              data = self.overscanned.array [ 0 ],
                                                              finesse = self.finesse,
                                                              gap = initial_gap,
                                                              wavelength = self.calibration_wavelength,
                                                              mpyfit_parinfo = parinfo_initial )

            airy_fit = numpy.ndarray ( shape = self.overscanned.shape )
            airy_fit [ 0 ] = airy_fitter_0 [ 1 ].array

            b_ratio     = airy_fitter_0 [ 0 ] [ 0 ]
            center_col  = airy_fitter_0 [ 0 ] [ 1 ]
            center_row  = airy_fitter_0 [ 0 ] [ 2 ]
            finesse     = airy_fitter_0 [ 0 ] [ 4 ]
            initial_gap = airy_fitter_0 [ 0 ] [ 5 ]
            
            parinfo = [ ]
            parbase = { 'fixed' : True }
            parinfo.append ( parbase )
            parbase = { 'fixed' : True }
            parinfo.append ( parbase )
            parbase = { 'fixed' : True }
            parinfo.append ( parbase )
            parbase = { 'fixed' : False }
            parinfo.append ( parbase )
            parbase = { 'fixed' : True }
            parinfo.append ( parbase )
            parbase = { 'fixed' : False, 'limits' : ( initial_gap - self.calibration_wavelength / 4,
                                                      initial_gap + self.calibration_wavelength / 4 ) }
            parinfo.append ( parbase )
            parbase = { 'fixed' : False }
            parinfo.append ( parbase )

            mid_plane = round ( self.overscanned.shape [ 0 ] / 2 )

            airy_fitter_1 = tuna.plugins.run ( "Airy fit" )  ( b_ratio = b_ratio,
                                                               center_col = center_col,
                                                               center_row = center_row,
                                                               data = self.overscanned.array [ mid_plane ],
                                                               finesse = finesse,
                                                               gap = initial_gap,
                                                               wavelength = self.calibration_wavelength,
                                                               mpyfit_parinfo = parinfo )
            
            airy_fit [ 1 ] = airy_fitter_1 [ 1 ].array
            
            channel_gap = ( airy_fitter_1 [ 0 ] [ 5 ] - airy_fitter_0 [ 0 ] [ 5 ] ) / mid_plane
            self.log.info ( "channel_gap = {} microns.".format ( channel_gap ) )

            latest_gap = airy_fitter_0 [ 0 ] [ 5 ] + channel_gap
            for plane in range ( 1, self.overscanned.planes ):
                parinfo = [ ]
                parbase = { 'fixed' : True }
                parinfo.append ( parbase )
                parbase = { 'fixed' : True }
                parinfo.append ( parbase )
                parbase = { 'fixed' : True }
                parinfo.append ( parbase )
                parbase = { 'fixed' : False }
                parinfo.append ( parbase )
                parbase = { 'fixed' : True }
                parinfo.append ( parbase )
                if channel_gap >= 0:
                    parbase = { 'fixed'  : False,
                                'limits' : ( latest_gap,
                                             latest_gap + 10 * abs ( channel_gap ) ) }
                else:
                    parbase = { 'fixed'  : False,
                                'limits' : ( latest_gap - 10 * abs ( channel_gap ),
                                             latest_gap ) }
                parinfo.append ( parbase )
                parbase = { 'fixed' : False }
                parinfo.append ( parbase )

                self.log.debug ( "Fitting Airy plane {}: gap at {:.5f}.".format (
                    plane, latest_gap ) )
                
                airy_fitter = tuna.plugins.run ( "Airy fit" ) ( b_ratio = b_ratio,
                                                                center_col = center_col,
                                                                center_row = center_row,
                                                                data = self.overscanned.array [ plane ],
                                                                finesse = finesse,
                                                                gap = latest_gap + channel_gap,
                                                                wavelength = self.calibration_wavelength,
                                                                mpyfit_parinfo = parinfo )
                latest_gap = airy_fitter [ 0 ] [ 5 ]
                airy_fit [ plane ] = airy_fitter [ 1 ].array
                self.log.debug ( "Plane {} fitted.".format ( plane ) ) 

            self.airy_fit = tuna.io.can ( airy_fit )
            
            airy_fit_residue = self.overscanned.array - self.airy_fit.array
            self.airy_fit_residue = tuna.io.can ( array = airy_fit_residue )
            airy_pixels = airy_fit_residue.shape [ 0 ] * airy_fit_residue.shape [ 1 ] * airy_fit_residue.shape [ 2 ] 
            self.log.info ( "Airy <|residue|> = {:.1f} photons / pixel".format (
                numpy.sum ( numpy.abs ( airy_fit_residue ) ) / airy_pixels ) )


        ring_border_detector = tuna.tools.phase_map.ring_border_detector (
            self.wrapped_phase_map,
            center,
            self.noise,
            self.find_rings )
        ring_border_detector.join ( )
        self.borders_to_center_distances = ring_border_detector.distances

        self.order_map = tuna.plugins.run ( "FSR mapper" ) ( distances = self.borders_to_center_distances,
                                                             wrapped = self.wrapped_phase_map,
                                                             center = center,
                                                             concentric_rings = self.find_rings [ 'concentric_rings' ] )

        self.create_unwrapped_phase_map ( )
        if self.unwrapped_only == True:
            return

        if self.dont_fit == False:
            # It seems Astropy's fitters ain't thread safe, so the airy fit must be already joined.
            parabolic_fitter = tuna.models.parabolic_fitter ( self.noise,
                                                              self.unwrapped_phase_map,
                                                              center )

        wavelength_calibrator = tuna.tools.wavelength.wavelength_calibrator ( self.unwrapped_phase_map,
                                                                              self.calibration_wavelength,
                                                                              self.free_spectral_range,
                                                                              self.interference_order,
                                                                              self.interference_reference_wavelength,
                                                                              self.overscanned.shape [ 0 ],
                                                                              center,
                                                                              self.scanning_wavelength )


        if self.dont_fit == False:
            substituted_channels = numpy.copy ( self.overscanned.array )
            for channel in range ( self.overscanned.planes ):
                if channel in self.channel_subset:
                    substituted_channels [ channel ] = numpy.copy ( self.airy_fit.array [ channel ] )
            self.substituted_channels = tuna.io.can ( array = substituted_channels )

            parabolic_fitter.join ( )
            self.parabolic_model = parabolic_fitter.coefficients
            self.parabolic_fit   = parabolic_fitter.fit
            self.verify_parabolic_model ( )

        wavelength_calibrator.join ( )
        self.wavelength_calibrated = wavelength_calibrator.calibrated

        self.log.debug ( "wavelength_calibrated.array [ 0 ] [ 0 ] == {}".format (
            self.wavelength_calibrated.array [ 0 ] [ 0 ] ) )

    def create_unwrapped_phase_map ( self ):
        """
        Unwraps the phase map according using the order array constructed.
        """
        start = time.time ( )

        max_x = self.wrapped_phase_map.array.shape[0]
        max_y = self.wrapped_phase_map.array.shape[1]
        max_channel = numpy.amax ( self.wrapped_phase_map.array )
        min_channel = numpy.amin ( self.wrapped_phase_map.array )

        unwrapped_phase_map = numpy.zeros ( shape = self.wrapped_phase_map.shape )
        self.log.debug ( "unwrapped_phase_map.ndim == %d" % unwrapped_phase_map.ndim )

        self.log.debug ( "Phase map 0% unwrapped." )
        last_percentage_logged = 0
        for x in range ( max_x ):
            percentage = 10 * int ( x / max_x * 10 )
            if percentage > last_percentage_logged:
                last_percentage_logged = percentage
                self.log.debug ( "Phase map %d%% unwrapped." % percentage )
            for y in range ( max_y ):
                unwrapped_phase_map [ x ] [ y ] = self.wrapped_phase_map.array [ x ] [ y ] + \
                                                  max_channel * float ( self.order_map.array [ x ] [ y ] )
        self.log.info ( "Phase map unwrapped." )

        self.unwrapped_phase_map = tuna.io.can ( array = unwrapped_phase_map )

        self.log.debug ( "create_unwrapped_phase_map() took %ds." % ( time.time ( ) - start ) )

    def verify_parabolic_model ( self ):
        """
        Since the parabolic model fits a second-degree equation in two variables to the data, which we expect to have a circular symmetry, the coefficients for each second-degree element in the fitted equation should be "close". This can be quantified as the ratio between these coefficients, which this method prints on the log.
        """
        self.log.debug ( "Ratio between 2nd degree coefficients is: %f" % ( self.parabolic_model [ 'x2y0' ] / 
                                                                            self.parabolic_model [ 'x0y2' ] ) )
                
def pixel_profiler ( reducer, pixel ):
    """
    This function's goal is to conveniently return a structure containing the data for a given "position" throughout the pipeline. Since objects can have 2 or 3 dimensions, the data structure returns either a value or a 1 dimensional array for each product.

    Parameters:

    * reducer : reference to a calibration_lamp_high_resolution object
        Should be set to the (already run) pipeline.

    * pixel : tuple of 2 integers
        Containing the values for column and row of the point to be investigated.

    Returns a dictionary with 8 fields (each field corresponds to the result of a method of the calibration_lamp_high_resolution class):

    * 'Original data' : numpy.ndarray
        Contains the spectrum for the input pixel.

    * 'Discontinuum' : numpy.ndarray
        The value of the continuum for the input pixel.

    * 'wrapped phase map' : float
        The value of the wrapped phase map at the input pixel.

    * 'Order map' : float
        The order to which the pixel belongs to (relative to the order at the center of the ring structure).

    * 'Unwrapped phase map' : float
        The value of the unwrapped phase map at the input pixel.

    * 'Parabolic fit' : float
        The value of the fitted parabolic model at the input pixel.

    * 'Airy fit' : numpy.ndarray
        The value of the fitted Airy model at the input pixel.

    * 'Wavelength' : float
        The value of the wavelength-calibrated map at the input pixel.
    """
    
    profile = { }

    profile [ 0 ] = ( 'Original data',       reducer.tuna_can.array              [ :, pixel [ 0 ], pixel [ 1 ] ] )
    profile [ 1 ] = ( 'Discontinuum',        reducer.discontinuum.array          [ :, pixel [ 0 ], pixel [ 1 ] ] )
    profile [ 2 ] = ( 'Wrapped phase map',   reducer.wrapped_phase_map.array     [ pixel [ 0 ] ] [ pixel [ 1 ] ] )
    profile [ 3 ] = ( 'Order map',           reducer.order_map.array             [ pixel [ 0 ] ] [ pixel [ 1 ] ] )
    profile [ 4 ] = ( 'Unwrapped phase map', reducer.unwrapped_phase_map.array   [ pixel [ 0 ] ] [ pixel [ 1 ] ] )
    profile [ 5 ] = ( 'Parabolic fit',       reducer.parabolic_fit.array         [ pixel [ 0 ] ] [ pixel [ 1 ] ] )
    profile [ 6 ] = ( 'Airy fit',            reducer.airy_fit.array              [ :, pixel [ 0 ], pixel [ 1 ] ] )
    profile [ 7 ] = ( 'Wavelength',          reducer.wavelength_calibrated.array [ pixel [ 0 ] ] [ pixel [ 1 ] ] )

    return profile
