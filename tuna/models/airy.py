"""
This module's scope is the modeling and fitting of Airy functions to data.
"""

__version__ = "0.1.0"
__changelog__ = { "Tuna" : "0.15.0", "Change" : "Added wrapper function fit_airy" }

import copy
import logging
import math
try:
    import mpyfit
except ImportError as e:
    print ( "Could not import mpyfit. Exception: {}".format ( e ) )
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
    This function's goal is to model the Airy function as:

    .. math::
      I = C + \dfrac{I_0}{1 + \dfrac{4F^2}{\pi^2} \sin^2 (\phi/2)}

    From the input parameters, this function will return a dataset with the value for I calculated on each point. The intention is to produce a tridimensional array where each plane is an image with rings equivalent to the ones in Fabry-Pérot interferograms.

    To calculate phi:

    .. math::
      \phi = 2 \pi \dfrac{ 2 n e_i \cos (theta)} {\lambda_c }

    Where:

    .. math::
      n e_i = n ( e + i \delta_e )
      
      theta = tan^{-1} ( b r ), b = s / f


    Parameters: (In parentheses, the equation variable the paremeter corresponds to)

    * b_ratio : float : defaults to 9.e-6
        The ratio between the pixel size and the camera focal length (b).

    * center_col : integer : defaults to 256
        The column for the center of the rings, in pixels.

    * center_row : integer : defaults to 256
        The row for the center of the rings, in pixels.

    * continuum : float : defaults to 1
        The value of the background intensity.

    * finesse : float : defaults to 15
        (F).

    * gap : float : defaults to 250
        The distance between the étalons, in microns (n e_i).

    * intensity : float : defaults to 100
        The beam maximum intensity (I_0).

    * shape_cols : integer : defaults to 512
        The number of columns for the 2D shape (columns, rows) to be generated. 

    * shape_rows : integer : defaults to 512
        The number of rows for the 2D shape (columns, rows) to be generated. 

    * wavelength : float : defaults to 0.6563
        Wavelength in microns ( lambda_c ).

    Returns:

    * result : numpy.ndarray
        Contains the data for the Airy model, given the input parameters.
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

    indices_rows, indices_cols = numpy.indices ( ( shape_cols, shape_rows ) )
    distances = numpy.sqrt ( ( indices_rows - center_col ) ** 2 +
                             ( indices_cols - center_row ) ** 2 )
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
    """
    This function's goal is to wrap the airy function proper, so that the API for using mpyfit is obeyed.

    Parameters:

    * p : tuple
        Containing the b_ratio, center_col, center_row, continuum, finesse, gap and intensity values.

    * args : tuple
        Containing the shape_cols, shape_rows, wavelength, data and flat values.
    """
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
        #log.debug ( "plane = %s" % str ( plane ) )
        log.debug ( "plane.shape = {}, data.shape = {}".format ( plane.shape, data.shape ) )
    except Exception as e:
        print ( "Exception: %s" % str ( e ) )

    try:
        residue = ( plane - data ) * flat
    except Exception as e:
        log.error ( tuna.console.output_exception ( e ) ) 

    #log.debug ( "residue = %s" % str ( residue ) )
    log.debug ( "numpy.sum ( residue ) = %f" % numpy.sum ( residue ) )
    log.debug ( "/least_mpyfit" )
    return ( residue.flatten ( ) )

class airy_fitter ( threading.Thread ):
    """
    This class' responsibility is to fit the Airy function. It will use the given parameters as initial guesses. The fit will stop when the fitter converges.

    It inherits from the :ref:`threading_label`.Thread class, and it auto-starts its thread execution. Clients are expected to use its .join ( ) method before using its results.

    Its constructor signature is:

    Parameters:

    * b_ratio : float
        The ratio between the pixel size and the camera focal length (b).

    * center_col : integer
        The column for the center of the rings, in pixels.

    * center_row : integer
        The row for the center of the rings, in pixels.

    * data : numpy.ndarray
        Contains the data to be fitted.

    * finesse : float
        (F).

    * gap : float
        The distance between the étalons, in microns (n e_i).
    
    * wavelength : float 
        Wavelength in microns ( lambda_c ).

    * mpyfit_parinfo : list : defaults to [ ]
        List of parameters' boundaries, and whether they are fixed or not. Must respect mpyfit's specification.
    """

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
        self.__version__ = "0.1.5"
        self.changelog = {
            "0.1.5" : "Tuna 0.14.0 : updated docstrings to new style.",
            "0.1.4" : "Added docstrings.",
            "0.1.3" : "Tweaked xtol to 1e-6, works on some tests.",
            "0.1.2" : "Changedx xtol from 1e-10 to 1e-5 to improve speed.",
            "0.1.1" : "Refactored algorithm for getting lowest percentile into another module.",
            "0.1.0" : "Initial changelog."
            }

        self.b_ratio = b_ratio
        self.center_col = center_col
        self.center_row = center_row
        self.data = data
        self.log.debug ( "self.data.shape = {}".format ( self.data.shape ) )
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
        This method's goal is to fit an Airy model to a given input.
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
                                                      xtol = 1e-7 )
                                                      #stepfactor = 10 )
        except Exception as e:
            self.log.error ( tuna.console.output_exception ( e ) )
            self.log.error ( "Error was using parameters = {}".format ( parameters ) )
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

def fit_airy ( b_ratio : float,
               center_col : float,
               center_row : float,
               data : numpy.ndarray,
               finesse : float,
               gap : float,
               wavelength : float,
               mpyfit_parinfo : list = [ ] ) -> ( dict, tuna.io.can ):
    """
    This method's goal is to conveniently fit the Airy function. It will use the given parameters as initial guesses. The fit will stop when the fitter converges.

    It inherits from the :ref:`threading_label`.Thread class, and it auto-starts its thread execution. Clients are expected to use its .join ( ) method before using its results.

    Arguments:

    * b_ratio : float
        The ratio between the pixel size and the camera focal length (b).

    * center_col : float
        The column for the center of the rings, in pixels.

    * center_row : float
        The row for the center of the rings, in pixels.

    * data : numpy.ndarray
        Contains the data to be fitted.

    * finesse : float
        (F).

    * gap : float
        The distance between the étalons, in microns (n e_i).
    
    * wavelength : float 
        Wavelength in microns ( lambda_c ).

    * mpyfit_parinfo : list : defaults to [ ]
        List of parameters' boundaries, and whether they are fixed or not. Must respect mpyfit's specification.
    """
    fitter = airy_fitter ( b_ratio,
                           center_col,
                           center_row,
                           data,
                           finesse,
                           gap,
                           wavelength,
                           mpyfit_parinfo )
    fitter.join ( )
    return ( fitter.parameters, fitter.fit )
