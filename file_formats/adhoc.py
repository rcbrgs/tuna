import numpy as np
from scipy import constants as cst
import pyfits as pf
from pyfits import Column
from time import sleep
import matplotlib as mpl
from matplotlib import pyplot as plt
#import codecs

#verifier l'organisation des cubes fits si on les ouvre en python
#faire un programme readad qui voit l'extension pour savoir comment ouvir (soit ad2, ad3, ad1...)
#gestion des NaN a inclure (input/output)!!!


class dtu:
    """Data Trailer Unit
    Class associated to any adhoc format, as HDU (Header Dat Unit) for fits format

    """

    def __init__(self, data=None, trailer=None, filename=None):
        self.data = data
        self.trailer = trailer
        self.filename = filename

    def read(self, filename=None):
        return

    def trailer(self, filename=None):
        return

    def trailertoheader(self, filename=None):
        return

    def data(self, filename=None):
        return

    def writeto(self, filename=None):
        return

    def writetofits(self, fitsname):
        return

    def convertfits(self, fits, filename=None):
        return

    def tohdu(self):
        hdu = pf.PrimaryHDU(self.data)
        hdul = pf.HDUList([hdu])
        return hdul
    #l'idee est de creer une classe avec des fonctions associees. Au debut, seul le filename est utile


def ad2trailer():
    return ad2trailer


def ad3trailer():
    return ad3trailer


def readad1(filename):
    return ad1


def readad2(filename):
    """Parameters
    ----------
    filename: string
        Name of the input file

    """

    data = open(filename, 'rb')
    data.seek(0, 2)
    sz = (data.tell() - 256) / 4  # size of the data array
    data.close()

    dt = np.dtype([('data', np.float32, sz), ('trailer', [('nbdim', np.int32), ('id', np.int8, 8), ('lx', np.int32), ('ly', np.int32), ('lz', np.int32), ('scale', np.float32), ('ix0', np.int32), ('iy0', np.int32), ('zoom', np.float32), ('modevis', np.int32), ('thrshld', np.float32), ('step', np.float32), ('nbiso', np.int32), ('pal', np.int32), ('cdelt1', np.float64), ('cdelt2', np.float64), ('crval1', np.float64), ('crval2', np.float64), ('crpix1', np.float32), ('crpix2', np.float32), ('crota2', np.float32), ('equinox', np.float32), ('x_mirror', np.int8), ('y_mirror', np.int8), ('was_compressed', np.int8), ('none2', np.int8, 1), ('none', np.int32, 4), ('comment', np.int8, 128)])])
    ad2 = np.fromfile(filename, dtype=dt)

    if (ad2['trailer']['lx'] >= 32768) | (ad2['trailer']['ly'] >= 32768):
        print('Error: lx or ly seems to be invalid: (' + np.str(ad2['trailer']['lx'][0]) + ', ' + np.str(ad2['trailer']['ly'][0]) + ')')
        print('If you want to allow arrays as large as this, modify the code!')
        return

    data = ad2['data'][0].reshape(ad2['trailer']['ly'], ad2['trailer']['lx'])
    data[np.where(data == -3.1E38)] = np.nan

    ad2 = dtu(data, ad2['trailer'][0], filename)

    # tester l'existence du fichier a lire
    #ca serait bien de pouvoir lire les fichiers compresses, je crois que ca existe en python

    return ad2

    #info = file_info(realfilename)
    #testgz = strsplit(realfilename, '.', /extract)
    #testgz = testgz[n_elements(testgz)-1]

    #if (info.exists eq 0) or (info.read eq 0) or (testgz eq 'gz') then begin
    #; On regarde si plutot le fichier est .ad3.gz...
    #if (testgz ne 'gz') then begin
    #realfilename = filename + '.gz'
    #info = file_info(realfilename)
    #endif else begin
    #realfilename = filename
    #endelse

    #if (info.exists eq 0) or (info.read eq 0) then return, -1
    #if (!version.os_family ne 'unix') then return, -1

    #testgz = 'gz'
    #spawn, 'gzip -l ' + realfilename, output
    #output = strsplit(output[1], ' ', /extract)
    #size = ulong64(output[1])

    #if testgz eq 'gz' then begin
    #trailer.was_compressed = 1
    #endif


