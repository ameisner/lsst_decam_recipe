## recipe for running the LSST ap_pipe pipeline on example DECam data from the HITS survey
### February 2022

This tutorial presumes that you have v19_0_0 of the LSST science pipelines installed.

Download the raw DECam science images, flats, biases and Pan-STARRS reference catalogs from the ``ap_verify_hits2015`` repository using:

```
git clone https://github.com/lsst/ap_verify_hits2015
```

For this to actually download all of the data, you need to have git-lfs installed and in your ``PATH``. If this has worked correctly, you'll end up with 100 GB of data downloaded:

```
$ du -hs ap_verify_hits2015
100G	ap_verify_hits2015
```

If git-lfs is not installed and in your ``PATH``, you'll end up with a failure message from the git clone command and your ``ap_verify_hits2015`` directory will only be a few MB in size.

Now begin setting up the working directory you will use for staging the necessary inputs and writing outputs. This can be a directory anywhere on your filesystem (with sufficient disk space), and does not need to be in any special location relative to where the ``ap_verify_hits2015`` repo was cloned to.

Now we start setting up the Butler repository, which we will choose to be a directory called ``DATA``. Within your chosen working directory, do:

```
mkdir DATA
echo lsst.obs.decam.DecamMapper > DATA/_mapper
```

Say that you cloned the ``ap_verify_hits2015`` repo within a base directory called ``$DATA``. Then you can bring the raw DECam data that we'll be working with into the Butler repository as follows:

```
ingestImagesDecam.py DATA --filetype raw $DATA/ap_verify_hits2015/raw/*.fz --mode=link
```

The ``mode=link`` option means that our Butler repository will hold symlinks to the raw DECam data within the ``ap_verify_hits2015`` repo, rather than holding full copies of those files.
