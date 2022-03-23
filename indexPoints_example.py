from lsst.meas.algorithms.htmIndexer import HtmIndexer

depth = 7
htm = HtmIndexer(depth=depth)

ra = [1.0, 2.0, 3.0]
dec = [10.0, 20.0, 30.0]

trixels = htm.indexPoints(ra, dec)
