import numpy as np
import glob
import astropy.io.fits as fits
from astropy.table import Table
import os

# basic idea is to loop over all mono_decals/flats_biases
# calibration files and figure out which are flats, biases
# and which are duplicates (in the sense of having more than one
# master bias or more than one g flat, more than one r flat, or
# more than one z flat)

t = Table()

dir = '/global/cscratch1/sd/ameisner/mono_decals/flats_biases'

flist = glob.glob(os.path.join(dir, '*.fits*'))

flist.sort()

t['fname'] = flist
n = len(flist)
filters = np.zeros(n, dtype='<U80')
obstype = np.zeros(n, dtype='<U80')
exptime = np.zeros(n, dtype=float)
caldat = np.zeros(n, dtype='U10')
proctype = np.zeros(n, dtype='<U80')
prodtype = np.zeros(n, dtype='<U80')
expnum = np.zeros(n, dtype=int)
camshut = np.zeros(n, dtype='<U80')
vsub = np.zeros(n, dtype='<U1')
photflag = np.zeros(n, dtype=int)

# would be good to also bring in the abbreviated filter from
# why am i getting e.g., Y band in here??

for i, f in enumerate(flist):
    h = fits.getheader(f)
    print(h['DTCALDAT'], h['OBSTYPE'], h['EXPTIME'], h['FILTER'])
    filters[i] = h['FILTER']
    obstype[i] = h['OBSTYPE']
    exptime[i] = h['EXPTIME']
    caldat[i] = h['DTCALDAT']
    proctype[i] = h['PROCTYPE']
    prodtype[i] = h['PRODTYPE']
    expnum[i] = h['EXPNUM']
    camshut[i] = h['CAMSHUT']
    vsub[i] = h['VSUB']
    photflag[i] = h['PHOTFLAG']

t['filter'] = filters
t['obstype'] = obstype
t['exptime'] = exptime
t['dtcaldat'] = caldat
t['proctype'] = proctype
t['prodtype'] = prodtype
t['expnum'] = expnum
t['camshut'] = camshut
t['vsub'] = vsub
t['photflag'] = photflag
