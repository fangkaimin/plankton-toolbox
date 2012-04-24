#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Project: Plankton Toolbox. http://plankton-toolbox.org
# Author: Arnold Andreasson, info@mellifica.se
# Copyright (c) 2010-2011 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License as follows:
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import os.path
import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
import plankton_toolbox.activities.activity_base as activity_base
import plankton_toolbox.toolbox.utils_qt as utils_qt
import plankton_toolbox.activities.analyse_datasets_tab1 as tab1
import plankton_toolbox.activities.analyse_datasets_tab2 as tab2
import plankton_toolbox.activities.analyse_datasets_tab3 as tab3
import plankton_toolbox.activities.analyse_datasets_tab4 as tab4
import plankton_toolbox.activities.analyse_datasets_tab5 as tab5
import plankton_toolbox.activities.analyse_datasets_tab6 as tab6
import envmonlib

class AnalyseDatasetsActivity(activity_base.ActivityBase):
    """
    """
    def __init__(self, name, parentwidget):
        """ """
        # Tree dataset used for analysis. 
        self._currentdata = None
        # Initialize parent.
        super(AnalyseDatasetsActivity, self).__init__(name, parentwidget)
        # Filename used when saving data to file.
        self._lastuseddirectory = '.'
        # Initiate tab's.
        tab1.AnalyseDatasetsTab1().setMainActivity(self)
        tab2.AnalyseDatasetsTab2().setMainActivity(self)
        tab3.AnalyseDatasetsTab3().setMainActivity(self)
        tab4.AnalyseDatasetsTab4().setMainActivity(self)
        tab5.AnalyseDatasetsTab5().setMainActivity(self)
        tab6.AnalyseDatasetsTab6().setMainActivity(self)

    def _createContent(self):
        """ """
        content = self._createScrollableContent()
        contentLayout = QtGui.QVBoxLayout()
        content.setLayout(contentLayout)
        # Add activity name at top.
        self._activityheader = QtGui.QLabel('<h2>' + self.objectName() + '</h2>', self)
        self._activityheader.setTextFormat(QtCore.Qt.RichText)
        self._activityheader.setAlignment(QtCore.Qt.AlignHCenter)
        self._activityheader.setStyleSheet(""" 
            * { color: white; background-color: #00677f; }
            """)
        contentLayout.addWidget(self._activityheader)
        # Add content to the activity.
        contentLayout.addWidget(self._contentAnalyseTabs())
        contentLayout.addWidget(self._contentCurrentDataTable(), 10)
        contentLayout.addWidget(self._contentSaveCurrentData())
    
    def _contentAnalyseTabs(self):
        """ """
        # Active widgets and connections.
        selectdatabox = QtGui.QGroupBox("", self)
        tabWidget = QtGui.QTabWidget()
        tabWidget.addTab(tab1.AnalyseDatasetsTab1().contentSelectDatasets(), "Select dataset(s)")
