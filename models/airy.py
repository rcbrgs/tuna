# coding: latin-1
"""
Airy function and fit.

The Airy function (or as Wikipedia calls it, the transmittance function of a Fabry-Pérot interferometer) modeled here is:

T = 1 / ( 1 + F sin^2 ( delta / 2 ) )

The airy_function will return a dataset containing the values for an Airy function with the given parameters.

The airy_fitter will spawn a thread that will fit the Airy function to the given data, using the given parameters as initial guesses.

"""

import copy
import logging
import math
import mpyfit
import numpy
import threading
import time
import tuna

def airy_plane ( b_ratio = 9.e-6,
                 center_col = 256,
                 center_row = 256,
                 continuum = 1,
                 finesse = 15,
                 gap = 250,
                 intensity = 100,
                 shape_cols = 512,
                 shape_rows = 512,
                 wavelength = 0.6563 ):
    """
    The Airy function being modeled is:

    I = C + I_0 / ( 1 + ( 4F^2 / pi^2 ) * sin^2 ( phi / 2 )

    From the input parameters, this function will return a dataset with the value for I calculated on each point. The intention is to produce a tridimensional array where each plane is an image with rings equivalent to the ones in Fabry-Pérot interferograms.

    To calculate phi:

    phi = 2 pi * ( 2 n e_i cos ( theta ) ) / lambda_c

    Where:

    n e_i = n ( e + i delta_e )

    theta = tan^-1 ( b r ), b = s / f


    Parameters: (In parentheses, the equation variable the paremeter corresponds to)
    -----------
    b_ratio:      the ratio between the pixel size and the camera focal length (b).
    center_col:   the column for the center of the rings, in pixels.
    center_row:   the row for the center of the rings, in pixels.
    continuum:    the value of the background intensity.
    finesse:      (F).
    gap:          the distance between the étalons, in microns (n e_i).
    intensity:    the beam maximum intensity (I_0).
    shape_cols:   the number of columns for the 2D shape (columns, rows) to be generated. 
    shape_rows:   the number of rows for the 2D shape (columns, rows) to be generated. 
    wavelength:   in microns ( lambda_c ).
    """

    log = logging.getLogger ( __name__ )
    log.debug ( "airy_plane" )
    
    log.debug ( "b_ratio = %f,"
                " center = (%d, %d),"
                " continuum = %f,"
                " finesse = %f,"
                " gap = %f,"
                " intensity = %f,"
                " shape = (%d, %d)"
                " wavelength = %f."
                % ( b_ratio, center_col, center_row, continuum, finesse, gap,
                    intensity, shape_cols, shape_rows, wavelength ) )

    indices_rows, indices_cols = numpy.indices ( ( shape_rows, shape_cols ) )
    distances = numpy.sqrt ( ( indices_rows - center_row ) ** 2 +
                             ( indices_cols - center_col ) ** 2 )
    log.debug ( "distances [ 0 ] [ 0 ] = %s" % str ( distances [ 0 ] [ 0 ] ) )
    
    log.debug ( "Calculating airy_function_I" )
    airy_function_I = 4.0 * finesse ** 2 / numpy.pi ** 2
    phase = 2.0 * numpy.pi * gap / ( wavelength * numpy.sqrt ( 1 + b_ratio ** 2 * distances ** 2 ) )
    log.debug ( "phase     [ 0 ] [ 0 ] = %s" % str ( phase [ 0 ] [ 0 ] ) )
    result = continuum + intensity / ( 1. + airy_function_I * numpy.sin ( phase ) ** 2 )
    log.debug ( "result    [ 0 ] [ 0 ] = %s" % str ( result [ 0] [ 0 ] ) )

    log.debug ( "/airy_plane" )
    return result

