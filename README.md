## recipe for running the LSST ``ap_pipe`` pipeline on example DECam data from the HITS program
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

Now we need to bring the calibrations into our Butler repository. The calibration products considered here are flats, biases and defect lists. We begin by making a top-level directory for calibrations within the Butler repo:

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

These two small files can be downloaded by cloning the ``testdata_ci_hsc`` repo from GitHub (in order to get the ``master_schema.fits`` file, the same considerations as before about git-lfs apply).

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

### per-CCD processing

The ``ap_verify_hits2015`` repo does not appear to contain templates in the Gen 2 (tract, patch) format that we need. Therefore we make our own templates, starting from the set of raw DECam exposures.

The first step toward making our templates is to calibrate all of the raw single-CCD images in our dataset using ``processCcd.py``:

```
processCcd.py DATA --calib DATA/CALIB --rerun processCcdOutputs --id --longlog -j 20 &> processCcd-all.log &
```

The lack of constraints after the ``--id`` command line argument means that all CCDs will be processed. The ``--rerun`` argument specifies the subdirectory of ``DATA/rerun`` in which the outputs will be written (you don't need to manually create the ``DATA/rerun`` directory before running this ``processCcd`` command). The ``--j 20`` argument means that we will use 20 CPUs in order to get through this processing faster. For instance, on our group's server, this calibration of ~5,000 DECam CCDs with 20 CPUs took ~3 hours, meaning that a typical CCD took ~40-45 seconds to calibrate.

The ``DATA/rerun/processCcdOutputs`` directory now has one output directory per exposure in this data set. Note that the total data volume of the ``DATA/rerun/processCcdOutputs`` outputs is 300+ GB!

### building coadds from the calibrated CCDs

Now that we have the calibrated CCDs, we need to assemble them into coadds. To do this, we follow the instructions at:

https://pipelines.lsst.io/v/v19_0_0/getting-started/coaddition.html

Which pertain to a sample HSC dataset, but can be very similarly applied to the DECam/HITS dataset.

Our HITS sample dataset contains three distinct fields (named Blind15A_26, Blind15A_40, and Blind15A_42), so we make one template per field. The first step is to define the map projection that will be used for each reference template:

```
makeDiscreteSkyMap.py DATA --id object=Blind15A_26 --rerun processCcdOutputs:coadd_26 --config skyMap.projection="TAN"
makeDiscreteSkyMap.py DATA --id object=Blind15A_40 --rerun processCcdOutputs:coadd_40 --config skyMap.projection="TAN"
makeDiscreteSkyMap.py DATA --id object=Blind15A_42 --rerun processCcdOutputs:coadd_42 --config skyMap.projection="TAN"
```

In the ``--rerun`` argument, we are "chaining" each field's coadd output to ``processCcdOutputs`` via the ``processCcdOutputs:coadd_??`` syntax. The above commands create new directories ``DATA/rerun/coadd_26``, ``DATA/rerun/coadd_40`` and ``DATA/rerun/coadd_42``. These sky maps each cover a small enough sky region that they will be just one "tract". The ``makeDiscreteSkyMap.py`` commands above also automatically figure out the number of coadd "patches" needed to cover the tract region. For instance, the last line of printed output from the first ``makeDiscreteSkyMap.py`` command above is:

```
makeDiscreteSkyMap INFO: tract 0 has corners (151.232, 1.103), (149.012, 1.103), (149.010, 3.322), (151.233, 3.322) (RA, Dec deg) and 6 x 6 patches
```

Which tells us that the tract has been broken up into a 6 x 6 grid of patches. The above commands also make files called ``DATA/rerun/coadd_??/deepCoadd/skyMap.pickle``, which can be loaded and inspected to see various map projection parameters (particularly via the ``.config`` attribute of the DiscreteSkyMap object).

The next step toward template coaddition is warping the calibrated CCD images onto the template sky map projection. This is accomplished via:

```
makeCoaddTempExp.py DATA --rerun coadd_26 \
    --selectId filter=g object=Blind15A_26 \
    --id filter=g tract=0 patch=0,0^0,1^0,2^0,3^0,4^0,5^1,0^1,1^1,2^1,3^1,4^1,5^2,0^2,1^2,2^2,3^2,4^2,5^3,0^3,1^3,2^3,3^3,4^3,5^4,0^4,1^4,2^4,3^4,4^4,5^5,0^5,1^5,2^5,3^5,4^5,5 \
    --config doApplyUberCal=False doApplySkyCorr=False &> makeCoaddTempExp_26.log &

makeCoaddTempExp.py DATA --rerun coadd_40 \
    --selectId filter=g object=Blind15A_40 \
    --id filter=g tract=0 patch=0,0^0,1^0,2^0,3^0,4^0,5^1,0^1,1^1,2^1,3^1,4^1,5^2,0^2,1^2,2^2,3^2,4^2,5^3,0^3,1^3,2^3,3^3,4^3,5^4,0^4,1^4,2^4,3^4,4^4,5^5,0^5,1^5,2^5,3^5,4^5,5 \
    --config doApplyUberCal=False doApplySkyCorr=False -j 20 &> makeCoaddTempExp_40.log &
    
makeCoaddTempExp.py DATA --rerun coadd_42 \
    --selectId filter=g object=Blind15A_42 \
    --id filter=g tract=0 patch=0,0^0,1^0,2^0,3^0,4^0,5^1,0^1,1^1,2^1,3^1,4^1,5^2,0^2,1^2,2^2,3^2,4^2,5^3,0^3,1^3,2^3,3^3,4^3,5^4,0^4,1^4,2^4,3^4,4^4,5^5,0^5,1^5,2^5,3^5,4^5,5 \
    --config doApplyUberCal=False doApplySkyCorr=False -j 20 &> makeCoaddTempExp_42.log &
```

Specifying ``--filter=g`` is probably not needed due to the fact that all images in this sample data set are in g-band. Note that we're selecting input data by field with the ``object=Blind15A_42`` criterion for the ``--selectId`` argument. The first command runs all of the per-CCD warping in serial, while the second and third use 20 CPUs in each case (``-j 20`` command line argument).

The full list of patches needs to be explicitly specified, which feels somewhat clunky given that with 6 x 6 patches we have to specify 36 caret-separated pairs, where each pair gives the indices of a particular patch in the two-dimensional grid of patches (zero-indexed).

Here's a small Python script that can generate these lists:

```
def _patches(n):
    # n x n set of patches

    result = ''
    for i in range(0, n):
        for j in range(0, n):
            pair = str(i)+','+str(j)
            result += pair
            if (i != (n-1)) | (j != (n-1)):
                result += '^'

    print(result)
```

Now we can run the actual coaddition:

```
assembleCoadd.py DATA --rerun coadd_26 \
    --selectId filter=g object=Blind15A_26 \
    --id filter=g tract=0 patch=0,0^0,1^0,2^0,3^0,4^0,5^1,0^1,1^1,2^1,3^1,4^1,5^2,0^2,1^2,2^2,3^2,4^2,5^3,0^3,1^3,2^3,3^3,4^3,5^4,0^4,1^4,2^4,3^4,4^4,5^5,0^5,1^5,2^5,3^5,4^5,5 --longlog &> assembleCoadd-26.log &
```

Only the Blind15A_26 case is shown here. The per-patch coaddition outputs are written to files ``DATA/rerun/coadd_26/deepCoadd/g/0/*.fits``. There are 32 such files -- not every single patch ends up having CCDs that overlap with its footprint.

### running the alert pipeline

For each field, its respective ``DATA/rerun/coadd_??`` will be specified to ``ap_pipe.py`` as the template location. For field Blind15A_26, we have:

```
mkdir ppdb/
make_ppdb.py -c ppdb.isolation_level=READ_UNCOMMITTED -c ppdb.db_url="sqlite:///ppdb/association.db"
ap_pipe.py DATA --calib DATA/CALIB --rerun processed -c ppdb.isolation_level=READ_UNCOMMITTED -c ppdb.db_url="sqlite:///ppdb/association.db" --id visit=411858 ccdnum=42 filter=g --template DATA/rerun/coadd_26 --longlog &> ap_26.log &
```

Output information gets written to ``ppdb/association.db``, and also ``DATA/rerun/processed``. Note that EXPID = 411858 was chosen because it is an observation of the Blind15A_26 field.

### appendix A: using the Butler sqlite3 database files

When raw data are ingested, a database file called ``DATA/registry.sqlite3`` is created. Checking this database can be useful as a debugging tool and to explore the dataset. For instance:

```
$ sqlite3 DATA/registry.sqlite3 
sqlite> .tables
raw        raw_visit
sqlite> select distinct FILTER from raw;
g
sqlite> select distinct OBJECT from raw;
Blind15A_26
Blind15A_40
Blind15A_42
sqlite> .header ON
sqlite> select * from raw limit 2;
id|visit|filter|date|taiObs|expTime|ccdnum|ccd|hdu|instcal|dqmask|wtmap|proposal|object
1|410915|g|2015-02-17|2015-02-17T03:22:34.400354|86.0|25|25|1||||2015A-0608|Blind15A_26
2|410915|g|2015-02-17|2015-02-17T03:22:34.400354|86.0|26|26|2||||2015A-0608|Blind15A_26
```

Similarly, when calibrations are ingested, another database file called ```DATA/CALIB/calibRegistry.sqlite3``` is created. Inspecting this database can be useful. For instance, at one point when I was wrongly trying to ingest defect lists from FITS binary tables in the ```ap_verify_hits2015``` repo, I noticed that the defects table within ```calibRegistry.sqlite3``` was empty.

```
$ sqlite3 DATA/CALIB/calibRegistry.sqlite3 
sqlite> .tables
bias            dark_visit      flat            fringe_visit  
bias_visit      defects         flat_visit      illumcor      
dark            defects_visit   fringe          illumcor_visit
sqlite> .header ON
sqlite> select * from defects limit 3;
id|filter|ccdnum|calibDate|validStart|validEnd
1|NONE|32|1970-01-01T00:00:00|1970-01-01|2013-01-14
2|NONE|32|2013-01-15T01:30:00|2013-01-15|2013-09-15
3|NONE|32|2013-09-16T09:26:00|2013-09-16|2014-01-16
```

### appendix B: making your own reference catalogs
