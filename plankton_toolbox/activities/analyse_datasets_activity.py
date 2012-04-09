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
#import datetime
import copy
import plankton_toolbox.activities.activity_base as activity_base
import plankton_toolbox.tools.tool_manager as tool_manager
import plankton_toolbox.toolbox.utils_qt as utils_qt
import plankton_toolbox.toolbox.toolbox_datasets as toolbox_datasets
import mmfw

class AnalyseDatasetsActivity(activity_base.ActivityBase):
    """
    """
    def __init__(self, name, parentwidget):
        """ """
        # Tree dataset used for analysis. 
        self.__analysisdata = None
        # Initialize parent.
        super(AnalyseDatasetsActivity, self).__init__(name, parentwidget)
        # Filename used when saving data to file.
        self.__lastuseddirectory = '.'

    def _createContent(self):
        """ """
        content = self._createScrollableContent()
        contentLayout = QtGui.QVBoxLayout()
        content.setLayout(contentLayout)
        # Add activity name at top.
        self.__activityheader = QtGui.QLabel('<h2>' + self.objectName() + '</h2>', self)
        self.__activityheader.setTextFormat(QtCore.Qt.RichText)
        self.__activityheader.setAlignment(QtCore.Qt.AlignHCenter)
        self.__activityheader.setStyleSheet(""" 
            * { color: white; background-color: #00677f; }
            """)
        contentLayout.addWidget(self.__activityheader)
        # Add content to the activity.
        contentLayout.addWidget(self.__contentAnalyseTabs())
        contentLayout.addWidget(self.__contentCurrentDataTable(), 10)
        contentLayout.addWidget(self.__contentSaveCurrentData())
    
    def __contentAnalyseTabs(self):
        """ """
        # Active widgets and connections.
        selectdatabox = QtGui.QGroupBox("", self)
        tabWidget = QtGui.QTabWidget()
        tabWidget.addTab(self.__contentSelectDatasets(), "Select dataset(s)")
        tabWidget.addTab(self.__contentFilterData(), "Filter data")
        tabWidget.addTab(self.__contentAggregateData(), "Aggregate data")
        tabWidget.addTab(self.__contentSelectData(), "Select data")
        tabWidget.addTab(self.__contentPreparedGraphs(), "Prepared graphs")
        tabWidget.addTab(self.__contentGenericGraphs(), "Generic graphs")
        # Layout widgets.
        layout = QtGui.QVBoxLayout()
        layout.addWidget(tabWidget)
        selectdatabox.setLayout(layout)        
        #
        return selectdatabox

    # ===== TAB: Select dataset(s) ===== 
    def __contentSelectDatasets(self):
        """ """
        widget = QtGui.QWidget()
        # Active widgets and connections.
        introlabel = utils_qt.RichTextQLabel()
        introlabel.setText("""
        Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod 
        tempor incididunt ut labore et dolore magna aliqua.
        """)
        #
        loaded_datasets_listview = QtGui.QListView()
        loaded_datasets_listview.setMaximumHeight(80)
#        view.setMinimumWidth(500)
        self.__loaded_datasets_model = QtGui.QStandardItemModel()
        loaded_datasets_listview.setModel(self.__loaded_datasets_model)
        # Listen for changes in the toolbox dataset list.
        self.connect(toolbox_datasets.ToolboxDatasets(), 
                     QtCore.SIGNAL("datasetListChanged"), 
                     self.__updateLoadedDatasetList)
        #
        self.__clearcurrentdata_button = QtGui.QPushButton("Clear current data")
        self.connect(self.__clearcurrentdata_button, QtCore.SIGNAL("clicked()"), self._clearCurrentData)                
        self.__useselecteddatasets_button = QtGui.QPushButton("Use selected dataset(s)")
        self.connect(self.__useselecteddatasets_button, QtCore.SIGNAL("clicked()"), self.__useSelectedDatasets)                
        # Layout widgets.
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addStretch(10)
        hbox1.addWidget(self.__clearcurrentdata_button)
        hbox1.addWidget(self.__useselecteddatasets_button)
        #
        layout = QtGui.QVBoxLayout()
        layout.addWidget(introlabel)
        layout.addWidget(loaded_datasets_listview)
