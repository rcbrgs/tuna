# -*- coding: utf-8 -*-
"""
This module's scope is the reduction of data from a calibration lamp using SOAR's SAMI instrument.
"""

__version__ = "0.1.0"
__changelog__ = {
    "0.1.0" : { "Tuna" : "0.16.0", "Change" : "Initial commit." }
    }

import astropy.io.fits
import IPython
import logging
import math
import numpy
import random
import re
import threading
import time
import tuna

class reducer ( threading.Thread ):
    """
    Creates and stores an unwrapped phase map, taking as input a raw data cube.

    It inherits from the :ref:`threading_label`.Thread class, and it auto-starts its thread execution. Clients are expected to use its .join ( ) method before using its results.

    The overscan removal used here was written by Bruno Quint in 2015.

    Intermediary products are:

    - overscanned (the original data, after overscan removal)
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

    * file_names_per_channel : dict : { }
        This dictionary allows the user to specify the file name associated with each channel of the instrument. For example::
        
        >>> file_names_per_channel = { 0 : "/data/fp_data_01.fits", \
                                       1 : "/data/fp_data_02.fits", \
                                       2 : "/data/fp_data_03.fits", \
                                       3 : "/data/fp_data_04.fits" }

        Please notice that the indexes must begin in 0 and not "skip" any channel.

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
                   file_names_per_channel : dict = { },
                   finesse : float = 1,
                   free_spectral_range : float = 1,
                   interference_order : int = 1,
                   interference_reference_wavelength : float = 0,
                   min_rings = 1,
                   noise_mask_radius = 1,
                   noise_threshold = None,
                   parameter_file : str = "",
                   pixel_size : float = 1,
                   plot_log = False,
                   ring_minimal_percentile = None,
                   scanning_wavelength : float = 0,
                   unwrapped_only = False,
                   verify_center = None ):
        super ( self.__class__, self ).__init__ ( )
        self.log = logging.getLogger ( __name__ )
        
        self.log.info ( "Starting {} pipeline.".format ( self.__module__ ) )

        """inputs:"""
        self.calibration_wavelength = calibration_wavelength
        self.channel_subset = channel_subset
        self.continuum_to_FSR_ratio = continuum_to_FSR_ratio
        self.dont_fit = dont_fit
        self.file_names_per_channel = file_names_per_channel
        self.finesse = finesse
        self.free_spectral_range = free_spectral_range
        self.interference_order = interference_order
        self.interference_reference_wavelength = interference_reference_wavelength
        self.min_rings = min_rings
        self.noise_mask_radius = noise_mask_radius
        self.noise_threshold = noise_threshold
        self.pixel_size = pixel_size
        self.plot_log = plot_log
        self.ring_minimal_percentile = ring_minimal_percentile
        self.scanning_wavelength = scanning_wavelength
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

        first_channel_hdu = astropy.io.fits.open ( self.file_names_per_channel [ 0 ] )
        # Validation
        observatory = first_channel_hdu [ 0 ].header [ "OBSERVAT" ]
        telescope   = first_channel_hdu [ 0 ].header [ "TELESCOP" ]
        instrument  = first_channel_hdu [ 0 ].header [ "INSTRUME" ]
        self.log.info ( "Data from '{}' observatory, '{}' telescope, '{}' instrument.".format (
            observatory, telescope, instrument ) )
        if ( observatory, telescope, instrument ) != ( "SOAR", "SOAR telescope", "SAM" ):
            self.log.warning ( "Metadata not consistent with pipeline!" )

        # Obtain geometry
        number_of_channels = len ( list ( self.file_names_per_channel.keys ( ) ) )
        self.log.debug ( "Raw data has {} channels.".format ( number_of_channels ) )

        ccd_rows, ccd_cols = self.parse_header_ranges (
            header_ranges = first_channel_hdu [ 1 ].header [ "CCDSIZE" ] )
        ccd_size = ( ccd_cols [ 1 ], ccd_rows [ 1 ] )
        self.log.debug ( "CCD size = {}.".format ( ccd_size ) )

        number_of_extensions_per_channel = int ( first_channel_hdu [ 0 ].header [ "NEXTEND" ] )
        panel_axis = int ( math.sqrt ( number_of_extensions_per_channel ) )
        self.log.debug ( "Each channel file has {} FITS extensions.".format ( number_of_extensions_per_channel ) )

        #trimmed_size = ccd_size
        panel_geometry = { }
        current_panel = 1
        cols_per_binning = int ( int ( ccd_cols [ 1 ] ) / panel_axis )
        rows_per_binning = int ( int ( ccd_rows [ 1 ] ) / panel_axis )
        for panel_col in range ( panel_axis ):
            for panel_row in range ( panel_axis ):
                panel_geometry [ current_panel ] = (
                    ( cols_per_binning * panel_col,
                      cols_per_binning * ( panel_col + 1 ) - 1 ),
                    ( rows_per_binning * panel_row,
                      rows_per_binning * ( panel_row + 1 ) - 1 ) )
                current_panel += 1
        for panel in range ( 1, number_of_extensions_per_channel + 1 ):
            self.log.debug ( "Geometry for extension {}: {}.".format ( panel, panel_geometry [ panel ] ) )

        # Create empty array for cube
        cube = numpy.zeros ( shape = ( number_of_channels,
                                       ccd_size [ 0 ],
                                       ccd_size [ 1 ] ) )
        
        # For each channel file:
        for channel in self.file_names_per_channel.keys ( ):
            self.log.info ( "Processing channel {} from raw file {}.".format (
                channel, self.file_names_per_channel [ channel ] ) )
            channel_hdu = astropy.io.fits.open ( self.file_names_per_channel [ channel ] )

            # For each panel in the file:
            for panel in range ( 1, number_of_extensions_per_channel + 1 ):
                # Obtain the trimmed and overscan (bias) data
                self.log.debug ( "Processing panel {}.".format ( panel ) )
                self.log.debug ( "channel_hdu [ {} ].data.shape = {}.".format (
                    panel, channel_hdu [ panel ].data.shape ) )
                trimsec = channel_hdu [ panel ].header [ 'TRIMSEC' ]
                biassec = channel_hdu [ panel ].header [ 'BIASSEC' ]
                trim_rows, trim_cols = self.parse_header_ranges ( header_ranges = trimsec )
                bias_rows, bias_cols = self.parse_header_ranges ( header_ranges = biassec )
                self.log.debug ( "trim = ({}, {})".format ( trim_cols, trim_rows ) )
                self.log.debug ( "bias = ({}, {})".format ( bias_cols, bias_rows ) )
                trim_data = channel_hdu [ panel ].data [ trim_cols [ 0 ] - 1 : trim_cols [ 1 ] - 1,
                                                         trim_rows [ 0 ] - 1 : trim_rows [ 1 ] - 1 ]
                #self.log.debug ( "trim_data = {}.".format ( trim_data ) )
                # fit and remove overscan
                bias_data = channel_hdu [ panel ].data [ bias_cols [ 0 ] - 1 : bias_cols [ 1 ] - 1,
                                                         bias_rows [ 0 ] - 1 : bias_rows [ 1 ] - 1 ]
                #self.log.debug ( "bias_data = {}".format ( bias_data ) )
                bias_median = numpy.median ( bias_data, axis = 1 )
                #self.log.debug ( "bias_median = {}".format ( bias_median ) )
                col_indexes = numpy.arange ( bias_median.size ) + 1
                #self.log.debug ( "col_indexes = {}".format ( col_indexes ) )
                bias_fit_parameters = numpy.polyfit ( col_indexes, bias_median, 4 )
                bias_fit = numpy.polyval ( bias_fit_parameters, col_indexes )
                bias_fit = bias_fit.reshape ( ( bias_fit.size, 1 ) )
                bias_fit = numpy.repeat ( bias_fit, trim_data.shape [ 1 ], axis = 1 )
                debiased_data = trim_data - bias_fit
                #self.log.debug ( "debiased_data = {}.".format ( debiased_data ) )
                
                # Add trimmed data to cube
                cube [ channel,
                       panel_geometry [ panel ] [ 0 ] [ 0 ] : panel_geometry [ panel ] [ 0 ] [ 1 ],
                       panel_geometry [ panel ] [ 1 ] [ 0 ] : panel_geometry [ panel ] [ 1 ] [ 1 ] ] = trim_data

        # move bad lines and columns to the "border" of the cube
        bad_cols = cube [ :,
                          ccd_size [ 0 ] / 2 - 1 : ccd_size [ 0 ] / 2 + 1,
                          : ]
        cube [ :, ccd_size [ 0 ] / 2 - 1 : - 2, : ] = cube [ :, ccd_size [ 0 ] / 2 + 1 :, : ]
        cube [ :, - 2 :, : ] = bad_cols
        bad_lines = cube [ :,
                           :,
                          ccd_size [ 1 ] / 2 - 1 : ccd_size [ 1 ] / 2 + 1 ]
        cube [ :, :, ccd_size [ 1 ] / 2 - 1 : - 2 ] = cube [ :, :, ccd_size [ 1 ] / 2 + 1 : ]
        cube [ :, :, - 2 : ] = bad_lines                           
                
        self.overscanned = tuna.io.can ( array = cube )

        self.colapsed = tuna.io.can ( array = numpy.sum ( self.overscanned.array, 0 ) )
        
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

    def parse_header_ranges ( self,
                              header_ranges : str ) -> tuple:
        """
        This method's goal is to parse a range, given as a string with the format '[xxxxx:yyyyyy,wwwww:zzzzz]', where the number of digits is variable, into a tuple of integers corresponding to these values.
        """
        matcher = re.compile ( r"\[([\d]+):([\d]+),([\d]+):([\d]+)\]" )
        matches = matcher.search ( header_ranges ).groups ( )
        return ( ( int ( matches [ 0 ] ), int ( matches [ 1 ] ) ),
                 ( int ( matches [ 2 ] ), int ( matches [ 3 ] ) ) )
        
    def plot ( self ):
        """
        This method relies on matplotlib and ipython being available, and renders the intermediary products of this pipeline as plots.
        """
        tuna.tools.plot ( self.overscanned.array,
                          cmap = "spectral",
                          title = "Data with overscan removed",
                          ipython = self.ipython )
        tuna.tools.plot ( self.colapsed.array,
                          cmap = "spectral",
                          title = "Overscanned data colapsed on the spectral dimension",
                          ipython = self.ipython )
        tuna.tools.plot ( self.continuum.array,
                          cmap = "spectral",
                          title = "Continuum map",
                          ipython = self.ipython )
        tuna.tools.plot ( self.discontinuum.array,
                          cmap = "spectral",
                          title = "Discontinuum map (original data minus its continuum)",
                          ipython = self.ipython )
        tuna.tools.plot ( self.wrapped_phase_map.array,
                          cmap = "spectral",
                          title = "Wrapped phase map (barycenter map)",
                          ipython = self.ipython )
        tuna.tools.plot ( self.noise.array,
                          title = "Noise",
                          ipython = self.ipython )
        tuna.tools.plot ( self.borders_to_center_distances.array,
                          title = "Borders to center distances",
                          ipython = self.ipython )
        tuna.tools.plot ( self.order_map.array,
                          title = "Order map",
                          ipython = self.ipython )
        tuna.tools.plot ( self.unwrapped_phase_map.array,
                          cmap = "spectral",
                          title = "Unwrapped phase map",
                          ipython = self.ipython )
        if self.parabolic_fit is not None:
            tuna.tools.plot ( self.parabolic_fit.array,
                              cmap = "spectral",
                              title = "Parabolic fit",
                              ipython = self.ipython )
        if self.airy_fit is not None:
            tuna.tools.plot ( self.airy_fit.array,
                              cmap = "spectral",
                              title = "Airy fit",
                              ipython = self.ipython )
        if self.airy_fit_residue is not None:
            tuna.tools.plot ( self.airy_fit_residue.array,
                              cmap = "spectral",
                              title = "Airy fit residue",
                              ipython = self.ipython )
        tuna.tools.plot ( self.substituted_channels.array,
                          cmap = "spectral",
                          title = "Synthetic cube, with Airy fit substituted channels",
                          ipython = self.ipython )
        tuna.tools.plot ( self.wavelength_calibrated.array,
                          cmap = "spectral",
                          title = "Wavelength calibrated phase map",
                          ipython = self.ipython )
        
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
