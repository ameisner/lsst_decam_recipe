import glob
import matplotlib.pyplot as plt
import os
import numpy as np

def get_num_exp(basedir):
    pass

def barchart_by_ccdnum(basedir, outname=None):
    """
    Bar chart of number of exposures with calexp output for each CCDNUM.

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

    bins = np.arange(63) + 0.5
    #counts_good, bins, _ = plt.hist(ccdnums, bins)
    counts_good, bins = np.histogram(ccdnums, bins)
    print(counts_good)
    print(bins)
    assert(np.sum(counts_good) == len(flist_calexp))

    counts_bad = n_exp - counts_good

    #plt.cla()

    # stacked bar chart

    # https://matplotlib.org/stable/gallery/lines_bars_and_markers/bar_stacked.html#sphx-glr-gallery-lines-bars-and-markers-bar-stacked-py

    fig, ax = plt.subplots(figsize=(12, 4))

    labels = np.arange(1, 63)
    width = 0.8
    ax.bar(labels, counts_good, width, label='success')
    ax.bar(labels, counts_bad, width, bottom=counts_good,
           label='failure')

    #ax.set_ylabel('Scores')
    #ax.set_title('Scores by group and gender')
    ax.legend(loc='upper right')

    plt.ylim((0, n_exp*1.25))

    xlim = (-2, 65)

    plt.plot(xlim, [n_exp]*2, c='gray', linestyle=':')
    plt.xlim(xlim)

    plt.xticks(np.arange(1, 63), rotation=90)

    title = basedir + ' ; ' + str(n_exp) + ' exposures'
    plt.title(title)

    plt.xlabel('CCDNUM')
    plt.ylabel('# of CCDs')

    if outname is not None:
        # assume outname has a valid image file type suffix
        plt.savefig(outname, dpi=200, bbox_inches='tight')
        plt.cla()
    else:
        plt.show()

def _mono_decals_v6_barchart():
    basedir = '/data0/ameisner/mono_decals/v6/DATA/rerun/processCcdOutputs'

    barchart_by_ccdnum(basedir, outname='mono_decals_v6-barchart.png')

def _mono_decals_v5_barchart():
    basedir = '/data0/ameisner/mono_decals/v5/DATA/rerun/processCcdOutputs'

    barchart_by_ccdnum(basedir, outname='mono_decals_v5-barchart.png')
