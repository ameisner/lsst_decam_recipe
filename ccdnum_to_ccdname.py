# https://pipelines.lsst.io/v/v19_0_0/py-api/lsst.obs.decam.DecamMapper.html#lsst.obs.decam.DecamMapper.detectorNames

from lsst.obs.decam import DecamMapper

mapper = DecamMapper()

mapping = mapper.detectorNames

for k in mapping.keys():
    print(k, mapping[k])
