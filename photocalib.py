import lsst.daf.persistence as dafPersist
import numpy as np
import astropy.io.fits as fits

butler = dafPersist.Butler(inputs='DATA/rerun/processCcdOutputs')

dataId = {'filter': 'g', 'visit': 769479, 'ccdnum': 10}

photoCalib = butler.get("calexp_photoCalib", **dataId)

h = fits.getheader('DATA/2018-09-06/g/decam0769479.fits.fz')

exptime = h['EXPTIME']

MAGZERO = 2.5*np.log10(photoCalib.getInstFluxAtZeroMagnitude()/exptime)

print(MAGZERO)