#        layout.addStretch(1)
        layout.addLayout(hbox1)
        widget.setLayout(layout)                
        #
        return widget

    def __updateLoadedDatasetList(self):
        """ """
        self.__loaded_datasets_model.clear()        
        for rowindex, dataset in enumerate(toolbox_datasets.ToolboxDatasets().getDatasets()):
            item = QtGui.QStandardItem(u"Dataset-" + unicode(rowindex) + 
                                       u".   Source: " + dataset.getMetadata(u'File name'))
            item.setCheckState(QtCore.Qt.Unchecked)
            item.setCheckable(True)
            self.__loaded_datasets_model.appendRow(item)

    def _clearCurrentData(self):
        """ """
        # Clear table.
        self.__analysisdata = None
        self.__updateCurrentData()    
        # Clear rows in comboboxes.
        self.__clearComboboxes()    

    def __useSelectedDatasets(self):
        """ """
        try:
            # Clear current data.
            self._clearCurrentData()    
            # Check if all selected datasets contains the same columns.
            compareheaders = None
            for rowindex in range(self.__loaded_datasets_model.rowCount()):
                item = self.__loaded_datasets_model.item(rowindex, 0)
                if item.checkState() == QtCore.Qt.Checked:
                    dataset = mmfw.Datasets().getDatasets()[rowindex]
                    if compareheaders == None:
                        compareheaders = dataset.getExportTableColumns()
                    else:
                        newheader = dataset.getExportTableColumns()
                        if len(compareheaders)==len(newheader) and \
                           all(compareheaders[i] == newheader[i] for i in range(len(compareheaders))):
                            pass # OK since export columns are equal.
                        else:
                            mmfw.Logging().log("Can't use datasets with different export columns. Please try again.")
                            raise UserWarning("Can't use datasets with different export columns. Please try again.")
            # Concatenate selected datasets.        
            dataset = None
            for rowindex in range(self.__loaded_datasets_model.rowCount()):
                item = self.__loaded_datasets_model.item(rowindex, 0)
                if item.checkState() == QtCore.Qt.Checked:        
                #             
                    if dataset == None:
                        # Deep copy of the first dataset.
                        dataset = copy.deepcopy(mmfw.Datasets().getDatasets()[rowindex])
                    else:
                        # Append top node data and children. Start with a deep copy.
                        tmp_dataset = copy.deepcopy(mmfw.Datasets().getDatasets()[rowindex])
                        for key, value in dataset.getDataDict():
                            dataset.addData(key, value)
                        for child in tmp_dataset.getChildren():
                            dataset.addChild(child)
            # Check.
            if (dataset == None) or (len(dataset.getChildren()) == 0):
                mmfw.Logging().log("Selected datasets are empty. Please try again.")
                raise UserWarning("Selected datasets are empty. Please try again.")
            # Use the concatenated datasets as current data.
            self.__analysisdata = dataset
            self.__updateCurrentData()    
            # Add rows in comboboxes.
            self.__reloadComboboxes()    
        except UserWarning, e:
            QtGui.QMessageBox.warning(self, "Warning", unicode(e))

    # ===== TAB: Filter data ===== 
    def __contentFilterData(self):
        """ """
        # Active widgets and connections.

        # Layout.
        widget = QtGui.QWidget()        
        layout = QtGui.QVBoxLayout()
        widget.setLayout(layout)
#        layout.addWidget(selectionbox)
#        layout.addWidget(resultbox)
        #
        return widget

    # ===== TAB: Aggregate data ===== 
    def __contentAggregateData(self):
        """ """
        # Active widgets and connections.

        # Layout.
        widget = QtGui.QWidget()        
        layout = QtGui.QVBoxLayout()
        widget.setLayout(layout)
