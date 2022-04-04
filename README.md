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

### reference catalogs (see appendix B for alternate method)

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

### running the alert pipeline: coadd template

For each field, its respective ``DATA/rerun/coadd_??`` will be specified to ``ap_pipe.py`` as the template location. For field Blind15A_26, we have:

```
mkdir ppdb/
make_ppdb.py -c ppdb.isolation_level=READ_UNCOMMITTED -c ppdb.db_url="sqlite:///ppdb/association.db"
ap_pipe.py DATA --calib DATA/CALIB --rerun processed -c ppdb.isolation_level=READ_UNCOMMITTED -c ppdb.db_url="sqlite:///ppdb/association.db" --id visit=411858 ccdnum=42 filter=g --template DATA/rerun/coadd_26 --longlog &> ap_26.log &
```

Output information gets written to ``ppdb/association.db``, and also ``DATA/rerun/processed``. Note that EXPID = 411858 was chosen because it is an observation of the Blind15A_26 field.

### running the alert pipeline: calexp template

It is also possible to run the alert pipeline using calibrated single-exposure data as the template. This can be accomplished with:

```
mkdir ppdb_calexp
make_ppdb.py -c ppdb.isolation_level=READ_UNCOMMITTED -c ppdb.db_url="sqlite:///ppdb_calexp/association.db"

ap_pipe.py DATA --calib DATA/CALIB --rerun processed_calexp -C $AP_PIPE_DIR/config/calexpTemplates.py -c ppdb.isolation_level=READ_UNCOMMITTED -c ppdb.db_url="sqlite:///ppdb_calexp/association.db" --id visit=411858 ccdnum=42 filter=g --templateId visit=410915 date=2015-02-17 &> ap_calexp_26.log &
```

Both exposures (visit=411858, 410915) were selected to be pointed at the Blind15A_26 field, so that ccdnum=42 in the two exposures are overlapping. Note that it is important to include `date=2015-02-17` within the `--templateId` data selection; if this date is not specified then the Butler assumes that the reference and science image have the same date, which is not the case in general (here the reference has date = 2015-02-17 and the science image has date = 2015-02-19).

Note also that the above command performs CCD level calibration on both the template and science CCDs, starting from the raw data; I tried but did not succeed at getting `ap_pipe.py` to use an existing rerun with calexp products already available.

A close variant of the above `ap_pipe.py` calexp command will process all CCDs in exposure 411858. Simply delete the `ccdnum=42` specification from the `--id` filtering:

```
rm -rf ppdb_calexp_many
rm -rf DATA/rerun/processed_calexp_many

mkdir ppdb_calexp_many
make_ppdb.py -c ppdb.isolation_level=READ_UNCOMMITTED -c ppdb.db_url="sqlite:///ppdb_calexp_many/association.db"

ap_pipe.py DATA --calib DATA/CALIB --rerun processed_calexp_many -C $AP_PIPE_DIR/config/calexpTemplates.py -c ppdb.isolation_level=READ_UNCOMMITTED -c ppdb.db_url="sqlite:///ppdb_calexp_many/association.db" --id visit=411858 filter=g --templateId visit=410915 date=2015-02-17 &> ap_calexp_26-many.log &
```

This serial processing takes about 1.75 minutes per science CCD (where that 1.75 minutes includes calibrating both the reference and science CCDs, and also performing the differencing). The above command's processing can also be parallelized using the `-j` command line argument for `ap_pipe.py`.

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

It is more generally useful to learn how to make reference catalogs from scratch oneself rather than copying/renaming a bunch of pre-provided files. This section explains how to generate a set of "sharded" HTM reference catalogs starting from a catalog covering the relevant sky region but in another (non-LSST) format. The instructions here are largely based on:

https://community.lsst.org/t/creating-and-using-new-style-reference-catalogs/1523

First you will need to (somehow) obtain a catalog of suitable astrometric/photometric reference stars covering the sky region of interest. In this example we will use the following file:

https://portal.nersc.gov/project/cosmo/temp/ameisner/ps1_HITS.csv.gz

Which is 169 MB (509 MB) compressed (uncompressed), and contains information about Pan-STARRS stars covering all of the relevant HITS data in the ap_verify_hits2015 example.

