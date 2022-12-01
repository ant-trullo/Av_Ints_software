"""This is the main window of the software segment spots time series.

This is version 1.0.
author: antonio.trullo@igmm.cnrs.fr
"""

import sys
from natsort import natsorted
import numpy as np
import pyqtgraph as pg
from PyQt5 import QtGui, QtWidgets

import LoadFiles
import SaveLists
import SpotsDetection


class MainWindow(QtWidgets.QMainWindow):
    """Main windows: coordinates all the actions, algorithms, visualization tools and analysis tools."""

    def __init__(self, parent=None):

        QtWidgets.QMainWindow.__init__(self, parent)

        widget  =  QtWidgets.QWidget(self)
        self.setCentralWidget(widget)

        load_data_action  =  QtWidgets.QAction(QtGui.QIcon('Icons/load-hi.png'), "&Load Data", self)
        load_data_action.triggered.connect(self.load_raw_data)
        load_data_action.setShortcut('Ctrl+L')

        load_mipdata_action  =  QtWidgets.QAction(QtGui.QIcon('Icons/load-hi.png'), "&Load MIP Data", self)
        load_mipdata_action.triggered.connect(self.load_mip_data)
        load_mipdata_action.setShortcut('Ctrl+M')

        save_analysis_action  =  QtWidgets.QAction(QtGui.QIcon('Icons/save-md.png'), "&Save Analysis", self)
        save_analysis_action.triggered.connect(self.save_analysis)
        save_analysis_action.setShortcut('Ctrl+S')

        exit_action  =  QtWidgets.QAction(QtGui.QIcon('Icons/exit.png'), "&Exit", self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip("Exit application")
        exit_action.triggered.connect(self.close)

        self.statusBar()

        menubar   =  self.menuBar()

        fileMenu  =  menubar.addMenu('&File')
        fileMenu.addAction(load_data_action)
        fileMenu.addAction(load_mipdata_action)
        fileMenu.addAction(save_analysis_action)
        fileMenu.addAction(exit_action)

        fname_edt = QtWidgets.QLineEdit(self)
        fname_edt.setToolTip('Name of the file you are working on')

        frame_raw  =  pg.ImageView(self, name="FrameRaw")
        frame_raw.ui.roiBtn.hide()
        frame_raw.ui.menuBtn.hide()
        frame_raw.timeLine.sigPositionChanged.connect(self.update_from_frame_raw)

        frame_sgm   =  pg.ImageView(self)
        frame_sgm.ui.roiBtn.hide()
        frame_sgm.ui.menuBtn.hide()
        frame_sgm.ui.histogram.hide()
        frame_sgm.view.setXLink("FrameRaw")
        frame_sgm.view.setYLink("FrameRaw")
        frame_sgm.timeLine.sigPositionChanged.connect(self.update_from_frame_sgm)

        frame_plot  =  pg.PlotWidget(self)

        tabs_tot  =  QtWidgets.QTabWidget()
        tab_raw   =  QtWidgets.QWidget()
        tab_sgm   =  QtWidgets.QWidget()

        frame_raw_box  =  QtWidgets.QHBoxLayout()
        frame_raw_box.addWidget(frame_raw)

        frame_sgm_box  =  QtWidgets.QHBoxLayout()
        frame_sgm_box.addWidget(frame_sgm)

        tab_raw.setLayout(frame_raw_box)
        tab_sgm.setLayout(frame_sgm_box)

        tabs_tot.addTab(tab_raw, "Raw")
        tabs_tot.addTab(tab_sgm, "Segm")

        layout_frames  =  QtWidgets.QVBoxLayout()
        layout_frames.addWidget(fname_edt)
        layout_frames.addWidget(tabs_tot)
        layout_frames.addWidget(frame_plot)

        thr_spts_lbl  =  QtWidgets.QLabel("Thr", self)
        thr_spts_lbl.setFixedSize(50, 25)

        frame_numb_lbl  =  QtWidgets.QLabel("Frame 0", self)
        frame_numb_lbl.setFixedSize(90, 25)

        thr_spts_edt  =  QtWidgets.QLineEdit(self)
        thr_spts_edt.textChanged[str].connect(self.thr_spts_var)
        thr_spts_edt.setFixedSize(40, 25)

        thr_vol_lbl  =  QtWidgets.QLabel("Vol", self)
        thr_vol_lbl.setFixedSize(50, 25)

        thr_vol_edt  =  QtWidgets.QLineEdit(self)
        thr_vol_edt.textChanged[str].connect(self.thr_vol_var)
        thr_vol_edt.setToolTip("Minimum spot volume")
        thr_vol_edt.setFixedSize(40, 25)

        thr_vol_lbl_edt_box  =  QtWidgets.QHBoxLayout()
        thr_vol_lbl_edt_box.addWidget(thr_vol_lbl)
        thr_vol_lbl_edt_box.addWidget(thr_vol_edt)

        thr_spts_lbl_edt_box  =  QtWidgets.QHBoxLayout()
        thr_spts_lbl_edt_box.addWidget(thr_spts_lbl)
        thr_spts_lbl_edt_box.addWidget(thr_spts_edt)

        thr_spts_btn  =  QtWidgets.QPushButton("Detect", self)
        thr_spts_btn.clicked.connect(self.thr_spts)
        thr_spts_btn.setFixedSize(90, 25)

        command_keys  =  QtWidgets.QVBoxLayout()
        command_keys.addLayout(thr_spts_lbl_edt_box)
        command_keys.addLayout(thr_vol_lbl_edt_box)
        command_keys.addWidget(thr_spts_btn)
        command_keys.addStretch()
        command_keys.addWidget(frame_numb_lbl)

        layout  =  QtWidgets.QHBoxLayout(widget)
        layout.addLayout(layout_frames)
        layout.addLayout(command_keys)

        self.setGeometry(100, 100, 1200, 800)
        self.show()

        self.frame_raw       =  frame_raw
        self.frame_sgm       =  frame_sgm
        self.frame_plot      =  frame_plot
        self.frame_numb_lbl  =  frame_numb_lbl
        self.fname_edt       =  fname_edt

    def closeEvent(self, event):
        """Close the GUI, asking confirmation."""
        quit_msg  =  "Are you sure you want to exit the program?"
        reply     =  QtWidgets.QMessageBox.question(self, 'Message', quit_msg, QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def load_raw_data(self):
        """Load and show avic raw data."""
        self.fnames    =  QtWidgets.QFileDialog.getOpenFileNames(None, "Select czi (or lsm) data files to concatenate...", filter="*.lsm *.czi *.tif *.lif")[0]
        self.fnames    =  natsorted(self.fnames)
        self.raw_data  =  LoadFiles.LoadFilesCzi5D(self.fnames)
        self.frame_raw.setImage(self.raw_data.img_mip)

        joined_fnames = ' '
        for s in range(len(self.fnames)):
            joined_fnames += str(self.fnames[s][self.fnames[s].rfind('/') + 1:]) + ' ----- '

        self.fname_edt.setText(joined_fnames)

    def load_mip_data(self):
        """Load mip tif data."""
        self.fnames    =  QtWidgets.QFileDialog.getOpenFileNames(None, "Select czi (or lsm) data files to concatenate...", filter="*.lsm *.czi *.tif *.lif")[0]
        self.raw_data  =  LoadFiles.LoadMipData(self.fnames)
        self.frame_raw.setImage(self.raw_data.img_mip)
        self.fname_edt.setText(self.fnames[0][self.fnames[0].rfind('/') + 1:])

    def update_from_frame_raw(self):
        """Update frames from raw frame index changes."""
        self.frame_numb_lbl.setText("Frame " + str(self.frame_raw.currentIndex))
        try:
            self.frame_sgm.setCurrentIndex(self.frame_raw.currentIndex)
        except Exception:
            pass

    def update_from_frame_sgm(self):
        """Update frames from sgm frame index changes."""
        self.frame_raw.setCurrentIndex(self.frame_sgm.currentIndex)

    def thr_spts_var(self, text):
        """Set detection threshold."""
        self.thr_spts_value  =  float(text)

    def thr_vol_var(self, text):
        """Set volume threshold."""
        self.thr_vol_value  =  int(text)

    def thr_spts(self):
        """Perform spots detection."""
        cif               =  self.frame_sgm.currentIndex
        self.spts_detect  =  SpotsDetection.SpotsDetection(self.raw_data.img_mip, self.thr_spts_value, self.thr_vol_value)
        self.frame_sgm.setImage(self.spts_detect.spots_mask, autoRange=False)
        self.frame_sgm.setCurrentIndex(cif)
        self.av_int  =  np.sum(self.spts_detect.spots_mask * self.raw_data.img_mip, axis=(1, 2)) / np.sum(self.spts_detect.spots_mask, axis=(1, 2))
        self.frame_plot.clear()
        self.frame_plot.plot(np.arange(self.av_int.size), self.av_int, symbol='x')

        pg.plot(self.spts_detect.bckg_vals, symbol='x', pen='r', title="BackGround")
        pg.plot(self.av_int / self.spts_detect.bckg_vals, symbol='x', pen='r', title="Av / BackGround")

    def save_analysis(self):
        """Save the results of the analysis."""
        xlsx_fname  =  QtWidgets.QFileDialog.getSaveFileName(self, "Define a xlsx file to write resullts")[0]
        SaveLists.SaveLists(xlsx_fname, self.av_int, self.spts_detect.bckg_vals)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == "__main__":

    sys.excepthook  =  except_hook

    app     =  QtWidgets.QApplication(sys.argv)
    window  =  MainWindow()
    window.show()
    sys.exit(app.exec_())
