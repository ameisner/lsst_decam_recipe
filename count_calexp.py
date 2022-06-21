import glob
import matplotlib.pyplot as plt
import os
import numpy as np

def get_num_exp(basedir):
    pass

def hist_by_ccdnum(basedir):
    """
    Histogram of number of exposures with calexp output for each CCDNUM.

    Notes
    -----
        Add a boolean switch to plot # of failures rather than # of successes?

    """

    # example basedir would be :
    # /data0/ameisner/mono_decals/v6/DATA/rerun/processCcdOutputs

    assert(os.path.exists(basedir))

    expdirs = glob.glob(os.path.join(basedir, '???????'))

    n_exp = len(expdirs)

    assert(n_exp > 0)

    flist_calexp = glob.glob(basedir + '/???????/calexp/calexp*')

    print(len(flist_calexp))

    ccdnums = np.zeros(len(flist_calexp), dtype=int)
    for i, f in enumerate(flist_calexp):
        tokens = os.path.basename(f).split('_')
        ccdnums[i] = int(tokens[1][0:2])

    bins = np.arange(62)
    plt.hist(ccdnums, bins)
    plt.show()

def _test():
    basedir = '/data0/ameisner/mono_decals/v6/DATA/rerun/processCcdOutputs'

    hist_by_ccdnum(basedir)