Let's make and go to a directory called $REF within which we'll build the sharded reference catalog. Download and uncompress the ps1_HITS.csv.gz catalog file so that there's a file called $REF/ps1_HITS.csv. Make a directory called $REF/my_ref_repo. This directory will be a Butler repository used for making the sharded reference catalogs. This repository needs a \_mapper file. This can be either of:

```echo "lsst.obs.test.TestMapper" > my_ref_repo/_mapper```

or

```echo "lsst.obs.decam.DecamMapper" > my_ref_repo/_mapper```

Now make a file called $REF/my_ref.cfg, which looks like:

```
# String to pass to the butler to retrieve persisted files.
config.dataset_config.ref_dataset_name='my_ps1_catalog'

# Name of RA column
config.ra_name='coord_ra'

# Name of Dec column
config.dec_name='coord_dec'

# Name of column to use as an identifier (optional).
config.id_name='id'

# The values in the reference catalog are assumed to be in AB magnitudes. List of column names to use for
# photometric information.  At least one entry is required.
config.mag_column_list=['g', 'r', 'i', 'z', 'y']

# A map of magnitude column name (key) to magnitude error column (value).
config.mag_err_column_map={'g':'g_err', 'r':'r_err', 'i':'i_err', 'z':'z_err', 'y':'y_err'}
```

The name `my_ps1_catalog` is arbitrary. The various column names provided need to match the column names in your CSV file. The RA and Dec values in the CSV file need to be in decimal degrees (they get converted to radians for the sharded HTM files). Now you can make the set of sharded reference catalogs by running:

```
ingestReferenceCatalog.py my_ref_repo/ ps1_HITS.csv --configfile my_ref.cfg
```

The sharded reference catalogs and the associated `config.py` and `master_schema.fits` files are written to `my_ref_repo/ref_cats/my_ps1_catalog`. If the input catalog were split across multiple CSV files, say `ps1_HITS-part[0-9]`, it would work to specify `ps1_HITS-part?.csv` instead of `ps1_HITS.csv` in the above `ingestReferenceCatalog.py` command.

Note that `ingestReferenceCatalog.py` accepts the `-j` argument for multiprocessing (and includes this argument in the `ingestReferenceCatalog.py -h` help), but multiprocessing won't actually happen. From the log file when using `-j 8`:

```
root WARN: This task does not support multiprocessing; using one process
```

This warning is issued both when ingesting FITS and CSV input catalog files. Multiprocessing during ingestion can be achieved by using the `config.n_processes` parameter for `ingestReferenceCatalog.py`. This can be added to the `ingestReferenceCatalog.py` configuration file as, for instance:

```
config.n_processes = 8
```

Note that the `config.n_processes` argument has no effect unless you are ingesting a set of multiple input catalogs (as opposed to one large input file).

Now we will use these reference catalogs to run DECam CCD calibration. Return to the `$DATA` directory, and make a symlink called `DATA/ref_cats/my_ps1_catalog` that points to `$REF/my_ref_repo/ref_cats/my_ps1_catalog`.

Now we need a configuration override file to make the calibration pipeline actually use our `my_ps1_catalog` reference catalogs. In this case we name this file `processCcd-overrides-my_ps1.py`, and its contents are:

```
from lsst.meas.algorithms import LoadIndexedReferenceObjectsTask
config.calibrate.photoRefObjLoader.retarget(LoadIndexedReferenceObjectsTask)
config.calibrate.photoRefObjLoader.ref_dataset_name = "my_ps1_catalog"
config.calibrate.astromRefObjLoader.retarget(LoadIndexedReferenceObjectsTask)
config.calibrate.astromRefObjLoader.ref_dataset_name = "my_ps1_catalog"

config.calibrate.photoCal.photoCatName='my_ps1_catalog'
config.calibrate.connections.astromRefCat='my_ps1_catalog'
config.calibrate.connections.photoRefCat='my_ps1_catalog'
```

Note that the first five lines are included in the aforementioned forum post, but the last three lines are not.

Now we can run `processCcd.py` using the `my_ps1_catalog` reference catalogs for both astrometric and photometric calibration:

```
processCcd.py DATA --calib DATA/CALIB --rerun processCcdOutputs_my_ps1 --id visit=412321 ccdnum=42 filter=g --longlog --configfile processCcd-overrides-my_ps1.py &> processCcd-my_ps1.log
```

