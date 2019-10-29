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
        print("Hello!! Welcome to the User Interface")
        
        super().__init__()
        uifile = os.path.join(os.path.dirname(__file__), 'Data_Analysis.ui')
        self.ui = loadUi(uifile, self)
        
        self.m = PlotCanvas(self, width=7, height=10)
        self.m.move(460,0)
        
        self.n = PlotCanvas(self, width=7, height=10)
        self.n.move(1180,0) 
        
        self.files=[]
        self.required_data_without_offset=[]
        self.required_echo_list = []
        
        for elem in self.ui.children():
            name = elem.objectName()
                
            if name == 'echo_frame':
                for child_elem in elem.children():
                    child_name = child_elem.objectName()
                    
                    if child_name == 'browse_file':
                        child_elem.clicked.connect(self.load_file)
                    elif child_name == 'table_widget':
                        self.table = child_elem
                    elif child_name == 'browse_file_input':
                        self.browse_file_input = child_elem
                    elif child_name == 'show_plot_btn':
                        child_elem.clicked.connect(self.plot_graph)
                    elif child_name == 'show_echo_btn':
                        child_elem.clicked.connect(self.plot_echo)
                    elif child_name == 'save_echo_btn': 
                        child_elem.clicked.connect(self.save_echo)
                        
    
    def load_file(self):
        files = []
        self.directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        paths = glob(f'{self.directory}/*')
        self.browse_file_input.setText(self.directory)
        #self.text_echo_filename.setText(self.directory)
        if len(paths) > 0:
            for p in paths:
                files += glob(f'{p}/*.csv')
            if not files:
                files = paths
            #for i in range(4):
            #    self.files.append(paths[i])
            self.files.append(paths[0])
        self.load_files_in_table(files)

        
    def load_files_in_table(self, files):
        self.table.setRowCount(len(files))
        for row, item in enumerate(files):
            filename = item.split('/')[-1]
            if filename.split('\\')[0]:
                filename =  filename.split('\\')[0]
            self.table.setItem(row, 0, QTableWidgetItem(filename))
            self.table.setItem(row, 1, QTableWidgetItem(basename(item)))
        
    def plot_graph(self):
        for file in self.files:
            print(file)
            df = pd.read_csv(file, skiprows=[0], header=None)
            required_data = df.iloc[:, 9:]
            data_without_offset = required_data.sub(required_data.mean(axis=1), axis=0).values
            print(data_without_offset.shape)
            #self.m.plot(data_without_offset)
            self.required_data_without_offset.append(data_without_offset)
            self.files = []
            
    def plot_echo(self):
        for i, data in enumerate(self.required_data_without_offset):
            required_echos = self.get_echos(data)
            print(np.array(required_echos).shape)
            #self.n.plot(required_echos)
            self.required_echo_list.append(required_echos)
            self.required_data_without_offset = []
            
    def get_echos(self, filtered_values):
        NOISE_SIZE = 250
        ECHO_SIZE = 512
        all_echo_range = [] 
        for index, data in enumerate(filtered_values):
            chopped_data = data[NOISE_SIZE:]
            max_point_distance = self.peak_value(chopped_data)
            if max_point_distance:
                cutting_distance = max_point_distance - 250
                if cutting_distance > 0:
                    echo_range = chopped_data[cutting_distance:]
                    echo_range = echo_range[:ECHO_SIZE]
                    all_echo_range.append(echo_range)
        return all_echo_range
    
    def peak_value(self, data):
        THRESHOLD = 0.15
        max_point_distance = 0
        peakData = 0
        max_point_distance = np.array(data).argmax()
        peakData = np.array(data).max()
        if peakData > THRESHOLD:
            return max_point_distance
        else: 
            return None
        
        
    def save_echo(self):
        echo_set = []
        for i, data in enumerate(self.required_echo_list):
            echo_set = echo_set + data
        data = pd.DataFrame(echo_set)
        filename = self.text_echo_filename.text()
        data.to_csv(self.directory +filename, header=False, index=False)
        print(data.shape)
        self.required_echo_list = []

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())