###        tabWidget.addTab(tab2.AnalyseDatasetsTab2().contentFilterData(), "Filter data")
        tabWidget.addTab(tab3.AnalyseDatasetsTab3().contentAggregateData(), "Aggregate data")
        tabWidget.addTab(tab4.AnalyseDatasetsTab4().contentSelectData(), "Select data")
        tabWidget.addTab(tab5.AnalyseDatasetsTab5().contentPreparedGraphs(), "Prepared graphs")
        tabWidget.addTab(tab6.AnalyseDatasetsTab6().contentGenericGraphs(), "Generic graphs")
        # Layout widgets.
        layout = QtGui.QVBoxLayout()
        layout.addWidget(tabWidget)
        selectdatabox.setLayout(layout)        
        #
        return selectdatabox

    # ===== CURRENT DATA =====    
    def _contentCurrentDataTable(self):
        """ """
        # Active widgets and connections.
        currentdatagroupbox = QtGui.QGroupBox("Current data", self)
        # Active widgets and connections.
        self._tableview = utils_qt.ToolboxQTableView()
        # Layout widgets.
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self._tableview)
        #
        currentdatagroupbox.setLayout(layout)
        #
        return currentdatagroupbox

    def _contentSaveCurrentData(self):
        """ """
        saveresultbox = QtGui.QGroupBox("Save current data", self)
        # Active widgets and connections.
        self._saveformat_list = QtGui.QComboBox()
        #
        self._saveformat_list.addItems(["Tab delimited text file (*.txt)",
                                         "Excel file (*.xlsx)"])
        self._savedataset_button = QtGui.QPushButton("Save...")
        self.connect(self._savedataset_button, QtCore.SIGNAL("clicked()"), self._saveCurrentData)                
        # Layout widgets.
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addStretch(5)
        hbox1.addWidget(QtGui.QLabel("File format:"))
        hbox1.addWidget(self._saveformat_list)
        hbox1.addWidget(self._savedataset_button)
        #
        saveresultbox.setLayout(hbox1)
        #
        return saveresultbox
        
    def setCurrentData(self, current_data):
        """ """
        self._currentdata = current_data
        self.updateCurrentData()
    
    def getCurrentData(self):
        """ """
        return self._currentdata
    
    def updateCurrentData(self):
        """ """
        # Clear table.
        self._tableview.tablemodel.setModeldata(None)
        self._refreshCurrentDataTable()
        #
        if self._currentdata:
            # Convert from tree model to table model.
            targetdataset = envmonlib.DatasetTable()
            self._currentdata.convertToTableDataset(targetdataset)
            # View model.
            self._tableview.tablemodel.setModeldata(targetdataset)
            self._refreshCurrentDataTable()
        #
        self.updateAllTabs()
    
    def _refreshCurrentDataTable(self):
        """ """
        self._tableview.tablemodel.reset() # Model data has changed.
        self._tableview.resizeColumnsToContents()

    def _saveCurrentData(self):
        """ """
        if self._tableview.tablemodel.getModeldata():
            # Show select file dialog box.
            namefilter = 'All files (*.*)'
            if self._saveformat_list.currentIndex() == 1: # Xlsx file.
                namefilter = 'Excel files (*.xlsx);;All files (*.*)'
            else:
                namefilter = 'Text files (*.txt);;All files (*.*)'
            filename = QtGui.QFileDialog.getSaveFileName(
                            self,
                            'Save dataset',
                            self._lastuseddirectory,
                            namefilter)
            filename = unicode(filename) # QString to unicode.
            # Check if user pressed ok or cancel.
            if filename:
                self._lastuseddirectory = os.path.dirname(filename)
                if self._saveformat_list.currentIndex() == 0: # Text file.
                    self._tableview.tablemodel.getModeldata().saveAsTextFile(filename)
                elif self._saveformat_list.currentIndex() == 1: # Excel file.
                    self._tableview.tablemodel.getModeldata().saveAsExcelFile(filename)

    def clearAllTabs(self):
        """ """
        tab1.AnalyseDatasetsTab1().clear()
        tab2.AnalyseDatasetsTab2().clear()
        tab3.AnalyseDatasetsTab3().clear()
        tab4.AnalyseDatasetsTab4().clear()
        tab5.AnalyseDatasetsTab5().clear()
        tab6.AnalyseDatasetsTab6().clear()

    def updateAllTabs(self):
        """ """
        tab1.AnalyseDatasetsTab1().update()
        tab2.AnalyseDatasetsTab2().update()
        tab3.AnalyseDatasetsTab3().update()
        tab4.AnalyseDatasetsTab4().update()
        tab5.AnalyseDatasetsTab5().update()
        tab6.AnalyseDatasetsTab6().update()

    def getSelectDataDict(self):
        """ """
        return tab4.AnalyseDatasetsTab4().getSelectDataDict()

