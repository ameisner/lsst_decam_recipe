import lsst.sphgeom
import numpy as np

def lon_lat_to_trixel(lon_deg, lat_deg, level):
    '''
    Convert longitude, latitude pair in degrees to HTM trixel number.
    
    Parameters:
        lon_deg : float
            Longitude in degrees.
        lat_deg : float
            Latitude in degrees.
        level : int
            HTM depth.
    Returns:
        trixel : int
            HTM trixel number corresponding to the input lon, lat and HTM depth.
    
    Notes:
        How to vectorize?
    '''

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
