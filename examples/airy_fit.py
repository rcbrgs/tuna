import logging
import math
import numpy
import threading
import time
import tuna

planes = 36

center_col  = 255
center_row  = 219
continuum   = 10
finesse     = 15
gap         = 2e-2
b_ratio     = 1e-2
initial_gap = 1e1
intensity   = 800
            
parinfo = [ ]
parbase = { 'fixed' : True }
parinfo.append ( parbase )
parbase = { 'fixed' : True }
parinfo.append ( parbase )
parbase = { 'fixed' : True }
parinfo.append ( parbase )
parbase = { 'fixed' : True }
parinfo.append ( parbase )
parbase = { 'fixed' : True }
parinfo.append ( parbase )
parbase = { 'fixed' : True }
parinfo.append ( parbase )
parbase = { 'fixed' : True }
parinfo.append ( parbase )

diversity = 0
airy_fit = numpy.ndarray ( shape = ( 36, 512, 512 ) )
for plane in range ( 36 ):
    airy_fit [ plane ] = tuna.models.airy_plane ( b_ratio,
                                                  center_col,
                                                  center_row,
                                                  continuum,
                                                  finesse,
                                                  initial_gap + plane * gap,
                                                  intensity,
                                                  512,
                                                  512,
                                                  0.6598953125 )
    diversity += numpy.amax ( airy_fit [ plane ] ) - numpy.amin ( airy_fit [ plane ] )
    #print ( "plane %d diversity = %f" % ( plane,
    #                                      diversity ) )
                                          
fit = tuna.io.can ( airy_fit )           
tuna.io.write ( array = airy_fit,
                file_format = 'fits',
                file_name = 'airy_fit.fits' )

golden = tuna.io.read ( "/home/nix/sync/tuna/sample_data/G094.AD3" )

residue = numpy.sum ( numpy.abs ( golden.array - airy_fit ) ) / ( 36 * 512 * 512 )
print ( "residue = %f, <diversity> = %f" % ( residue,
                                             diversity / planes ) )
