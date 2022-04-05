#!/usr/bin/env python

import argparse
import requests
import full_decam_filter_name
import json
import os
import pandas as pd

def query_night(night):
    # query the /short api
    # handling of failed queries? retry in that case?

    url_short = 'https://astroarchive.noirlab.edu/api/short/ct4m/decam/' + \
                night + '/'
    nightsum = pd.DataFrame(requests.get(url_short).json()[1:])

    return nightsum

def raw_science_frames(nightsum, min_exptime_s=1.0):

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
    return result

def download_images(df, outdir):
    # df could be either the set of raw science exposures or
    # set of calibration images to download

    # could parallelize for speed-up?
    
    assert(os.path.exists(outdir))

    for i in range(len(df)):
        print(i+1, ' of ', len(df))
        url = df['url'].iloc[i]
        r = requests.get(url, allow_redirects=True)

        outname = os.path.join(outdir,
                               os.path.basename(df['archive_filename'].iloc[i]))

        print(url, outname)

        assert(not os.path.exists(outname))
        open(outname, 'wb').write(r.content)
    
def download_raw_science(df):
    pass

def download_calibs(df):
    pass

def download_ps1_shards(ras, decs):
    import get_shards

    # get shards list for each ra, dec then do downloads for the
    # unique set

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

    # I guess filter here should be an abbreviated name like 'u', 'g', 'r', ...
    # rather than the full filter name?
    parser.add_argument('--filter', default=None, type=str,
                        help="only process raw science data with this filter")

    # PROPID format?
    parser.add_argument('--propid', default=None, type=str,
                        help="only process raw science data with this propid")
