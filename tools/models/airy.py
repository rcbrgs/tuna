import numpy

def create_airy_array ( I0=1., lamb=0.6563, F=15, n=1, e=1000., fcam=0.1, pix=9., x=512, y=512, xc=256, yc=256 ):

    '''
    Airy function in order to compute a ring
    Originally written by Benoît Epinat.

    Parameters
    ----------

    I0=1. : float
    intensity
    lamb=0.6563 : float
    wavelength (micron),
    F=15 : float
    finesse,
    n=1 : float
    reflexion index,
    e=1000. : float
    spacing between the two FP plates (micron),
    fcam=0.1 : float
        focal length of the camera (meter),
    pix=9. : float
        pixel size (micron),
    x=512 : integer
        x-size of the image,
    y=512 : integer
        y-size of the image,
    xc=256 : float
        ring center x coordinate,
    yc=256 : float
    ring center y coordinate.

    Return
    ------

    out : ndarray
    An image of a ring with the above parameters given as input
    '''
    
    image = numpy.zeros((y,x))
    # we need the indices of the pixels in image
    ind = numpy.indices((y,x))
    # we use numpy sqrt function because we compute on arrays
    rpix = numpy.sqrt((ind[1]-xc)**2+(ind[0]-yc)**2)
    # radius unit = meter
    r = rpix*pix*(1.e-6)
    theta = numpy.arctan(r/fcam)
    # function of Airy I
    f = 4.0*((F**2))/(numpy.pi**2)
    phi = 2.0*numpy.pi*( ( 2*n*e*(numpy.cos(theta)) )/(lamb) )
    I = I0 / ( 1. + f*(numpy.sin(phi/2.0))**2 )

    return I
