## recipe for running the LSST ``ap_pipe`` pipeline on example DECam data from the HITS survey
### February 2022

This tutorial presumes that you have v19_0_0 of the LSST science pipelines installed. v19_0_0 is a so-called "Gen 2" version of the LSST pipeline.

### initialization and raw data

Download the raw DECam science images, flats, biases and Pan-STARRS reference catalogs for the relevant sky region from the ``ap_verify_hits2015`` repository using:

```
git clone https://github.com/lsst/ap_verify_hits2015
```

For this to actually download all of the data, you need to have git-lfs installed and in your ``PATH``. You also need to have edited your ``~/.gitconfig`` and ``~/.git-credentials`` files according to https://pipelines.lsst.io/v/v19_0_0/install/git-lfs.html. If the download has worked correctly, you'll end up with 100 GB of data downloaded:

```
$ du -hs ap_verify_hits2015
100G	ap_verify_hits2015
```

If git-lfs is not properly installed/configured and in your ``PATH``, you'll end up with a failure message from the git clone command and your ``ap_verify_hits2015`` directory will only be a few MB in size. This recipe uses a version of the ``ap_verify_hits2015`` repo with most recent commit ``28e47907b485dbfea865de16639b9a8dde1b402a``.

Now begin setting up the working directory within which you will stage the necessary pipeline inputs and write processing outputs. This can be a directory anywhere on your filesystem (with sufficient disk space), and does not need to be in any special location relative to where the ``ap_verify_hits2015`` repo was cloned.

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

Where ``$INSTALL_DIR`` is the top-level path to the local v19_0_0 LSST pipeline installation. You can verify that your environment is set up with v19_0_0 of the LSST pipeline by running:

```
$ eups list lsst_distrib
   19.0.0+2   	current v19_0_0 setup
```

Say that you cloned the ``ap_verify_hits2015`` repo within a directory called ``$DATA``. Then you can bring the raw DECam data that we'll be working with into the Butler repository as follows:

```
ingestImagesDecam.py DATA --filetype raw $DATA/ap_verify_hits2015/raw/*.fz --mode=link
```

The ``mode=link`` option means that our Butler repository will hold symlinks to the raw DECam data located within the ``ap_verify_hits2015`` repo, rather than holding full copies of those files. The raw data symlinks show up within your Butler repository at ``DATA/2015-??-??/g/*.fz``.

### calibrations

Now we need to bring the calibrations into our Butler repository. The calibration products considered here are the flats, biases and defect lists. We begin by making a base directory for calibrations within the Butler repo:

```
mkdir DATA/CALIB
```

Now get ready to ingest the actual flats and biases, by creating a directory containing all of the relevant image files:

```
mkdir flats_biases
rsync -arv $DATA/ap_verify_hits2015/preloaded/DECam/calib/*/cpBias/cpBias*.fits flats_biases
rsync -arv $DATA/ap_verify_hits2015/preloaded/DECam/calib/*/cpFlat/g/*/cpFlat*.fits flats_biases
```

Then ingest the staged flats/biases into the Butler repo:

```
ingestCalibs.py DATA --calib DATA/CALIB flats_biases/*.fits --validity 999 --mode=link
```

Possibly an appropriate regexp involving ``$DATA/ap_verify_hits2015/preloaded/DECam/calib`` in the ``ingestCalibs.py`` command above would eliminate the need for copying the flat/bias FITS files into a staging directory called ``flats_biases`` as is done here.

Next, we will ingest the defect lists for DECam.

```
ingestDefects.py DATA $INSTALL_DIR/stack/miniconda3-4.7.10-4d7b902/Linux64/obs_decam_data/19.0.0/decam/defects --calib DATA/CALIB
```

Note that the defect lists are coming from the ``obs_decam_data`` repository within our LSST pipelines installation, rather than the ``ap_verify_hits2015`` repository. ``ingestDefects.py`` needs the defects to be in .ecsv text format (see [RFC-595](https://community.lsst.org/t/changes-to-how-defects-are-handled-implementation-of-rfc-595)), whereas the ``ap_verify_hits2015`` repo has a set of FITS files containing the defect lists as binary tables.

### reference catalogs

Now we will set up our reference catalogs, which come from Pan-STARRS. Start by doing:

```
mkdir DATA/ref_cats
```

Now copy the actual reference catalog files from the ``ap_verify_hits2015`` repository to our Butler repository:

```
rsync -arv $DATA/ap_verify_hits2015/preloaded/refcats/gen2/panstarrs DATA/ref_cats
mv DATA/ref_cats/panstarrs DATA/ref_cats/ps1_pv3_3pi_20170110
```

The default configuration for ``processCcd.py`` seems to require that the Pan-STARRS reference catalogs be in a directory called ``ps1_pv3_3pi_20170110`` rather than ``panstarrs``, hence the ``mv`` command. 

There are two additional necessary files for the reference catalogs: there needs to be a ``DATA/ref_cats/ps1_pv3_3pi_20170110/config.py`` and a ``DATA/ref_cats/ps1_pv3_3pi_20170110/master_schema.fits``. These files are not present in the ``ap_verify_hits2015`` repo, but they can be gathered from the ``testdata_ci_hsc`` repository used for the [v19_0_0 pipeline tutorial](https://pipelines.lsst.io/v/v19_0_0/getting-started/index.html#getting-started-tutorial) based on sample HSC data:

https://github.com/lsst/testdata_ci_hsc
https://github.com/lsst/testdata_ci_hsc/blob/f3c39b7aca3a779582da3df0ce7e6b46e7dbf001/ps1_pv3_3pi_20170110/config.py
https://github.com/lsst/testdata_ci_hsc/blob/f3c39b7aca3a779582da3df0ce7e6b46e7dbf001/ps1_pv3_3pi_20170110/master_schema.fits

These two small files can be downloaded manually/individually, or by cloning the ``testdata_ci_hsc`` repo from GitHub.

The Pan-STARRS HTM shard file names as provided in the ``ap_verify_hits2015`` repo do not follow the default/expected naming convention used when running ``processCcd.py``. In the ``ap_verify_hits2015`` repo, they have a naming convention ``panstarrs_??????_refcats_gen2.fits``, where ?????? is the HTM shard index. By default, ``processCcd.py`` expects the Pan-STARRS shard files to be named simply ``??????.fits``, where ?????? is the HTM shard index. Renaming the Pan-STARRS shard files could be done in multiple ways, for instance a small Python script:

```
#!/usr/bin/env python 

import os
import glob

flist = glob.glob('DATA/ref_cats/ps1_pv3_3pi_20170110/panstarrs*.fits')

for f in flist:
    fname_new = f.replace('/panstarrs_', '/')
    fname_new = fname_new.replace('_refcats_gen2', '')

    os.rename(f, fname_new)
```

### templates

The ``ap_verify_hits2015`` repo does not contain templates in the Gen 2 (tract, patch) format that we need. Therefore we make our own templates, starting from the set of raw DECam exposures.

The first step toward making our templates is to calibrate all of the raw single-CCD images in our dataset using ``processCcd.py``.

```
processCcd.py DATA --calib DATA/CALIB --rerun processCcdOutputs --id --longlog -j 20 &> processCcd-all.log &
```

The lack of constraints after the ``--id`` command line argument means that all CCDs will be processed. The ``--rerun`` argument specifies the subdirectory of ``DATA/rerun`` in which the outputs will be written. The ``--j 20`` argument means that we will use 20 CPUs in order to get through this processing faster. For instance, on our group's server, this calibration of ~5,000 DECam CCDs with 20 CPUs took ~3 hours, meaning that a typical CCD took ~40-45 seconds to calibrate.