#        layout.addWidget(selectionbox)
#        layout.addWidget(resultbox)
        #
        return widget

    # ===== TAB: Select data ===== 
    def __contentSelectData(self):
        """ """
        widget = QtGui.QWidget()
        # Active widgets and connections.
        introlabel = utils_qt.RichTextQLabel()
        introlabel.setText("""
        Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod 
        tempor incididunt ut labore et dolore magna aliqua.
        """)
        # Start date and end date.
        self.__startdate_edit = QtGui.QLineEdit("")
        self.__enddate_edit = QtGui.QLineEdit("")
        # Stations
        stations_listview = QtGui.QListView()
        stations_listview.setMaximumHeight(100)
        self.__select_stations_model = QtGui.QStandardItemModel()
        stations_listview.setModel(self.__select_stations_model)
        # Min-max depth.
        minmaxdepth_listview = QtGui.QListView()
        minmaxdepth_listview.setMaximumHeight(100)
        self.__selected_minmaxdepth_model = QtGui.QStandardItemModel()
        minmaxdepth_listview.setModel(self.__selected_minmaxdepth_model)
        # Trophy.
        trophy_listview = QtGui.QListView()
        trophy_listview.setMaximumHeight(100)
        self.__selected_trophy_model = QtGui.QStandardItemModel()
        trophy_listview.setModel(self.__selected_trophy_model)
        # Layout widgets.
        form1 = QtGui.QGridLayout()
        gridrow = 0
        label1 = QtGui.QLabel("Date from:")
        label2 = QtGui.QLabel("Stations:")
        label3 = QtGui.QLabel("Min-max depth:")
        label4 = QtGui.QLabel("Trophy:")
        form1.addWidget(label1, gridrow, 0, 1, 1)
        form1.addWidget(label2, gridrow, 1, 1, 1)
        form1.addWidget(label3, gridrow, 2, 1, 1)
        form1.addWidget(label4, gridrow, 3, 1, 1)
        gridrow += 1
        form1.addWidget(self.__startdate_edit, gridrow, 0, 1, 1)
        form1.addWidget(stations_listview, gridrow, 1, 4, 1)
        form1.addWidget(minmaxdepth_listview, gridrow, 2, 4, 1)
        form1.addWidget(trophy_listview, gridrow, 3, 4, 1)
        gridrow += 1
        label1 = QtGui.QLabel("Date to:")
        form1.addWidget(label1, gridrow, 0, 1, 1)
        gridrow += 1
        form1.addWidget(self.__enddate_edit, gridrow, 0, 1, 1)
        #
        layout = QtGui.QVBoxLayout()
        layout.addWidget(introlabel)
        layout.addLayout(form1)
        layout.addStretch(5)
        widget.setLayout(layout)                
        #
        return widget


    def __updateSelectDataAlternatives(self):
        """ """
        #
        startdate = '9999-99-99'
        enddate = '0000-00-00'
        stationset = set()
        minmaxdepthset = set()
        trophyset = set()
        #
        for visitnode in self.__analysisdata.getChildren():
            stationset.add(visitnode.getData(u'Station.reported name'))
            startdate = min(startdate, visitnode.getData(u'Date'))
            enddate = max(enddate, visitnode.getData(u'Date'))
            for samplenode in visitnode.getChildren():
                depthstring = samplenode.getData(u'Sample min depth') + '-' + samplenode.getData(u'Sample max depth')
                minmaxdepthset.add(depthstring)
                for variablenode in samplenode.getChildren():
                    trophyset.add(variablenode.getData(u'Trophy'))
        #
        stationlist = sorted(stationset)
        minmaxdepthlist = sorted(minmaxdepthset)
        trophylist = sorted(trophyset)


#        self.__startdate_edit
#        self.__enddate_edit
#        self.__select_stations_model
#        self.__selected_minmaxdepth_model
#        self.__selected_trophy_model
     
        #
        self.__select_stations_model.clear()        
        for station in stationlist:
            item = QtGui.QStandardItem(station)
            item.setCheckState(QtCore.Qt.Checked)
            item.setCheckable(True)
            self.__select_stations_model.appendRow(item)
    
    
    
    
    
    # ===== TAB: Prepared graphs ===== 
    def __contentPreparedGraphs(self):
        """ """
        # Active widgets and connections.

        # Layout.
        widget = QtGui.QWidget()        
        layout = QtGui.QVBoxLayout()
        widget.setLayout(layout)
#        layout.addWidget(selectionbox)
#        layout.addWidget(resultbox)
        #
        return widget

    # ===== TAB: Generic graphs ===== 
    def __contentGenericGraphs(self):
        """ """
        widget = QtGui.QWidget()
        # Active widgets and connections.
        introlabel = utils_qt.RichTextQLabel()
        introlabel.setText("""
        Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod 
        tempor incididunt ut labore et dolore magna aliqua.
        """)        
        # - Select column for x-axis:
        self.__x_axis_column_list = QtGui.QComboBox()
        self.__x_axis_column_list.setMinimumContentsLength(20)
        self.__x_axis_column_list.addItems([u"Parameter:"])
        self.__x_axis_column_list.setEnabled(False) # Disabled until rows are added.
        self.__x_axis_parameter_list = QtGui.QComboBox()        
        self.__x_axis_parameter_list.setMinimumContentsLength(20)
        self.__x_axis_parameter_list.setEnabled(False) # Disabled until rows are added.
        #
        self.connect(self.__x_axis_column_list, QtCore.SIGNAL("currentIndexChanged(int)"), self.__updateEnabledDisabled)                
        # - Add available column names.