### appendix C: making reference catalogs from FITS input

FITS files are in some ways preferable to ASCII. Suppose your starting point is a FITS file called `ps1_HITS.fits` rather than `ps1_HITS.csv`. `ps1_HITS.fits` should contain the catalog in a binary table in extension=1 and have the same column names as did `ps1_HITS.csv`:

```
hdul.info()
Filename: ps1_HITS.fits
No.    Name      Ver    Type      Cards   Dimensions   Format
  0  PRIMARY       1 PrimaryHDU       4   ()      
  1                1 BinTableHDU     56   2293913R x 22C   [K, D, D, K, D, D, D, D, D, D, D, D, D, D, D, D, K, D, D, D, D, K] 
```

Here is the relevant configuration file (`my_ref_fits.cfg`) for ingestReferenceCatalog.py to read FITS input:

```
from lsst.meas.algorithms.readFitsCatalogTask import ReadFitsCatalogTask

# String to pass to the butler to retrieve persisted files.
config.dataset_config.ref_dataset_name='my_ps1_catalog'

config.file_reader.retarget(ReadFitsCatalogTask)

# Name of RA column
config.ra_name='coord_ra'

# Name of Dec column
config.dec_name='coord_dec'

# Name of column to use as an identifier (optional).
config.id_name='id'

# The values in the reference catalog are assumed to be in AB magnitudes. List of column names to use for
# photometric information.  At least one entry is required.
config.mag_column_list=['g', 'r', 'i', 'z', 'y']

# A map of magnitude column name (key) to magnitude error column (value).
config.mag_err_column_map={'g':'g_err', 'r':'r_err', 'i':'i_err', 'z':'z_err', 'y':'y_err'}
```

Regarding the setting of `config.file_reader`, it is important that this be done with `config.file_reader.retarget(ReadFitsCatalogTask)`; `config.file_reader=ReadFitsCatalogTask` does not work. This would then be run with:

```
ingestReferenceCatalog.py my_ref_repo/ ps1_HITS.fits --configfile my_ref_fits.cfg &> ingestReferenceCatalog-fits.log &
```

Building the reference catalogs from FITS files also works starting with multiple FITS files, for instance if `ps1_HITS.fits` were split between `ps1_HITS-part1.fits` and `ps1_HITS-part2.fits`, then replacing `ps1_HITS.fits` with `ps1_HITS-part?.fits` in the above `ingestReferenceCatalog.py` command would work.

### appendix D: making NSC DR2 reference catalogs

Say that you've obtained an ASCII version of some portion of the NSC DR2 "object" table from Data Lab, in a file named `result.txt`. This can be ingested into LSST-style sharded HTM reference catalog format using the following configuration file `my_ref.cfg`:

```
# String to pass to the butler to retrieve persisted files.
config.dataset_config.ref_dataset_name='nsc_dr2_object'

# Name of RA column
config.ra_name='ra'

# Name of Dec column
config.dec_name='dec'

# Name of column to use as an identifier (optional).
config.id_name='id'

# The values in the reference catalog are assumed to be in AB magnitudes. List of column names to use for
# photometric information.  At least one entry is required.
config.mag_column_list=['gmag', 'rmag', 'imag', 'zmag', 'ymag']

# A map of magnitude column name (key) to magnitude error column (value).
config.mag_err_column_map={'gmag':'gerr', 'rmag':'rerr', 'imag':'ierr', 'zmag':'zerr', 'ymag':'yerr'}
```

Then, assuming you've set up your repository as before in Appendix B, you can run:

```
ingestReferenceCatalog.py my_ref_repo/ result.txt --configfile my_ref.cfg
```

This will produce output HTM shard catalog files at `my_ref_repo/ref_cats/nsc_dr2_object`.

### appendix E: making DECaPS DR1 reference catalogs

Say that you've obtained an ASCII version of some portion of the DECaPS DR1 "object" table from Data Lab, in a file named `result.txt`. This can be ingested into LSST-style sharded HTM reference catalog format using the following configuration file `my_ref.cfg`:

