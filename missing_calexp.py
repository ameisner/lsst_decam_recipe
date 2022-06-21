import glob
import matplotlib.pyplot as plt
import os
import numpy as np
import decam_reduce.util as util
import pandas as pd
import astropy.io.fits as fits
import decam_reduce.plotting as plotting

def missing_calexp(basedir):
    # get list of exposures
    # loop over 1 -> 62 inclusive testing for calexp/calexp_

    # example of basedir is
    # /data0/ameisner/mono_decals/v6/DATA/rerun/processCcdOutputs

    expdirs = glob.glob(os.path.join(basedir, '???????'))

    expdirs.sort()

    indstr = fits.getdata('/home/ameisner/decam_reduce/py/decam_reduce/data/decals_unique_nights.fits')

    ccdnums = np.arange(1, 63)
    missing = []
    for expdir in expdirs:
        for ccdnum in ccdnums:
            if ccdnum in [2, 61]:
                continue
            suffix = str(ccdnum).zfill(2) + \
                         '.fits'
            fname_pred = 'calexp-' + os.path.basename(expdir) + \
                         '_' + suffix
            fname_pred = os.path.join(basedir, os.path.basename(expdir),
                                      'calexp', fname_pred)
            #print(fname_pred)
            if not os.path.exists(fname_pred):
                fname_good = fname_pred.replace(suffix, '06.fits')
                assert(os.path.exists(fname_good))
                h = fits.getheader(fname_good)
                missing.append((fname_pred, ccdnum, int(os.path.basename(expdir)), h['DTCALDAT']))
                

    # at the end, print out a list of the missing calexp images
    #for m in missing:
    #    print(m[0], m[1], util.ccdnum_to_ccdname(m[1]))

    t = pd.DataFrame()
    expnum_missing = [m[2] for m in missing]
    ccdnum_missing = [m[1] for m in missing]
    ccdname_missing = [util.ccdnum_to_ccdname(m[1]) for m in missing]

    t['expnum'] = expnum_missing
    t['night'] = [m[3] for m in missing]
    t['ccdnum'] = ccdnum_missing
    t['ccdname'] = ccdname_missing

    return t


def _test():
    basedir = '/data0/ameisner/mono_decals/v6/DATA/rerun/processCcdOutputs'
    df = missing_calexp(basedir)

    print(df)
    print()
    print('unique nights with missing CCDs :', np.unique(df['night']))
    print()
    print('unique EXPNUM with missing CCDs :', np.unique(df['expnum']))
    return df


def _get_fname_raw(expnum):
    raw_dir = '/data0/ameisner/mono_decals/v6/raw'
    flist_raw = glob.glob(os.path.join(raw_dir, '*.fits.fz'))

    for f in flist_raw:
        h = fits.getheader(f)
        if h['EXPNUM'] == expnum:
            return f

def _v6_missing_fp_plots():

    df = _test()

    expnums = np.unique(df['expnum'])

    for expnum in expnums:
        # construct raw file name
        fname_raw = _get_fname_raw(expnum)
        rerun_dir = '/data0/ameisner/mono_decals/v6/DATA/rerun/processCcdOutputs'
        plotting.outputs_fp_map(fname_raw, rerun_dir, save=False, 
                                outname_extra='', title_extra='')