#        self.__x_axis_column_list.addItems(self._matrix_list)                
        # - Select column for y-axis:
        self.__y_axis_column_list = QtGui.QComboBox()
        self.__y_axis_column_list.setMinimumContentsLength(20)
        self.__y_axis_column_list.addItems([u"Parameter:"])        
        self.__y_axis_column_list.setEnabled(False) # Disabled until rows are added.
        self.__y_axis_parameter_list = QtGui.QComboBox()
        self.__y_axis_parameter_list.setMinimumContentsLength(20)
        self.__y_axis_parameter_list.setEnabled(False) # Disabled until rows are added.
        #
        self.connect(self.__y_axis_column_list, QtCore.SIGNAL("currentIndexChanged(int)"), self.__updateEnabledDisabled)                
        # - Add available column names.
#        self.__x_axis_column_list.addItems(self._matrix_list)                

        # Draw graph.
        self.__plotindex_list = QtGui.QComboBox()
        self.__plotindex_list.addItems(["Time series 1", "Time series 2", "Time series 3", "Time series 4", 
                                       "X/Y plot 1", "X/Y plot 2", "X/Y plot 3", "X/Y plot 4"])
        self.__addplot_button = QtGui.QPushButton("Add plot")
        self.connect(self.__addplot_button, QtCore.SIGNAL("clicked()"), self.__addPlot)                
#        self.__addxyplot_button = QtGui.QPushButton("Add X/Y plot")
#        self.connect(self.__addxyplot_button, QtCore.SIGNAL("clicked()"), self.__addXYPlot)                

        # Layout widgets.
        form1 = QtGui.QGridLayout()
        gridrow = 0
        label1 = QtGui.QLabel("Select x-axis:")
        label2 = QtGui.QLabel("Parameter:")
        stretchlabel = QtGui.QLabel("")
        form1.addWidget(label1, gridrow, 0, 1, 1)
        form1.addWidget(self.__x_axis_column_list, gridrow, 1, 1, 1)
        form1.addWidget(label2, gridrow, 2, 1, 1)
        form1.addWidget(self.__x_axis_parameter_list, gridrow, 3, 1, 1)
        form1.addWidget(stretchlabel, gridrow,4, 1, 20)
        gridrow += 1
#        label1 = QtGui.QLabel("Select column for y-axis:")
#        form1.addWidget(label1, gridrow, 0, 1, 1)
#        form1.addWidget(self.__y_axis_column_list, gridrow, 1, 1, 1)
        label1 = QtGui.QLabel("Select y-axis:")
        label2 = QtGui.QLabel("Parameter:")
        form1.addWidget(label1, gridrow, 0, 1, 1)
        form1.addWidget(self.__y_axis_column_list, gridrow, 1, 1, 1)
        form1.addWidget(label2, gridrow, 2, 1, 1)
        form1.addWidget(self.__y_axis_parameter_list, gridrow, 3, 1, 1)
        #
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addStretch(10)
        hbox1.addWidget(QtGui.QLabel("Select plot:"))
        hbox1.addWidget(self.__plotindex_list)
        hbox1.addWidget(self.__addplot_button)