```
# String to pass to the butler to retrieve persisted files.
config.dataset_config.ref_dataset_name='decaps_dr1_object'

# Name of RA column
config.ra_name='ra'

# Name of Dec column
config.dec_name='dec'

# Name of column to use as an identifier (optional).
config.id_name='_id'

# The values in the reference catalog are assumed to be in AB magnitudes. List of column names to use for
# photometric information.  At least one entry is required.
config.mag_column_list=['mean_mag_g', 'mean_mag_r', 'mean_mag_i', 'mean_mag_z', 'mean_mag_y']
```

Then, assuming you've set up your repository as before in Appendix B, you can run:

```
ingestReferenceCatalog.py my_ref_repo/ result.txt --configfile my_ref.cfg
```

This will produce output HTM shard catalog files at `my_ref_repo/ref_cats/decaps_dr1_object`.

### appendix F: reducing other DECam data

Let's say that you would like to reduce some other DECam science data (not from the example HITS 2015 data set) using the LSST pipeline. For g band, you can run `processCcd.py` using the same calibration files curated for the example HITS data set. To do this, you can set up a new repository:

```
mkdir DATA
mkdir DATA/CALIB

echo lsst.obs.decam.DecamMapper > DATA/_mapper
```

Then ingest the raw DECam science images from a staging directory called `raw/`:

```
ingestImagesDecam.py DATA --filetype raw raw/*.fz --mode=link
```

There are multiple ways of populating the `raw/` directory. I used an Astro Data Archive SIA query to construct `wget` download commands:

```
wget https://astroarchive.noirlab.edu/api/retrieve/0eae8b74999ebeb2bf8d3c41611cca50/ -O 'raw/DECam_00769126.fits.fz'
wget https://astroarchive.noirlab.edu/api/retrieve/1b97b87a65db6c8dac10c953105c7e7e/ -O 'raw/DECam_00660930.fits.fz'
```

Load the calibrations very similarly to what was done for the HITS 2015 example data set:

```
mkdir flats_biases
rsync -arv $DATA/ap_verify_hits2015/preloaded/DECam/calib/*/cpBias/cpBias*.fits flats_biases
rsync -arv $DATA/ap_verify_hits2015/preloaded/DECam/calib/*/cpFlat/g/*/cpFlat*.fits flats_biases

ingestCalibs.py DATA --calib DATA/CALIB flats_biases/*.fits --validity 999 --mode=link -C configSupersede.py

ingestDefects.py DATA $INSTALL_DIR/stack/miniconda3-4.7.10-4d7b902/Linux64/obs_decam_data/19.0.0/decam/defects --calib DATA/CALIB
```


In the `ingestCalibs.py` call, the configuration has been changed slightly in order to use the HITS 2015 calibrations for other DECam data, which may fall outside of the `validStart` to `validEnd`date range of the HITS 2015 calibrations. This is accomplished with a configuration file called `configSupersede.py`:

```
Tables for which to set validity for a calib from when it is taken until it is superseded by the next; validity in other tables is calculated by applying the validity range.
config.register.validityUntilSuperseded=['defects', 'bias', 'flat', 'fringe', 'dark', 'illumcor']
```

The idea is to make the pipeline ignore the `validStart`/`validEnd` constraint on e.g., the available master biases/flats. You'll also need to put suitable reference catalogs in place covering your chosen sky location. Then, if your reference catalogs are at `DATA/ref_cats/ps1_pv3_3pi_20170110`, you can perform the data reduction as follows:

```
processCcd.py DATA --calib DATA/CALIB --rerun processCcdOutputs --id --longlog
```

If you don't use the custom `validityUntilSuperseded` configuration mentioned above, then you will end up with errors like:

```
RuntimeError: Unable to retrieve cpBias for {'date': '2018-09-05', 'filter': 'g', 'visit': 769126, 'hdu': 1, 'ccdnum': 25, 'object': 'DECaLS_57359_g'}: No locations for get: datasetType:cpBias dataId:DataId(initialdata={'date': '2018-09-05', 'filter': 'g', 'visit': 769126, 'hdu': 1, 'ccdnum': 25, 'object': 'DECaLS_57359_g'}, tag=set()).
```

### appendix G: DECam VR data

In order to calibrate DECam VR data with `processCcd.py`, one needs to specify which filter to use from within the reference catalog. This can be accomplished by creating a custom configuration Python file with VR added to the following dictionaries:

```
config.charImage.refObjLoader.filterMap={'u': 'g', 'Y': 'y', 'VR': 'r'}
config.calibrate.astromRefObjLoader.filterMap={'u': 'g', 'Y': 'y', 'VR': 'r'}
config.calibrate.photoRefObjLoader.filterMap={'u': 'g', 'Y': 'y', 'VR': 'r'}
```

In the above case, VR is being mapped to r-band. It is also possible to instead map VR to g-band:

```
config.charImage.refObjLoader.filterMap={'u': 'g', 'Y': 'y', 'VR': 'g'}
config.calibrate.astromRefObjLoader.filterMap={'u': 'g', 'Y': 'y', 'VR': 'g'}
config.calibrate.photoRefObjLoader.filterMap={'u': 'g', 'Y': 'y', 'VR': 'g'}
```

If these configuration options are specified in a file called `config-filtermap.py`, then they can be employed by `processedCcd.py` using:

```
processCcd.py DATA --calib DATA/CALIB --rerun processCcdOutputs --id --longlog -C config-filtermap.py -j 20
```

### appendix H: DECam u band in COSMOS

Download the following raw DECam u-band exposure in/near the COSMOS region:

```
wget https://astroarchive.noirlab.edu/api/retrieve/297af0ee3aa4c643244de084df3345ab/ -O 'raw/DECam_00177741.fits.fz'
```

This exposure was identified via an Astro Data Archive SIA voimage API cone search centered on (RA, Dec) ~ (150.1, 2.2):

```
import requests
import pandas as pd

url_u = 'https://astroarchive.noirlab.edu/api/sia/voimg?POS=150.11916667,2.20583333&SIZE=2&VERB=2&limit=10000&instrument=decam&proctype=raw&format=json'
df_u = pd.DataFrame(requests.get(url_u).json()[1:])
```

And making some subsequent cuts on the resulting DataFrame. DECam_00177741.fits.fz has `DTCALDAT` = 2013-02-12. To identify the corresponding u-band flat and bias for this date, begin by issuing a query to the `/short` Astro Data Archive API:

https://astroarchive.noirlab.edu/api/docs/#/short/short_read

The `/short` API provides a list of all files for a specific (telescope, instrument, night). To identify relevant calibrations for the u-band DECam science exposure, we can start by doing:

```
url_short = 'https://astroarchive.noirlab.edu/api/short/ct4m/decam/2013-02-12/'
nightsum_u = pd.DataFrame(requests.get(url_short).json()[1:])
```

The master flat for this night can then be identified by trimming the night summary data frame, requiring `proc_type` = 'mastercal', `prod_type` = 'image', `ifilter` = 'u DECam c0006 3500.0 1000.0', and `obs_type` = 'dome flat'. Using `archive_filename` and `url` from the the relevant row of the night summary data frame, we can then construct a `wget` command to download the u-band master flat:

```
wget https://astroarchive.noirlab.edu/api/retrieve/85b0f0932156012e3215df9160b58c6d/ -O 'flats_biases/tu1926715.fits.fz'
```

The master bias for 2013-02-12 can be identified by trimming the night summary data frame with cuts requiring `obs_type` = 'zero', `prod_type` = 'image', and `proc_type` = 'mastercal'. Using `archive_filename` and `url` from the the relevant row of the night summary data frame, we can then construct a `wget` command to download the master bias:

```
wget https://astroarchive.noirlab.edu/api/retrieve/68d33ad5f5ee90a59219cfa26f3496f4/ -O 'flats_biases/tu1931853.fits.fz'
```

We can then ingest the flat/bias, defects and raw data as usual. Since this sky location is at Dec > -30 deg and the LSST pipeline by default uses g-band as the reference filter to calibrate u-band, we can populate `DATA/ref_cats` with the standard `ps1_pv3_3pi_20170110` PS1 shard files covering the relevant sky area. Then we can run the vanilla `processCcd.py` command:

```
processCcd.py DATA --calib DATA/CALIB --rerun processCcdOutputs --id --longlog -j 20
```

The default filter mapping being used here is:

```
$ processCcd.py DATA --calib DATA/CALIB --rerun processCcdOutputs --id --longlog -j 20 --show config |grep -i filtermap
config.charImage.refObjLoader.filterMap={'u': 'g', 'Y': 'y'}
config.calibrate.astromRefObjLoader.filterMap={'u': 'g', 'Y': 'y'}
config.calibrate.photoRefObjLoader.filterMap={'u': 'g', 'Y': 'y'}
```

It would perhaps be more satisfying to calibrate the u-band exposure with u-band reference catalog data, but PS1 does not offer u-band. To calibrate with a u-band reference catalog, we use NSC DR2. To accomplish this, we start by issuing an NSC cone query to the NOIRLab Astro Data Lab using the `dl` Data Lab Python module:

```
from dl import queryClient as qc

res = qc.query(sql='select * from nsc_dr2.object where q3c_radial_query(object.ra,object.dec,150.1101875,2.23218611,1.3) and ((object.umag < 22) or (object.rmag < 21))', fmt='table')

for band in ['u', 'g', 'r', 'i', 'z', 'y']:
    res.rename_column(band + 'mag', band)

res.write('cosmos_u_refcat-renamed.csv', format='csv')
```

I found the renaming of the bands to simply 'u', 'g', ... rather than 'umag', 'gmag', ... to be necessary in order for `processCcd.py` to successfully access the correct reference catalog photometry columns during calibration (possibly there are configuration parameter changes that could be applied to make this renaming unnecessary; the renaming could also be done directly in the SQL query). You can then ingest this reference catalog with:

```
ingestReferenceCatalog.py my_ref_repo-renamed/ cosmos_u_refcat-renamed.csv --configfile my_ref-renamed.cfg
```

Where `my_ref-renamed.cfg` contains:

```
# String to pass to the butler to retrieve persisted files.
config.dataset_config.ref_dataset_name='nsc_dr2_object_rename'

# Name of RA column
config.ra_name='ra'

# Name of Dec column
config.dec_name='dec'

# Name of column to use as an identifier (optional).
config.id_name='id'

# The values in the reference catalog are assumed to be in AB magnitudes. List of column names to use for
# photometric information.  At least one entry is required.
config.mag_column_list=['u', 'g', 'r', 'i', 'z', 'y']

# A map of magnitude column name (key) to magnitude error column (value).
config.mag_err_column_map={'u':'uerr', 'g':'gerr', 'r':'rerr', 'i':'ierr', 'z':'zerr', 'y':'yerr'}
```

Now we can run calibration using NSC DR2 u-band as the reference data set:

```
processCcd.py DATA --calib DATA/CALIB --rerun processCcdOutputs --id --longlog --configfile processCcd-overrides-nsc_dr2_renamed-filtermap.py -j 20
```

Where `processCcd-overrides-nsc_dr2_renamed-filtermap.py` contains:

```
from lsst.meas.algorithms import LoadIndexedReferenceObjectsTask
config.calibrate.photoRefObjLoader.retarget(LoadIndexedReferenceObjectsTask)
config.calibrate.photoRefObjLoader.ref_dataset_name = "nsc_dr2_object_rename"
config.calibrate.astromRefObjLoader.retarget(LoadIndexedReferenceObjectsTask)
config.calibrate.astromRefObjLoader.ref_dataset_name = "nsc_dr2_object_rename"

config.calibrate.photoCal.photoCatName='nsc_dr2_object_rename'
config.calibrate.connections.astromRefCat='nsc_dr2_object_rename'
config.calibrate.connections.photoRefCat='nsc_dr2_object_rename'

config.charImage.refObjLoader.filterMap={'u': 'u', 'Y': 'y'}
config.calibrate.astromRefObjLoader.filterMap={'u': 'u', 'Y': 'y'}
config.calibrate.photoRefObjLoader.filterMap={'u': 'u', 'Y': 'y'}
```

This configuration file both points to the ingested NSC DR2 reference catalog based on its `ref_dataset_name` and also maps `'u' : 'u'` in the `filterMap`. Possibly it might be better to do something like using u-band for the photometric calibration while using e.g., r-band for the astrometry.

### appendix I: DECaLS r-band reduction example

An example raw DECam r-band image from DECaLS can be downloaded as:

```
wget https://astroarchive.noirlab.edu/api/retrieve/6ccecc118687b836b0fac3ffc5e768fb/ -O 'raw/DECam_00661619.fits.fz'
```

