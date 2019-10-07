import sys
import os
from os.path import basename
from glob import glob
import pickle

from PyQt5.QtGui import *
from PyQt5 import QtCore
from PyQt5.uic import loadUi

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QFileDialog, QWidget, QApplication, QSizePolicy
from PyQt5.QtWidgets import QTableWidget, QTableWidgetItem, QTableView, QVBoxLayout, QHeaderView

class Widget(QWidget):
    def __init__(self):
        print("Hello!! Welcome to the User Interface")
        
        super().__init__()
        uifile = os.path.join(os.path.dirname(__file__), 'Individual_Project.ui')
        self.ui = loadUi(uifile, self)
        
        
        for elem in self.ui.children():
            name = elem.objectName()
            if name == 'radio_choose_echo':
                elem.clicked.connect(self.select_echo)
            
            if name =='radio_choose_ML':
                elem.clicked.connect(self.select_ML)
                
            if name == 'echo_frame':
                for child_elem in elem.children():
                    child_name = child_elem.objectName()
                    
                    if child_name == 'browse_file':
                        child_elem.clicked.connect(self.load_file)
                    elif child_name == 'table_widget':
                        self.table = child_elem
                    elif child_name == 'browse_file_input':
                        self.browse_file_input = child_elem
                
    def select_echo(self):
        self.echo_frame.show()
        self.ML_frame.hide()
    
    def load_file(self):
        directory = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        paths = glob(f'{directory}/*')
        self.browse_file_input.setText(directory)
        files = []
        if len(paths) > 0:
            for p in paths:
                files += glob(f'{p}/*.csv')
            
            if not files:
                files = paths
        self.load_files_in_table(files)
        
    def load_files_in_table(self, files):
        self.table.setRowCount(len(files))
        for row, item in enumerate(files):
            filename = item.split('/')[-1]
            if filename.split('\\')[0]:
                filename =  filename.split('\\')[0]
            self.table.setItem(row, 0, QTableWidgetItem(filename))
            self.table.setItem(row, 1, QTableWidgetItem(basename(item)))

    def select_ML(self):
        self.echo_frame.hide()
        self.ML_frame.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = Widget()
    w.show()
    sys.exit(app.exec_())