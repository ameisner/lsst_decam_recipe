#!/usr/bin/env python

import argparse
import requests
import full_decam_filter_name
import json
import os
import pandas as pd
from astropy.table import vstack
import numpy as np

def query_night(night):
    # query the /short api
    # handling of failed queries? retry in that case?

    url_short = 'https://astroarchive.noirlab.edu/api/short/ct4m/decam/' + \
                night + '/'
    nightsum = pd.DataFrame(requests.get(url_short).json()[1:])

    return nightsum

def select_raw_science(nightsum, min_exptime_s=1.0):

    # nightsum is a pandas dataframe of the sort that would be returned
    #     by query_night
    # filter the data based on some min exposure time
    # needs to be a science frame (OBSTYPE == 'object' ?)
    # for now restrict to u, g, r, i, z, Y (?)
    # proc_type == raw
    # prod_type == image
    # sort the output by something? by EXPID? looks like EXPID isn't available

    keep = (nightsum['proc_type'] == 'raw') & \
           (nightsum['prod_type'] == 'image') & \
           (nightsum['obs_type'] == 'object') & \
           (nightsum['exposure'] >= 1)

    # what to do for edge case in which nothing is retained?
    result = nightsum[keep]

    result = result.sort_values('original_filename')

    return result

def select_mastercal(nightsum):

    keep = (nightsum['proc_type'] == 'mastercal') & \
           (nightsum['prod_type'] == 'image') & \
           ((nightsum['obs_type'] == 'dome flat') | \
            (nightsum['obs_type'] == 'zero'))

    result = nightsum[keep]

    return result

def download_images(df, outdir):
    # df could be either the set of raw science exposures or
    # set of calibration images to download

    # could parallelize for speed-up?
    
    assert(os.path.exists(outdir))

    for i in range(len(df)):
        print(i+1, ' of ', len(df))
        url = df['url'].iloc[i]

        outname = os.path.join(outdir,
                               os.path.basename(df['archive_filename'].iloc[i]))

        print(url, outname)

        assert(not os.path.exists(outname))

        r = requests.get(url, allow_redirects=True)
        open(outname, 'wb').write(r.content)

def download_raw_science(df):
    print('DOWNLOADING RAW SCIENCE FRAMES')
    outdir = 'raw'
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    download_images(df, outdir)

def download_calibs(df):
    print('DOWNLOADING NIGHTLY MASTER CALIBRATIONS')
    outdir = 'flats_biases'
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    download_images(df, outdir)

def download_ps1_shards(ras, decs):
    import get_shards

    # check that ras, decs have same number of elements?

    # get shards list for each ra, dec then do downloads for the
    # unique set

    margin = 0.1 # deg, not sure...
    tables = []
    for i in range(len(ras)):
        shards = get_shards.getShards_decam_pointing(ras[i], decs[i], depth=7,
                                                     margin=margin)
        tables.append(shards)

    table = vstack(tables)

    shards = np.unique(table['shard'])

    base_url = 'http://tigress-web.princeton.edu/~pprice/ps1_pv3_3pi_20170110/'

    outdir = 'ps1_pv3_3pi_20170110'
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    for i, shard in enumerate(shards):
        print(i+1, ' of ', len(shards))
        _name = str(shard) + '.fits'
        url = os.path.join(base_url, _name)
        print(url)

        outname = os.path.join(outdir, _name)
        r = requests.get(url, allow_redirects=True)
        open(outname, 'wb').write(r.content)

# get list of files from /short API
# get unique list of filters (maybe not strictly necessary)
# download/ingest the calibs (flats) for those filters
# download/ingest the bias for this night
#     deal with fringe corr for z/Y
# code to locate calibs from adjacent nights if needed
# workaround for mastercal w/ wrong OBSTYPE?
# figure out the list of HTM files
#    download those from princeton server
# create script for building butler repo and also the processCcd.py command
# use DECaLS night = 2018-09-05 as a test case

def write_staging_script():
    pass

def write_launch_script(outname):

    cmd = 'processCcd.py DATA --calib DATA/CALIB --rerun processCcdOutputs --id --longlog -j 20'

    with open(outname, 'wb') as f:
        f.write(cmd.encode('ascii'))

def _proc(caldat, limit=None):
    print('WORKING ON NIGHT ' + caldat)

    nightsum = query_night('2018-09-05')
    
    raw = select_raw_science(nightsum)

    if limit is not None:
        raw = raw[0:limit]

    calib = select_mastercal(nightsum)

    download_raw_science(raw)

    download_calibs(calib)

    download_ps1_shards(np.array(raw['ra_min']),
                        np.array(raw['dec_min']))

    write_staging_script()
    write_launch_script()
    
if __name__ == "__main__":
    descr = 'process a night of raw DECam data'

    parser = argparse.ArgumentParser(description=descr)

    parser.add_argument('caldat', type=str, nargs=1,
                        help="observing night in YYYY-MM-DD format")

    parser.add_argument('--repo_name', default='DATA', type=str,
                        help="Butler repository name")

    parser.add_argument('--staging_script_name', default='stage.sh', type=str,
                        help="output name for repo staging script")

    parser.add_argument('--launch_script_name', default='launch.sh', type=str,
                        help="output name for processing launch script")

    parser.add_argument('--multiproc', default=None, type=int,
                        help="number of threads for multiprocessing")

    parser.add_argument('--limit', default=None, type=int,
                        help="process only first limit exposures")
    
    # I guess filter here should be an abbreviated name like 'u', 'g', 'r', ...
    # rather than the full filter name?
    parser.add_argument('--filter', default=None, type=str,
                        help="only process raw science data with this filter")

    # PROPID format?
    parser.add_argument('--propid', default=None, type=str,
                        help="only process raw science data with this propid")

    args = parser.parse_args()

    _proc(args.caldat[0], limit=args.limit)
