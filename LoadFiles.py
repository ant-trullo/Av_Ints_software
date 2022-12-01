"""This function loads .lsm files.

Given the filename of a .lsm file, this function gives as output the matrices
of the red and green channels maximum intensity projected plus the green channel
as it is. Inputs are the file-name and the channel number for nuclei and spots.
"""


import numpy as np
import czifile
import tifffile
# from PyQt5 import QtWidgets


class LoadFilesCzi5D:
    """Coordinates the action of the single file loader on several files."""
    def __init__(self, fnames):

        img_mip  =  None
        mt_buff  =  None
        if len(fnames) == 1:                                                               # it can be zero when used in multiprocessing
            if fnames[0][-4:] == ".czi":                                                   # check the file type
                mt_buff  =  LoadCzi5D(fnames[0])                                           # read first .czi file
            elif fnames[0][-4:] == ".tif":
                mt_buff  =  LoadTiff5D(fnames[0])                                          # read first .tif files
            img_mip  =  mt_buff.img_mip

        elif len(fnames) > 1:                                                              # in case of several files
            if fnames[0][-4:] == ".czi":
                mt_buff                   =  LoadCzi5D(fnames[0])                           # load the first file
                t_steps_done, xlen, ylen  =  mt_buff.img_mip.shape                          # mip shape
                img_mip                   =  mt_buff.img_mip.ravel()                        # mip matrix
                for fname in fnames[1:]:                                                    # go on with the other files
                    mt_buff       =   LoadCzi5D(fname)                                      # read
                    t_steps_done  +=  mt_buff.img_mip.shape[0]                              # update the number of time frames
                    img_mip       =   np.concatenate([img_mip, mt_buff.img_mip.ravel()])    # concatenate the mip matrix reshaped with 1xN

                img_mip  =  img_mip.reshape((t_steps_done, xlen, ylen))                     # reshape the final matrix

            elif fnames[0][-4:] == ".tif":                                                  # same as before, for tif files
                mt_buff                   =  LoadTiff5D(fnames[0])
                t_steps_done, xlen, ylen  =  mt_buff.img_mip.shape
                img_mip                   =  mt_buff.img_mip.ravel()
                for fname in fnames[1:]:
                    mt_buff       =   LoadTiff5D(fname)
                    t_steps_done  +=  mt_buff.img_mip.shape[0]
                    img_mip       =   np.concatenate([img_mip, mt_buff.img_mip.ravel()])

                img_mip  =  img_mip.reshape((t_steps_done, xlen, ylen))

        self.img_mip  =  img_mip


class LoadCzi5D:
    """Load a single czi file into numpy array."""
    def __init__(self, fname):

        file_array               =  np.squeeze(czifile.imread(fname))                       # read czi file
        steps, zlen, xlen, ylen  =  file_array.shape                                        # read shape
        img_mip                  =  np.zeros((steps, xlen, ylen))                           # initialize maximum intensity projected matrix
        for tt in range(steps):
            for xx in range(xlen):
                img_mip[tt, xx, :]  =  file_array[tt, :, xx, :].max(0)                      # maximum intensity projection

        self.img_mip     =  img_mip


class LoadMipData:
    """Load a mip single file."""
    def __init__(self, fname):

        self.img_mip  =  tifffile.imread(fname).astype(np.float32)


class LoadTiff5D:
    """Load a single tif file."""
    def __init__(self, fname):

        file_array               =  tifffile.imread(fname)                              # read tif file
        steps, zlen, xlen, ylen  =  file_array.shape                                    # read shape
        img_mip                  =  np.zeros((steps, xlen, ylen))                       # initialize maximum intensity projected matrix
        for tt in range(steps):
            for xx in range(xlen):
                img_mip[tt, xx, :]  =  file_array[tt, :, xx, :].max(0)                  # maximum intensity projection

        self.img_mip     =  img_mip
