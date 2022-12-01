"""This function detects transcriptional spots.

Given the matrix of the raw data (Maximum Intensity Projected),
it performs a simple blob detection.
"""


import numpy as np
from scipy import ndimage
from scipy.stats import norm
from skimage.measure import label
from skimage.morphology import remove_small_objects
from skimage.segmentation import expand_labels


class SpotsDetection:
    """Only class, does all the job."""
    def __init__(self, imarray_green, thr_sigma, thr_vol):

        steps       =  imarray_green[:, 0, 0].size
        spots_gf    =  ndimage.gaussian_filter(imarray_green, 1)     # pre-smoothing of the matrix
        spots_la    =  -ndimage.laplace(spots_gf)                    # laplacian filter
        spots_mask  =  np.zeros(imarray_green.shape)
        spots_lbls  =  np.zeros(imarray_green.shape, dtype=np.uint16)
        bckg_mask   =  np.zeros(spots_lbls.shape, dtype=np.uint8)

        for t in range(steps):
            (mu, sigma)          =  norm.fit(spots_la[t, :, :])                  # gaussian fitting of the histogram of the matrix
            spots_mask[t, :, :]  =  spots_la[t, :, :] > mu + thr_sigma * sigma   # the threshold is expressed in terms of the standard deviation of the fitting

        for t in range(steps):
            spots_lbls[t]  =  label(spots_mask[t]).astype(np.uint16)            # frame by frame label the spots
            spots_lbls[t]  =  remove_small_objects(spots_lbls[t], thr_vol)      # remove small spots with a user defined threshold
            bckg_mask[t]   =  (expand_labels(spots_lbls[t], distance=4) - expand_labels(spots_lbls[t], distance=2)) * imarray_green[t]    # define cages to background measure

        bckg_vals  =  np.sum(bckg_mask, axis=(1, 2)) / np.sum(np.sign(bckg_mask), axis=(1, 2))              # average background

        self.spots_mask  =  spots_mask * np.sign(spots_lbls)
        self.spots_lbls  =  spots_lbls
        self.bckg_vals   =  bckg_vals
