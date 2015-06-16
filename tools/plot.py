"""
Plot the numpy array using matplotlib.
"""

import matplotlib.pyplot as plt
import numpy

def plot ( data ):
    #fig, axes = matplotlib.pyplot.subplots ( nrows = 1, ncols = 1 )
    #fig.set_figwidth ( 20 )
    #fig.set_figheight ( 4 )
    #imleft   = axes.imshow( array )
    #imcenter = axes.flat [ 1 ].imshow( center )
    #imright  = axes.flat [ 2 ].imshow( right )
    
    #fig.colorbar ( imleft, ax = axes )
    #fig.colorbar ( imcenter, ax = axes [ 1 ] )
    #fig.colorbar ( imright, ax = axes [ 2 ] )
    
    #matplotlib.pyplot.show()
    
    #pixels = left.shape [ 0 ] * left.shape [ 1 ]
    #print ( "max       = %d\t\t\t %d\t\t\t %d" % ( numpy.amax ( left ),
    fig = plt.figure ( )
    ax1 = plt.subplot ( 131 )
    plt.imshow ( data, cmap='spectral')
    plt.colorbar ( orientation="horizontal" )
                    