def least_mpyfit ( p, args ):
    log = logging.getLogger ( __name__ )
    log.debug ( "least_mpyfit" )
    
    b_ratio, center_col, center_row, continuum, finesse, gap, intensity = p
    shape_cols, shape_rows, wavelength, data, flat  = args

    try:
        plane = airy_plane ( b_ratio,
                             center_col,
                             center_row,
                             continuum,
                             finesse,
                             gap,
                             intensity,
                             shape_cols,
                             shape_rows,
                             wavelength )
        log.debug ( "plane = %s" % str ( plane ) )
    except Exception as e:
        print ( "Exception: %s" % str ( e ) )

    try:
        residue = ( plane - data ) * flat
    except Exception as e:
        print ( "Exception: %s" % str ( e ) )

    log.debug ( "residue = %s" % str ( residue ) )
    log.debug ( "numpy.sum ( residue ) = %f" % numpy.sum ( residue ) )
    log.debug ( "/least_mpyfit" )
    return ( residue.flatten ( ) )

class airy_fitter ( threading.Thread ):
    def __init__ ( self,
                   b_ratio,
                   center_col,
                   center_row,
                   data,
                   finesse,
                   gap,
                   wavelength,
                   mpyfit_parinfo = [ ] ):
                   
        self.log = logging.getLogger ( __name__ )
        super ( self.__class__, self ).__init__ ( )
        self.__version__ = '0.1.1'
        self.changelog = {
            '0.1.1' : "Refactored algorithm for getting lowest percentile into another module.",
            '0.1.0' : "Initial changelog."
            }

        self.b_ratio = b_ratio
        self.center_col = center_col
        self.center_row = center_row
        self.data = data
        self.finesse = finesse
        self.gap = gap
        self.mpyfit_parinfo = mpyfit_parinfo
        self.shape_cols = self.data.shape [ 0 ]
        self.shape_rows = self.data.shape [ 1 ]
        self.wavelength = wavelength
        
        self.fit = None
        self.parameters = None

        self.start ( )

    def run ( self ):
        """
        Interface function to fit an Airy model to a given input.
        """
        start = time.time ( )

        lower_percentile = tuna.tools.find_lowest_nonnull_percentile ( self.data )
        upper_percentile = 99          
        self.log.debug ( "%d-percentile = %f, %d-percentile = %f." % ( lower_percentile,
                                                                       numpy.percentile ( self.data,
                                                                                          lower_percentile ),
                                                                       upper_percentile,
                                                                       numpy.percentile ( self.data,
                                                                                          upper_percentile ) ) )
        
        intensity = numpy.percentile ( self.data, upper_percentile ) - numpy.percentile ( self.data, lower_percentile )
        self.log.debug ( "percentile difference = %f" % intensity )
        finesse_factor = 4.0 * self.finesse ** 2 / numpy.pi ** 2
        finesse_intensity_factor = ( 1 + finesse_factor ) / finesse_factor
        self.log.debug ( "finesse_intensity_factor = ( 1 + F ) / F = %f" % finesse_intensity_factor )
        intensity *= finesse_intensity_factor
        self.log.debug ( "intensity = %f" % intensity )

        continuum = abs ( numpy.percentile ( self.data, upper_percentile ) - intensity )

        self.log.debug ( "guesses:\n"
                         "\tb_ratio     = {:e},\n"
                         "\tcenter      = ( {}, {} )\n"
                         "\tcontinuum   = {:e}\n"
                         "\tfinesse     = {:e}\n"
                         "\tinitial gap = {:e}\n"
                         "\tintensity   = {:e}".format ( self.b_ratio, self.center_col,
                                                         self.center_row, continuum, self.finesse,
                                                         self.gap, intensity ) )
              
        parameters = ( self.b_ratio,
                       self.center_col,
                       self.center_row,
                       continuum,
                       self.finesse,
                       self.gap,
                       intensity )
        
        # Constraints on parameters
        if self.mpyfit_parinfo == [ ]:
            parinfo = [ ]
            parbase = { 'fixed' : False, 'limits' : ( self.b_ratio * 0.9, self.b_ratio * 1.1 ) }
            parinfo.append ( parbase )
            parbase = { 'fixed' : False, 'limits' : ( self.center_col - 5, self.center_col + 5 ) }
            parinfo.append ( parbase )
            parbase = { 'fixed' : False, 'limits' : ( self.center_row - 5, self.center_row + 5 ) }
            parinfo.append ( parbase )
            parbase = { 'fixed' : False, 'limits' : ( continuum * 0.9, continuum * 1.1 ) }
            parinfo.append ( parbase )
            parbase = { 'fixed' : False, 'limits' : ( self.finesse * 0.95, self.finesse * 1.05 ) }
            parinfo.append ( parbase )
            parbase = { 'fixed' : False, 'limits' : ( self.gap - self.wavelength / 4., self.gap + self.wavelength / 4. ) }
            parinfo.append ( parbase )
            parbase = { 'fixed' : False, 'limits' : ( intensity * 0.9, intensity * 1.1 ) }
            parinfo.append ( parbase )
        else:
            parinfo = [ ]
            parbase = self.mpyfit_parinfo [ 0 ]
            parinfo.append ( parbase )
            parbase = self.mpyfit_parinfo [ 1 ]
            parinfo.append ( parbase )
            parbase = self.mpyfit_parinfo [ 2 ]
            parinfo.append ( parbase )
            parbase = { 'fixed'  : self.mpyfit_parinfo [ 3 ] [ 'fixed' ],
                        'limits' : ( continuum * 0.9, continuum * 1.1 ) }
            parinfo.append ( parbase )
            parbase = self.mpyfit_parinfo [ 4 ]
            parinfo.append ( parbase )
            parbase = self.mpyfit_parinfo [ 5 ]
            parinfo.append ( parbase )
            parbase = { 'fixed'  : self.mpyfit_parinfo [ 6 ] [ 'fixed' ],
                        'limits' : ( intensity * 0.9, intensity * 1.1 ) }
            parinfo.append ( parbase )

        for entry in parinfo:
            self.log.debug ( "parinfo = %s" % str ( entry ) )
            
        flat = 1

        self.log.debug ( "run ( )" )

        try:
            self.log.debug ( "parameters = %s" % str ( parameters ) ) 
            fit_parameters, fit_result = mpyfit.fit ( least_mpyfit,
                                                      parameters,
                                                      args = ( self.shape_cols,
                                                               self.shape_rows,
                                                               self.wavelength,
                                                               self.data,
                                                               flat ),
                                                      parinfo = parinfo,
                                                      stepfactor = 10 )
        except Exception as e:
            print ( "Exception: %s" % str ( e ) )
            raise ( e )
        
        self.log.debug ( "fit_result [ 'bestnorm' ] = %s" % str ( fit_result [ 'bestnorm' ] ) )
        non_spammy_results = copy.copy ( fit_result )
        del ( non_spammy_results [ 'covariances' ] )
        for key in non_spammy_results.keys ( ):
            self.log.debug ( "fit_result [ {} ] = {}".format ( key, non_spammy_results [ key ] ) )

        self.log.debug ( "results:\n"
                         "\tb_ratio     = {:e},\n"
                         "\tcenter      = ( {}, {} )\n"
                         "\tcontinuum   = {:e}\n"
                         "\tfinesse     = {:e}\n"
                         "\tinitial gap = {:e}\n"
                         "\tintensity   = {:e}".format ( fit_parameters [ 0 ],
                                                         fit_parameters [ 1 ], 
                                                         fit_parameters [ 2 ], 
                                                         fit_parameters [ 3 ],
                                                         fit_parameters [ 4 ], 
                                                         fit_parameters [ 5 ],
                                                         fit_parameters [ 6 ] ) )

        self.log.debug ( "Airy fit took %ds." % ( time.time ( ) - start ) )
        self.fit = tuna.io.can ( airy_plane ( fit_parameters [ 0 ],
                                              fit_parameters [ 1 ],
                                              fit_parameters [ 2 ],
                                              fit_parameters [ 3 ],
                                              fit_parameters [ 4 ],
                                              fit_parameters [ 5 ],
                                              fit_parameters [ 6 ],
                                              self.shape_cols,
                                              self.shape_rows,
                                              self.wavelength ) )
        self.parameters = fit_parameters