def readad3(filename, xyz=True):
    """Parameters
    ----------
    filename: string
        Name of the input file
    xyz=True: boolean (optional)
        False to return data in standard zxy adhoc format
        True  to return data in xyz format (default)

    """

    data = open(filename, 'rb')
    data.seek(0, 2)
    sz = (data.tell() - 256) / 4
    data.close()

    dt = np.dtype([('data', np.float32, sz), ('trailer', [('nbdim', np.int32), ('id', np.int8, 8), ('lx', np.int32), ('ly', np.int32), ('lz', np.int32), ('scale', np.float32), ('ix0', np.int32), ('iy0', np.int32), ('zoom', np.float32), ('xl1', np.float32), ('xi1', np.float32), ('vr0', np.float32), ('corrv', np.float32), ('p0', np.float32), ('xlp', np.float32), ('xl0', np.float32), ('vr1', np.float32), ('xik', np.float32), ('cdelt1', np.float64), ('cdelt2', np.float64), ('crval1', np.float64), ('crval2', np.float64), ('crpix1', np.float32), ('crpix2', np.float32), ('crota2', np.float32), ('equinox', np.float32), ('x_mirror', np.int8), ('y_mirror', np.int8), ('was_compressed', np.int8), ('none2', np.int8, 1), ('comment', np.int8, 128)])])
    ad3 = np.fromfile(filename, dtype=dt)

    if (ad3['trailer']['lx'][0] * ad3['trailer']['ly'][0] * ad3['trailer']['lz'][0] >= 250 * 1024 * 1024):
        print('Error: lx or ly or lz seems to be invalid: (' + np.str(ad3['trailer']['lx'][0]) + ', ' + np.str(ad3['trailer']['ly'][0]) + ', ' + np.str(ad3['trailer']['lz'][0]) + ')')
        print('If you want to allow arrays as large as this, modify the code!')
        return

    if ad3['trailer']['nbdim'] == -3:  # nbdim ?
        data = ad3['data'][0].reshape(ad3['trailer']['lz'], ad3['trailer']['ly'], ad3['trailer']['lx'])  #
    else:
        data = ad3['data'][0].reshape(ad3['trailer']['ly'], ad3['trailer']['lx'], ad3['trailer']['lz'])

    if xyz & (ad3['trailer']['nbdim'] == 3):
        #return the data ordered in z, y, x
        data = data.transpose(2, 0, 1)

    if (not xyz) & (ad3['trailer']['nbdim'] == -3):
        #return data ordered in y, x, z
        data = data.transpose(1, 2, 0)

    data[np.where(data == -3.1E38)] = np.nan
    ad3 = dtu(data, ad3['trailer'][0], filename)

    return ad3


def readadt(filename):
    return adt


def readada(filename, xsize, ysize):
    """Parameters
    ----------
    filename: string
        Name of the input ada file
    xsize: float
        Size of the final image along x-axis
    ysize: float
        Size of the final image along y-axis

    Returns
    -------
    out: ndarray
        Image corresponding to the ada

    """

    #Initialization of the image
    im = np.zeros((ysize, xsize))
    #We read the ada file
    ada = np.fromfile(filename, dtype=np.int16)
    #We reshape the data since we know the file is organize with y,x,y,x,y,x...
    data = ada.reshape(ada.size / 2, 2)
    plt.ion()
    image = plt.imshow(im)
    #we loop on each photon to create the image
    for i in range(data.shape[0]):
        #we check the location of each photon is inside the image
        if (data[i][0] < ysize) & (data[i][1] < xsize) & (data[i][0] >= 0) & (data[i][1] >= 0):
            im[data[i][0], data[i][1]] += 1
            image.set_data(im)
            #plt.draw()
            #sleep(0.1)
    plt.draw()
    return im
    #it seems that the first frame is duplicated
    #it would be nice to be able to display the creation of the image photon by photon


def readadz(filename):
    return adz


def writead1(data, trailer, filename):
    return ad1


def writead2(data, trailer, filename):
    return ad2


def writead3(data, trailer, filename):
    return ad3


def ad2tofits(filename):
    return fits


def ad3tofits(filename):
    return fits


def dtutohdu(dtu):
    hdu = pf.PrimaryHDU()
    hdr = hdu[0].header
    hdu[0].data = dtu.data
    return hdu


def hdutodtu(hdu):
    dtu = 0
    return dtu


def ad3tofits(filename):
    return fits


def ad2trailertofitsheader(ad2trailer):
    hdu = pf.PrimaryHDU()
    hdr = hdu[0].header
    #hdr.update('key','value','comment') # ajouter ou mettre a jour des keywords
    #hdr.add_history('') # indiquer la date ou la conversion a ete faite

    return fitsheader


def ad3trailertofitsheader(ad3trailer):
    hdu = pf.PrimaryHDU()
    hdr = hdu[0].header
    #hdr.update('key','value','comment') # ajouter ou mettre a jour des keywords
    #hdr.add_history('') # indiquer la date ou la conversion a ete faite

    return fitsheader


def fitstoad2(filename):
    return ad2


def fitstoad3(filename):
    return ad3


def fitsheadertoad2trailer(header):
    return ad2trailer


def fitsheadertoad3trailer(header):
    return ad3trailer
