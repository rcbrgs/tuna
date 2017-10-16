"""
This module's scope is related to plotting data graphically.

Example::

    import tuna
    raw = tuna.io.read ( "tuna/test/unit/unit_io/adhoc.ad3" )
    tuna.tools.plot ( raw )
"""
__version__ = "0.1.1"
__changelog__ = {
    "0.1.1" : { "Tuna" : "0.16.0", "Change" : "Added parameter for colormap in plot." },
    "0.1.0" : { "Tuna" : "0.15.3", "Change" : "Added check for ipython reference after its creation and abort plot when reference is None." }
    }

import IPython
import math
import numpy
import warnings

try:
    with warnings.catch_warnings ( ):
        warnings.simplefilter ( "ignore" )
        import matplotlib.pyplot as plt
except ImportError:
    raise ImportError ( "Tuna requires matplotlib. Please install it." )

def log ( message ):
    """
    This function's goal is to output the input message if its debug value is True, otherwise it does nothing. It is a poor substitute for writing proper support to the logging module.

    Parameters:

    * message : string
    """
    debug = False
    if debug:
        print ( message )

#def plot ( data, cmap = "Greys", title = "", ipython = None ):
def plot ( data, cmap = "Reds", title = "", ipython = None ):
    """
    This function's goal is to plot a numpy ndarray argument.
    Will plot a mosaic if data is 3D, a simple plot if 2D.

    Parameters:

    * data : numpy.ndarray

    * cmap : str : "Reds"
        The colormap to be passed to matplotlib.

    * title : string

    * ipython : object
        A reference to the running ipython environment.
    """
    if not ipython:
        ipython = IPython.get_ipython()
        if ipython == None:
            log ( "Could not get ipython reference, aborting plot." )
        ipython.magic ( "matplotlib qt" )

    #if len ( data.shape ) == 3:
    if len ( self.get_array().shape ) == 3:
        #subplots = data.shape [ 0 ]
        subplots=self.get_array().shape[0]
        log ( "subplots = {}".format ( subplots ) )

        dimensions = math.ceil ( math.sqrt ( subplots ) )
        log ( "should create mosaic of {} x {} slots.".format ( dimensions, dimensions ) )

        figure, axes = plt.subplots ( dimensions, dimensions, sharex='col', sharey='row' )

        figure.suptitle ( title )

        for plane in range ( data.shape [ 0 ] ):
            #image = axes.flat [ plane ] .imshow ( data [ plane ], cmap = cmap )
            image = axes.flat [ plane ] .imshow ( self.get_array()[plane], cmap = cmap )
            axes.flat[plane].set_title("Channel {}".format(plane))

        figure.subplots_adjust( right = 0.8 )

        colorbar_axe = figure.add_axes ( [ 0.85, 0.15, 0.05, 0.7 ] )
        figure.colorbar ( image, cax=colorbar_axe )

        return

    #if len ( data.shape ) == 2:
    if len ( self.get_array().shape) == 2:    
        fig = plt.figure ( )
        #plt.imshow ( data, cmap = cmap )
        plt.imshow ( self.get_array(), cmap = cmap )
        plt.colorbar ( orientation = "horizontal" )
        plt.title ( title )

def plot_high_res ( high_res ):
    """
    This function's goal is to plot the intermediary products of a tuna.pipelines.calibration_lamp_high_resolution object.

    Parameters:

    * high_res : object
        A reference to a :ref:`tuna_pipelines_calibration_lamp_high_resolution_label` object.
    """

    ipython = IPython.get_ipython()
    ipython.magic("matplotlib qt")

    plot ( high_res.tuna_can.array, title = "Original data", ipython = ipython, cmap = "spectral" )
    plot ( high_res.continuum.array, title = "continuum", ipython = ipython, cmap = "spectral" )
    plot ( high_res.discontinuum.array, title = "discontinuum", ipython = ipython, cmap = "spectral" )
    plot ( high_res.wrapped_phase_map.array, title = "wrapped phase map", ipython = ipython, cmap = "spectral" )
    plot ( high_res.noise.array, title = "noise", ipython = ipython )
    ring_counter = 0
    for ring in high_res.find_rings [ 'ring_pixel_sets' ]:
        plot ( ring [ 0 ], title = "ring {}".format ( ring_counter ), ipython = ipython )
        ring_counter += 1
    plot ( high_res.borders_to_center_distances.array, title = "borders to center distances", ipython = ipython )
    plot ( high_res.order_map.array, title = "order map", ipython = ipython )
    plot ( high_res.unwrapped_phase_map.array, title = "unwrapped phase map", ipython = ipython, cmap = "spectral" )
    if high_res.parabolic_fit:
        plot ( high_res.parabolic_fit.array, title = "parabolic fit", ipython = ipython, cmap = "spectral" )
    if high_res.airy_fit:
        plot ( high_res.airy_fit.array, title = "airy fit", ipython = ipython, cmap = "spectral" )
        plot ( high_res.airy_fit_residue.array, title = "airy fit residue", ipython = ipython, cmap = "spectral" )
    if high_res.substituted_channels != None:
        plot ( high_res.substituted_channels.array, title = "substituted channels", ipython = ipython, cmap = "spectral" )
    plot ( high_res.wavelength_calibrated.array, title = "wavelength calibrated", ipython = ipython, cmap = "spectral" )

def plot_spectral_rings ( spectral_rings ):
    """
    This function will plot all arrays and print the data of all parameters specified in a tuna.tools.spectral_rings_fitter object.
    """
    ipython = IPython.get_ipython()
    ipython.magic("matplotlib qt")

    plot ( spectral_rings [ "ridge" ], title = "Ridge", ipython = ipython )
    for counter in range ( len ( spectral_rings [ "ring_pixel_sets" ] ) ):
        plot ( spectral_rings [ "ring_pixel_sets" ] [ counter ] [ 0 ], title = "Ring pixel set {}".format ( counter ), ipython = ipython )
    for counter in range ( len ( spectral_rings [ "gradients" ] ) ):
        plot ( spectral_rings [ "gradients" ] [ counter ], title = "Gradients", ipython = ipython )
    plot ( spectral_rings [ "upper_percentile_regions" ], title = "lower_percentile_regions", ipython = ipython )
    plot ( spectral_rings [ "lower_percentile_regions" ], title = "upper_percentile_regions", ipython = ipython )
    for counter in range ( len ( spectral_rings [ "construction" ] ) ):
        plot ( spectral_rings [ "construction" ] [ counter ], title = "Construction {}".format ( counter ), ipython = ipython )
    for counter in range ( len ( spectral_rings [ "ring_fit" ] ) ):
        plot ( spectral_rings [ "ring_fit" ] [ counter ], title = "Ring fit {}".format ( counter ), ipython = ipython )
        print ( "Ring {} parameters: {}".format ( counter, spectral_rings [ "ring_fit_parameters" ] ) )
    for counter in range ( len ( spectral_rings [ "rings" ] ) ):
        print ( "Ring {} = {}".format ( counter, spectral_rings [ "rings" ] [ counter ] ) )
    for counter in range ( len ( spectral_rings [ "concentric_rings" ] ) ):
        print ( "Concentric ring {} = {}".format ( counter, spectral_rings [ "concentric_rings" ] [ counter ] ) )
