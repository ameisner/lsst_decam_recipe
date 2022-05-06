import lsst.daf.persistence as dafPersist
import matplotlib.pyplot as plt
import numpy as np

butler = dafPersist.Butler(inputs='DATA/rerun/processCcdOutputs')

format = ('visit', 'ccdnum', 'filter')

dataId_tuples = butler.queryMetadata('calexp', format, ccdnum=10)

dataIds = [{format[0] : t[0], format[1]: t[1], format[2]: t[2]} for t in dataId_tuples]

for i, dataId in enumerate(dataIds):
    print(i+1, ' of ', len(dataIds))
    calexp = butler.get('calexp', dataId)

    psf = calexp.getPsf()

    rendering = psf.computeImage()

    arr = rendering.array

    print('PSF model sums to : ', np.sum(arr))

    plt.imshow(arr, origin='lower', interpolation='nearest') #, cmap='gray')

    plt.xticks([])
    plt.yticks([])
    title = 'EXPNUM = ' + str(dataId['visit']) + ' ; ' + \
            'CCDNUM = ' + str(dataId['ccdnum']) + ' ; night = 2018-09-05'

    plt.title(title)

    outname = str(dataId['visit']) + '.png'

    plt.savefig(outname)
    plt.cla()
