import lsst.daf.persistence as dafPersist
import matplotlib.pyplot as plt

butler = dafPersist.Butler(inputs='DATA/rerun/processCcdOutputs')

dataId = {'filter': 'g', 'visit': 769479, 'ccdnum': 10}
calexp = butler.get('calexp', dataId)

psf = calexp.getPsf()

rendering = psf.computeImage()

arr = rendering.array

plt.imshow(arr, origin='lower', interpolation='nearest', cmap='gray')

plt.show()
