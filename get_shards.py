
from lsst.meas.algorithms.htmIndexer import HtmIndexer
from lsst.geom import degrees
from lsst.geom import SpherePoint
from astropy.table import Table

def getShards(ra, dec, radius, depth=7):
        '''
        Get HTM trixel numbers within a given radius of a sky location.

        Parameters
        ----------
            ra : float
                Right Ascension in decimal degrees.
            dec : float
                Declination in decimal degrees.
            radius : float
                Radius within which to return nearby HTM trixel numbers.

        Returns
        -------
            t : astropy.table.table.Table
                Table with the list of HTM trixel numbers and corresponding
                boolean flag indicating whether each trixel is on the boundary
                of the search region.

        Notes
        -----
            adapted from:
            https://tigress-web.princeton.edu/~pprice/ps1_pv3_3pi_20170110/README.txt

            takes ~0.001-0.002 seconds for a ~1 deg radius

            takes ~7 seconds for a 180 deg radius (all-sky), almost all of
            which is accounted for by my reformatting to Astropy table. actual
            calculations take ~5e-4 seconds for radius = 1 deg, 3e-2 seconds
            for radius = 180 deg

        '''

        htm = HtmIndexer(depth=depth)

        coord = SpherePoint(ra, dec, degrees)

        shards, onBoundary = htm.getShardIds(coord, radius*degrees)

        t = Table()
        t['shard'] = shards
        t['is_on_boundary'] = list(onBoundary)

        return t
