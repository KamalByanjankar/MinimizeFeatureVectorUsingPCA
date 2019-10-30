import sys
import os
from os.path import basename
from glob import glob

from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5.uic import loadUi

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QWidget, QApplication, QSizePolicy
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QTableView, QVBoxLayout, QHeaderView

import pandas as pd
import numpy as np
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from numpy.fft import fft, fftfreq, ifft

class PlotCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        #self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        FigureCanvas.setSizePolicy(self,
                QSizePolicy.Expanding,
                QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)


    def plot(self, data_list):        
        for index, data in enumerate(data_list):
            ax = self.figure.add_subplot(7,7,index+1)
            ax.plot(data)
            self.draw()


class Widget(QWidget):
    def __init__(self):
        print("Hello!! Welcome to the FFT")
        
        super().__init__()
        uifile = os.path.join(os.path.dirname(__file__), 'FFT_implementation.ui')
        self.ui = loadUi(uifile, self)
        
        self.m = PlotCanvas(self, width=7, height=10)
        self.m.move(460,0)
        
        self.n = PlotCanvas(self, width=7, height=10)
        self.n.move(1180,0)
        
        self.files=[]
        
        for elem in self.ui.children():
            name = elem.objectName()
            
            if name == 'echo_frame':
               for child_elem in elem.children():
                    child_name = child_elem.objectName()
                    
                    if child_name == 'browse_echo_file':
                        child_elem.clicked.connect(self.load_echo_file)
                    elif child_name == 'table_widget':
                        self.table = child_elem
                    elif child_name =='apply_fft':
                        child_elem.clicked.connect(self.fftOperation)
                        
        
    def load_echo_file(self):
        files = []
        self.directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        paths = glob(f'{self.directory}/*')
        self.browse_file_input.setText(self.directory)
        #print(len(paths))
        if len(paths) > 0:
            for p in paths:
                files += glob(f'{p}/*.csv')
            if not files:
                files = paths
            #for i in range(4):
            #    self.files.append(paths[i])
            for i in range(len(paths)):
                self.files.append(paths[i])
        self.load_files_in_table(files)
        
    def load_files_in_table(self, files):
        self.table.setRowCount(len(files))
        for row, item in enumerate(files):
            filename = item.split('/')[-1]
            if filename.split('\\')[0]:
                filename =  filename.split('\\')[0]
            self.table.setItem(row, 0, QTableWidgetItem(filename))
            self.table.setItem(row, 1, QTableWidgetItem(basename(item)))
            
    def fftOperation(self):
        print("FFT Operation")
        fft_set = []
        for file in self.files:
            #print(file)
            data = pd.read_csv(file)
            fft_data = self.fft_from_data_frame(data)
            fft_set = fft_data + fft_set
        data = pd.DataFrame(fft_set)
       # self.fft_filename.setText('_fft.csv')
        filename = self.fft_filename.text()
        data.to_csv(self.directory +filename, header=False, index=False)
        print(data.shape)
        self.files=[]
            
    def fft_from_data_frame(self, data_frame):
        fs= 114e3
        signal_set = []
        for row in data_frame.values:
            fft_data = fft(row, n=row.size)/row.size
            freq = fftfreq(row.size, d=1/fs)
            cut_high_signal = abs(fft_data).copy()
            cut_high_signal[(freq > 50000)] = 0
            cut_high_signal[(freq < 30000)] = 0
            signal_without_0 = list(filter(lambda a: a != 0, cut_high_signal))
            signal_set.append(np.abs(signal_without_0))
        return signal_set
        
if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())
