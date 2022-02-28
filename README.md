## recipe for running the LSST ``ap_pipe`` pipeline on example DECam data from the HITS survey
### February 2022

This tutorial presumes that you have v19_0_0 of the LSST science pipelines installed. v19_0_0 is a so-called "Gen 2" version of the LSST pipeline.

Download the raw DECam science images, flats, biases and Pan-STARRS reference catalogs from the ``ap_verify_hits2015`` repository using:

```
git clone https://github.com/lsst/ap_verify_hits2015
```

For this to actually download all of the data, you need to have git-lfs installed and in your ``PATH``. You also need to have edited your ``~/.gitconfig`` and ``~/.git-credentials`` files according to https://pipelines.lsst.io/v/v19_0_0/install/git-lfs.html. If the download has worked correctly, you'll end up with 100 GB of data downloaded:

```
$ du -hs ap_verify_hits2015
100G	ap_verify_hits2015
```

If git-lfs is not installed and in your ``PATH``, you'll end up with a failure message from the git clone command and your ``ap_verify_hits2015`` directory will only be a few MB in size. This recipe uses a version of the ``ap_verify_hits2015`` repo with most recent commit ``28e47907b485dbfea865de16639b9a8dde1b402a``.

Now begin setting up the working directory within which you will stage the necessary inputs and write processing outputs. This can be a directory anywhere on your filesystem (with sufficient disk space), and does not need to be in any special location relative to where the ``ap_verify_hits2015`` repo was cloned to.

Now we start setting up the Butler repository, which we will choose to be a directory called ``DATA``. Within your chosen working directory, do:

```
mkdir DATA
echo lsst.obs.decam.DecamMapper > DATA/_mapper
```

Before running any of the Butler ingestion Python commands, we need to make sure our environment is set up to use the LSST pipelines:

```
source $INSTALL_DIR/loadLSST.bash
setup lsst_distrib
```

Where ``$INSTALL_DIR`` is the top-level path to the local v19_0_0 LSST pipeline installation. You can verify that your environment is set up with an LSST pipeline installation by running:

```
$ eups list lsst_distrib
   19.0.0+2   	current v19_0_0 setup
```

Say that you cloned the ``ap_verify_hits2015`` repo within a base directory called ``$DATA``. Then you can bring the raw DECam data that we'll be working with into the Butler repository as follows:

```
ingestImagesDecam.py DATA --filetype raw $DATA/ap_verify_hits2015/raw/*.fz --mode=link
```

The ``mode=link`` option means that our Butler repository will hold symlinks to the raw DECam data located within the ``ap_verify_hits2015`` repo, rather than holding full copies of those files. The raw data symlinks show up within your Butler repository at ``DATA/2015-??-??/g/*.fz``.

Now we need to bring the calibrations into our Butler repository. The calibration products considered here are the flats, biases and defect lists. We begin by making a base directory for calibrations within the Butler repo:

```
mkdir DATA/CALIB
```

Now get ready to ingest the actual flats and biases, by creating a simple directory containing all of the relevant image files:

```
mkdir flats_biases
rsync -arv $DATA/ap_verify_hits2015/preloaded/DECam/calib/*/cpBias/cpBias*.fits flats_biases
rsync -arv $DATA/ap_verify_hits2015/preloaded/DECam/calib/*/cpFlat/g/*/cpFlat*.fits flats_biases
```

Then ingest the staged flats/biases into the Butler repo:

```
ingestCalibs.py DATA --calib DATA/CALIB flats_biases/*.fits --validity 999 --mode=link
```

Possibly an appropriate regexp in the ``ingestCalibs.py`` command above would eliminate the need for copying the flat/bias FITS files into a staging directory called ``flats_biases`` as is done here.
