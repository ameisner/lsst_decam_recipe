## using HTM utilities within the LSST v19_0_0 pipeline

HTM = Hierarchical Triangular Mesh

```
import lsst.sphgeom
htm = lsst.sphgeom.HtmPixelization(7)

from lsst.sphgeom import UnitVector3d
u = UnitVector3d(1, 0, 0)

trixel = htm.index(u)
```
