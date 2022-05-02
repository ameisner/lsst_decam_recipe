from lsst.meas.algorithms.htmIndexer import HtmIndexer
import astropy.io.fits as fits
from astropy.table import Table
import os

depth = 7
htm = HtmIndexer(depth=depth)

tab = fits.getdata('/data0/ameisner/healgen_for_htm-2048.fits')

trixels = htm.indexPoints(tab['LON_DEG'], tab['LAT_DEG'])

tab = Table(tab)

tab['trixel'] = trixels

outname = '/data0/ameisner/healgen_for_htm-2048-depth7.fits'

assert(not os.path.exists(outname))

tab.write(outname, format='fits')
