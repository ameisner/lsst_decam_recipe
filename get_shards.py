# adapted from:
# https://tigress-web.princeton.edu/~pprice/ps1_pv3_3pi_20170110/README.txt

from lsst.meas.algorithms.htmIndexer import HtmIndexer
##from lsst.afw.coord import IcrsCoord
from lsst.geom import degrees
from lsst.geom import SpherePoint
from astropy.table import Table

def getShards(ra, dec, radius, depth=7):
        htm = HtmIndexer(depth=depth)

        coord = SpherePoint(ra, dec, degrees)

        shards, onBoundary = htm.getShardIds(coord, radius*degrees)

        t = Table()
        t['shard'] = shards
        t['is_on_boundary'] = list(onBoundary)

        return t
