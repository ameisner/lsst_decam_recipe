import htm
import astropy.io.fits as fits
import numpy as np
import os

# /data0/ameisner/process_decam/DATA/ref_cats/ps1_pv3_3pi_20170110/config.py has:
# config.indexer['HTM'].depth=7

htm_level = 7

fname = '/data0/ameisner/process_decam/DATA/ref_cats/ps1_pv3_3pi_20170110/157338.fits'

hdul = fits.open(fname)

tab = hdul[1].data

# choose some arbitrary row from the middle of the file
row = tab[len(tab) // 2]

rad2deg = 180.0/np.pi

lon_deg = row['coord_ra']*rad2deg
lat_deg = row['coord_dec']*rad2deg

print(lon_deg, lat_deg)

print(htm.lon_lat_to_trixel(lon_deg, lat_deg, htm_level), os.path.basename(fname))
