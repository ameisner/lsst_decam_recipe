#!/usr/bin/env python

import astropy.io.fits as fits
import sys
import os

#fname_in = '/data0/ameisner/ccd62_dummy/flats_biases/c4d_180905_193713_zci_v1.fits.fz'
#fname_in = '/data0/ameisner/ccd62_dummy/flats_biases/c4d_180905_201855_fci_r_v1.fits.fz'

fname_in = sys.argv[1]

assert(os.path.exists(fname_in))

hdul = fits.open(fname_in)

_hdul = hdul[0:61]

_hdul.append(_hdul[60])
_hdul.append(hdul[61])

for i, hdu in enumerate(_hdul):
    if 'CCDNUM' in hdu.header:
        print(i, hdu.header['CCDNUM'], i == hdu.header['CCDNUM'])

outname_tmp = fname_in + '.tmp'

_hdul.writeto(outname_tmp)
