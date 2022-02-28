## recipe for running the LSST ap_pipe pipeline on example DECam data from the HITS survey
### February 2022

This tutorial presumes that you have v19_0_0 of the LSST science pipelines installed.

Download the raw DECam science images, flats, biases and Pan-STARRS reference catalogs from the ap_verify_hits2015 repository using:

git clone https://github.com/lsst/ap_verify_hits2015

For this to actually download all of the data, you need to have git-lfs installed and in your path. If this has worked correctly, you'll end up with 100 GB of data downloaded:

```
$ du -hs ap_verify_hits2015
100G	ap_verify_hits2015
```

