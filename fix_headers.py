import astropy.io.fits as fits
import os
import glob

#fname_in = 'raw_stage/c4d_150408_040549_ori.fits.fz'
#fname_out = 'raw/c4d_150408_040549_ori.fits.fz'

def _process_1file(fname_in, outdir):

    fname_out = os.path.join(outdir, os.path.basename(fname_in))

    assert(os.path.exists(outdir))
    assert(not os.path.exists(fname_out))

    hdul = fits.open(fname_in)

    #WINDDIR = 'NaN     '           / [deg] Wind direction (from North)             
    #HUMIDITY= 'NaN     '           / [%] Ambient relative humidity (outside)       
    #PRESSURE= 'NaN     '           / [Torr] Barometric pressure (outside)          
    #DIMMSEE = 'NaN     '           / [arcsec] DIMM Seeing                          
    #OUTTEMP = 'NaN     '           / [deg C] Outside temperature    

    modified = False

    if type(hdul[0].header['WINDDIR']) == str:
        hdul[0].header['WINDDIR'] = 1.0 # arbitrary choice...
        modified = True

    if type(hdul[0].header['HUMIDITY']) == str:
        hdul[0].header['HUMIDITY'] = 50.0 # arbitrary choice...
        modified = True

    if type(hdul[0].header['PRESSURE']) == str:
        hdul[0].header['PRESSURE'] = 760.0 # 1 atmosphere in torr...
        modified = True

    if type(hdul[0].header['DIMMSEE']) == str:
        hdul[0].header['DIMMSEE'] = 1.0 # arbitrary choice...
        modified = True

    if type(hdul[0].header['OUTTEMP']) == str:
        hdul[0].header['OUTTEMP'] = 11.0 # arbitrary choice
        modified = True

    if modified:
        hdul.writeto(fname_out)
    else:
        os.symlink(fname_in, fname_out)

    
def _loop(indir, outdir):
    assert(os.path.exists(indir))
    assert(os.path.exists(outdir))

    flist_in = glob.glob(indir + '/*.fz')

    flist_in.sort()
    assert(len(flist_in) > 0)

    print(len(flist_in))
    for i, fname_in in enumerate(flist_in):
        print(i, fname_in)
        _process_1file(fname_in, outdir)


def _run():
    indir = '/data0/ameisner/mono_decals/v6/raw'
    outdir = 'raw'
    _loop(indir, outdir)
