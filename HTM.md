## using HTM utilities within the LSST v19_0_0 pipeline

HTM = Hierarchical Triangular Mesh

```
import lsst.sphgeom
htm = lsst.sphgeom.HtmPixelization(7)

from lsst.sphgeom import UnitVector3d
u = UnitVector3d(1, 0, 0)

trixel = htm.index(u)
```

Starting out with longitude and latitude:

Create an lsst.sphgeom.angle.Angle object for the latitude:

```
__init__(self: lsst.sphgeom.angle.Angle, angle: lsst.sphgeom.angle.Angle)
```

Create an lsst.sphgeom.NormalizedAngle object for the longitude:

```
__init__(self: lsst.sphgeom.normalizedAngle.NormalizedAngle, radians: float)
```

Use the NormalizedAngle and Angle objects to create a lsst.sphgeom.lonLat.LonLat object:

```
__init__(self: lsst.sphgeom.lonLat.LonLat, lon: lsst::sphgeom::NormalizedAngle, lat: lsst.sphgeom.angle.Angle)
```

Use the LonLat object to create a UnitVector3d object:

```
__init__(self: lsst.sphgeom.unitVector3d.UnitVector3d, lonLat: lsst.sphgeom.lonLat.LonLat)
```
