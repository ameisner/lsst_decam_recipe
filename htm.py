import lsst.sphgeom
import numpy as np

def lon_lat_to_trixel(lon_deg, lat_deg, level):
    # level is HTM level (integer)
    # vectorization?

    deg2rad = np.pi/180

    lon_rad = lon_deg*deg2rad
    lat_rad = lat_deg*deg2rad

    lon = lsst.sphgeom.normalizedAngle.NormalizedAngle(lon_rad)
    lat = lsst.sphgeom.angle.Angle(lat_rad)

    lonlat = lsst.sphgeom.lonLat.LonLat(lon, lat)

    u = lsst.sphgeom.UnitVector3d(lonlat)

    htm = lsst.sphgeom.HtmPixelization(level)
    trixel = htm.index(u)

    return trixel