#        hbox1.addWidget(self.__addxyplot_button)
        #
        layout = QtGui.QVBoxLayout()
        layout.addWidget(introlabel)
        layout.addLayout(form1)
        layout.addStretch(1)
        layout.addLayout(hbox1)
        widget.setLayout(layout)                
        #
        return widget
        
    def __updateEnabledDisabled(self, index):
        """ """
        #
        if self.__x_axis_column_list.currentIndex() == 0:
            self.__x_axis_parameter_list.setEnabled(True)
        else:
            self.__x_axis_parameter_list.setEnabled(False)
        #
        if self.__y_axis_column_list.currentIndex() == 0:
            self.__y_axis_parameter_list.setEnabled(True)
        else:
            self.__y_axis_parameter_list.setEnabled(False)
            
    def __addPlot(self):
        """ """
        tool_manager.ToolManager().showToolByName(u'Graph plot') # Show tool if hidden.
        graphtool = tool_manager.ToolManager().getToolByName(u'Graph plot')
        # Selected columns.
        x_column = unicode(self.__x_axis_column_list.currentText())
        y_column = unicode(self.__y_axis_column_list.currentText())
        # Selected parameters.
        x_param = None
        y_param = None
        if x_column == u"Parameter:":
            x_param = unicode(self.__x_axis_parameter_list.currentText())
        if y_column == u"Parameter:":
            y_param = unicode(self.__y_axis_parameter_list.currentText())
        # Check exports columns backwards.
        x_visit_key = None
        x_sample_key = None                      
        x_variable_key = None
        y_visit_key = None
        y_sample_key = None                      
        y_variable_key = None
        if x_column != u"Parameter:":
            for export_info in self.__analysisdata.getExportTableColumns():
                if export_info.get('Header', u'') == x_column:
                    if export_info.get('Node', u'') == 'Visit':
                        x_visit_key =  export_info.get('Key', None)
                    elif export_info.get('Node', u'') == 'Sample':
                        x_sample_key =  export_info.get('Key', None)                        
                    elif export_info.get('Node', u'') == 'Variable':
                        x_variable_key =  export_info.get('Key', None)
        if y_column != u"Parameter:":
            for export_info in self.__analysisdata.getExportTableColumns():
                if export_info.get('Header', u'') == y_column:
                    if export_info.get('Node', u'') == 'Visit':
                        y_visit_key =  export_info.get('Key', None)
                    elif export_info.get('Node', u'') == 'Sample':
                        y_sample_key =  export_info.get('Key', None)                        
                    elif export_info.get('Node', u'') == 'Variable':
                        y_variable_key =  export_info.get('Key', None)
        
        # Extract data.
        x_data = []
        y_data = []
        x_value = None
        y_value = None
        #
        for visitnode in self.__analysisdata.getChildren(): 
            if x_visit_key: x_value = visitnode.getData(x_visit_key) # if x_visit_key else None
            if y_visit_key: y_value = visitnode.getData(y_visit_key) # if y_visit_key else None
            for samplenode in visitnode.getChildren():
                if x_sample_key: x_value = samplenode.getData(x_sample_key) # if x_sample_key else None
                if y_sample_key: y_value = samplenode.getData(y_sample_key) # if y_sample_key else None
                for variablenode in samplenode.getChildren():
                    #
                    if x_variable_key: x_value = variablenode.getData(x_variable_key) # if x_variable_key else None
                    if y_variable_key: y_value = variablenode.getData(y_variable_key) # if y_variable_key else None
                    #
                    if x_param or y_param:
                        parameter = variablenode.getData(u'Parameter')
                        if x_param:
                            if parameter == x_param:
                                x_value = variablenode.getData(u'Value')
                        if y_param:
                            if parameter == y_param:
                                y_value = variablenode.getData(u'Value')
                    # If NOT both are parameters, add data on variable level.
                    if not (x_param and y_param):
                        # Add values to lists if both values are available.
                        if (x_value and y_value):
                            x_data.append(x_value)
                            y_data.append(y_value)
                        # Clear used values.
                        if x_param: x_value = None    
                        if y_param: y_value = None    
                    # Clear used values.
                    if x_variable_key: x_value = None    
                    if x_variable_key: y_value = None
                # If both are parameters, add data on sample level.     
                if (x_param and y_param):
                    # Add values to lists if both values are available.
                    if (x_value and y_value):
                        x_data.append(x_value)
                        y_data.append(y_value)
                        # Clear used values.
                        if x_param: x_value = None    
                        if y_param: y_value = None    
                # Clear used values.
                if x_sample_key: x_value = None    
                if y_sample_key: y_value = None    
            # Clear used values.
            if x_visit_key: x_value = None    
            if y_visit_key: y_value = None    
        #

        # Check if this is a time series or not.
        selectedplotindex = self.__plotindex_list.currentIndex() 
        if selectedplotindex in [0, 1, 2, 3]:
            graphtool.addTimeseriesPlot(selectedplotindex, x_data, y_data)
        else:
            graphtool.addXYPlot(selectedplotindex - 4, x_data, y_data)

    # ===== CURRENT DATA =====    
    def __contentCurrentDataTable(self):
        """ """
        # Active widgets and connections.
        currentdatagroupbox = QtGui.QGroupBox("Current data", self)
        # Active widgets and connections.
        self.__tableview = utils_qt.ToolboxQTableView()
        # Layout widgets.
        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.__tableview)
        #
        currentdatagroupbox.setLayout(layout)
        #
        return currentdatagroupbox

    def __contentSaveCurrentData(self):
        """ """
        saveresultbox = QtGui.QGroupBox("Save current data", self)
        # Active widgets and connections.
        self.__saveformat_list = QtGui.QComboBox()
        #
        self.__saveformat_list.addItems(["Tab delimited text file (*.txt)",
                                         "Excel file (*.xlsx)"])
        self.__savedataset_button = QtGui.QPushButton("Save...")
        self.connect(self.__savedataset_button, QtCore.SIGNAL("clicked()"), self.__saveCurrentData)                
        # Layout widgets.
        hbox1 = QtGui.QHBoxLayout()
        hbox1.addStretch(5)
        hbox1.addWidget(QtGui.QLabel("File format:"))
        hbox1.addWidget(self.__saveformat_list)
        hbox1.addWidget(self.__savedataset_button)
        #
        saveresultbox.setLayout(hbox1)
        #
        return saveresultbox
        
    def __updateCurrentData(self):
        """ """
        # Clear table.
        self.__tableview.tablemodel.setModeldata(None)
        self.__refreshResultTable()
        #
        if self.__analysisdata:
            # Convert from tree model to table model.
            targetdataset = mmfw.DatasetTable()
            self.__analysisdata.convertToTableDataset(targetdataset)
            # View model.
            self.__tableview.tablemodel.setModeldata(targetdataset)
            self.__refreshResultTable()
    
    def __refreshResultTable(self):
        """ """
        self.__tableview.tablemodel.reset() # Model data has changed.
        self.__tableview.resizeColumnsToContents()

    def __saveCurrentData(self):
        """ """
        if self.__tableview.tablemodel.getModeldata():
            # Show select file dialog box.
            namefilter = 'All files (*.*)'
            if self.__saveformat_list.currentIndex() == 1: # Xlsx file.
                namefilter = 'Excel files (*.xlsx);;All files (*.*)'
            else:
                namefilter = 'Text files (*.txt);;All files (*.*)'
            filename = QtGui.QFileDialog.getSaveFileName(
                            self,
                            'Save dataset',
                            self.__lastuseddirectory,
                            namefilter)
            filename = unicode(filename) # QString to unicode.
            # Check if user pressed ok or cancel.
            if filename:
                self.__lastuseddirectory = os.path.dirname(filename)
                if self.__saveformat_list.currentIndex() == 0: # Text file.
                    self.__tableview.tablemodel.getModeldata().saveAsTextFile(filename)
                elif self.__saveformat_list.currentIndex() == 1: # Excel file.
                    self.__tableview.tablemodel.getModeldata().saveAsExcelFile(filename)
        
    # ===== COMMON METHODS ===== 
    def __clearComboboxes(self):
        """ """
        # Clear rows in comboboxes.
        self.__x_axis_column_list.clear()
        self.__x_axis_parameter_list.clear()
        self.__y_axis_column_list.clear()
        self.__y_axis_parameter_list.clear()
        self.__x_axis_column_list.addItems([u"Parameter:"])
        self.__y_axis_column_list.addItems([u"Parameter:"])

    def __reloadComboboxes(self):
        """ """
        # Reload the content of the rows in comboboxes.
        self.__x_axis_column_list.addItems([item[u'Header'] for item in self.__analysisdata.getExportTableColumns()])
        self.__y_axis_column_list.addItems([item[u'Header'] for item in self.__analysisdata.getExportTableColumns()])
        # Search for all parameters in current data.
        parameterset = set()
        for visitnode in self.__analysisdata.getChildren():
            for samplenode in visitnode.getChildren():
                for variablenode in samplenode.getChildren():
                    parameterset.add(variablenode.getData(u"Parameter"))
        parameterlist = sorted(parameterset)
        self.__x_axis_parameter_list.addItems(parameterlist)
        self.__y_axis_parameter_list.addItems(parameterlist)
        #  Make comboboxes visible.
        self.__x_axis_column_list.setEnabled(True)
        self.__y_axis_column_list.setEnabled(True)
        self.__x_axis_parameter_list.setEnabled(True)
        self.__y_axis_parameter_list.setEnabled(True)
        #
        #
        #
        self.__updateSelectDataAlternatives()

