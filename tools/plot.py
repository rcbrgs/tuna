"""
Plot the numpy array using matplotlib.
"""

import math
import matplotlib.pyplot as plt
import numpy

def log ( message ):
    debug = True
    if debug:
        print ( message )

def plot ( data, title = "" ):
    """
    Function that attempts to plot a numpy ndarray argument.
    Will plot a mosaic if data is 3D, a simple plot if 2D.
    """
    if len ( data.shape ) == 3:
        subplots = data.shape [ 0 ]
        log ( "subplots = {}".format ( subplots ) )

        dimensions = math.ceil ( math.sqrt ( subplots ) )
        log ( "should create mosaic of {} x {} slots.".format ( dimensions, dimensions ) )

        figure, axes = plt.subplots ( dimensions, dimensions, sharex='all', sharey='all' )

        figure.suptitle ( title )

        for plane in range ( data.shape [ 0 ] ):
            axes.flat [ plane ] .imshow ( data [ plane ] )

        return

    if len ( data.shape ) == 2:
        fig = plt.figure ( )
        plt.imshow ( data, cmap='spectral')
        plt.colorbar ( orientation="horizontal" )
        plt.title ( title )

def plot_high_res ( high_res ):
    """
    Expects a high_res object.
    Will plot each of the intermediary products.
    """
    plot ( high_res.continuum.array, title = "continuum" )
    plot ( high_res.discontinuum.array, title = "discontinuum" )
    plot ( high_res.wrapped_phase_map.array, title = "wrapped phase map" )
    plot ( high_res.noise.array, title = "noise" )
    plot ( high_res.borders_to_center_distances.array, title = "borders to center distances" )
    plot ( high_res.order_map.array, title = "order map" )
    plot ( high_res.unwrapped_phase_map.array, title = "unwrapped phase map" )
    if high_res.parabolic_fit:
        plot ( high_res.parabolic_fit.array, title = "parabolic fit" )
    if high_res.airy_fit:
        plot ( high_res.airy_fit.array, title = "airy fit" )
        plot ( high_res.airy_fit_residue.array, title = "airy fit residue" )
    plot ( high_res.substituted_channels.array, title = "substituted channels" )
    plot ( high_res.wavelength_calibrated.array, title = "wavelength calibrated" )
