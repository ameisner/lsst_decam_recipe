import numpy as np
from astropy.table import Table
from lsst.daf.butler import Butler 
import glob
import os

folders = glob.glob("repo/DECam/runs/v00/*")
collections = [i.split('repo/')[1] for i in folders]
butler = Butler('repo', collections=collections)

types = ['deepCoadd_meas', 'deepCoadd_forced_src']

base_input_dir = 'repo/DECam/runs/v00/20230325T015602Z'


def get_dataids(_type='deepCoadd_meas'):
    assert(_type in types)

    basedir = os.path.join(base_input_dir, _type)

    assert(os.path.exists(basedir))

    flist = glob.glob(basedir + '/*/*/*/*.fits')

    flist.sort()

    dataids = [(int(f.split('/')[6]), int(f.split('/')[7]), f.split('/')[8], os.path.basename(f)) for f in flist]

    assert(len(set(dataids)) == len(flist))

    return dataids

def _convert_1cat(tract, patch, band, _type='deepCoadd_meas'):

    assert(_type in types)

    coaddPhotoCalib = butler.get('deepCoadd_calexp.photoCalib', band=band, 
                                  tract=tract, patch=patch)
    sources = butler.get(_type, band=band, tract=tract, patch=patch)
    calibFluxes = coaddPhotoCalib.instFluxToNanojansky(sources, 
        'base_PsfFlux')

    fluxes = calibFluxes[:, 0]
    flux_sigmas = calibFluxes[:, 1]

    return sources, fluxes, flux_sigmas

def _astropy_table(sources, fluxes, flux_sigmas):
    t = Table()

    schema = sources.getSchema()
    colnames = schema.getNames()

    for colname in colnames:
        try:
            t[colname] = sources[colname]
        except:
            print(colname, ' is bad')

    t['calibPsfFlux'] = fluxes
    t['calibPsfFlux_sigma'] = flux_sigmas

    return t

def _loop(_type='deepCoadd_meas', indstart=0, nproc=10000):

    assert(_type in types)

    dataids = get_dataids(_type=_type)

    n = len(dataids)
    
    indend = min(n, indstart+nproc)

    dataids = dataids[indstart:indend]

    for i,dataid in enumerate(dataids):
        print(i, dataid[3])
        tract,patch,band = dataid[0],dataid[1],dataid[2]
        
        sources, fluxes, flux_sigmas = _convert_1cat(tract, patch, band, 
            _type=_type)

        t = _astropy_table(sources, fluxes, flux_sigmas)

        outname = os.path.join('calib_flux_cats', _type, dataid[3])
        assert(not os.path.exists(outname))

        t.write(outname, format='fits')
