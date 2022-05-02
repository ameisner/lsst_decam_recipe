import astropy.io.fits as fits
from astropy import wcs
import matplotlib.pyplot as plt
import decam_reduce.util as util
import os
import numpy as np

fname_raw = '/data0/ameisner/globular_cluster_m2/raw/dec113856.fits.fz'

hdul = fits.open(fname_raw)
hdu = hdul['N23']
w = wcs.WCS(hdu.header)

ra, dec = util.header_radec_to_decimal(hdul[0].header)

shards = util.getShards_decam_pointing(ra, dec, depth=7)

basedir = os.environ['PS1_FULLSKY_DIR']

rad2deg = 180.0/np.pi

xs = []
ys = []
ras = []
decs = []
for shard in shards:
    fname = os.path.join(basedir, str(shard['shard']).zfill(6) + '.fits.gz')
    assert(os.path.exists(fname))
    print(fname)

    tab = fits.getdata(fname)
    x, y = w.all_world2pix(tab['COORD_RA']*rad2deg,
                           tab['COORD_DEC']*rad2deg, 0)

    in_ccd = (x > 0) & (x < 2048) & (y > 0) & (y < 4096)
    if np.sum(in_ccd) > 0:
        xs = xs + list(x[in_ccd])
        ys = ys + list(y[in_ccd])
        ras = ras + list(tab['COORD_RA'][in_ccd]*rad2deg)
        decs = decs + list(tab['COORD_DEC'][in_ccd]*rad2deg)

plt.figure(figsize=(4, 6))
plt.scatter(xs, ys, s=1, edgecolor='none')
plt.xlabel('CCD x pixel coordinate')
plt.ylabel('CCD y pixel coordinate')
plt.title(str(hdul[0].header['EXPNUM']).zfill(7) + '_' + str(hdu.header['CCDNUM']).zfill(2))
plt.xlim((0, 2048))
plt.ylim((0, 4096))
plt.savefig('m2_reference_catalog_source_locations.png', dpi=200,
            bbox_inches='tight')
    
