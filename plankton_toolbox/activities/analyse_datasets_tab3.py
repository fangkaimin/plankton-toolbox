#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# Copyright (c) 2010-2014 SMHI, Swedish Meteorological and Hydrological Institute 
# License: MIT License (see LICENSE.txt or http://opensource.org/licenses/mit).
#

import PyQt4.QtGui as QtGui
import PyQt4.QtCore as QtCore
import plankton_toolbox.toolbox.utils_qt as utils_qt
import plankton_toolbox.toolbox.help_texts as help_texts
import envmonlib

class AnalyseDatasetsTab3(QtGui.QWidget):
    """ """
    def __init__(self):
        """ """
        self._main_activity = None
        self._analysisdata = None
        super(AnalyseDatasetsTab3, self).__init__()

    def setMainActivity(self, main_activity):
        """ """
        self._main_activity = main_activity
        self._analysisdata = main_activity.getAnalysisData()

    def clear(self):
        """ """
        self._trophy_listview.clear()
        
    def update(self):
        """ """
        self.clear()        
        self._updateSelectDataAlternatives()
        
    # ===== TAB: Aggregate data ===== 
    def contentAggregateData(self):
        """ """
        # Active widgets and connections.
        introlabel = utils_qt.RichTextQLabel()
        introlabel.setText(help_texts.HelpTexts().getText(u'AnalyseDatasetsTab3_intro'))
#         introlabel.setText("""
#         You may want to aggregate abundance or biovolume data from the level of size group or 
#         species level to a higher taxonomic level. 
#         A common task is to aggregate to genus or class level. 
#         Also a level termed Algal groups with fewer classes is available. 
#         Here you can also select only autotrophs (AU), mixotrophs (MX), heterotrophs (HT) or 
#         organisms with trophic type not specified (NS). 
#         For phytoplankton most often a combination is used, e.g. AU + MX for all organisms with photosynthesis.
#         """)
        # Active widgets and connections.
        # Aggregate over taxonomic rank.
        self._aggregate_rank_list = QtGui.QComboBox()
        self._aggregate_rank_list.addItems([
            u"Biota (all levels)",
            u"Plankton group",
            u"Kingdom",
            u"Phylum",
            u"Class",
            u"Order",
            u"Family",
            u"Genus",
            u"Species", 
            u"Kingdom (from dataset)",
            u"Phylum (from dataset)",
            u"Class (from dataset)",
            u"Order (from dataset)",
            u"Family (from dataset)",
            u"Genus (from dataset)",
            u"Species (from dataset)", 
            ])
        self._aggregate_rank_list.setCurrentIndex(4) # Default: Class.
        #  Aggregate over trophy.
        self._trophy_listview = utils_qt.SelectableQListView()
        self._trophy_listview.setMaximumHeight(80)
        #  Aggregate over life stage.
        self._lifestage_listview = utils_qt.SelectableQListView()
        self._lifestage_listview.setMaximumHeight(80)
        # Buttons.
        self._aggregatedata_button = QtGui.QPushButton("Aggregate data")
        self.connect(self._aggregatedata_button, QtCore.SIGNAL("clicked()"), self._aggregateData)
        #
        self._reloaddata_button = QtGui.QPushButton("Reload analysis data (no clean up)")
        self.connect(self._reloaddata_button, QtCore.SIGNAL("clicked()"), self._main_activity._tab1widget._copyDatasetsForAnalysis)
        #               
        self._addmissingtaxa_button = QtGui.QPushButton("Add 0 for not observed")
        self.connect(self._addmissingtaxa_button, QtCore.SIGNAL("clicked()"), self._addMissingTaxa)                
        # Layout widgets.
        form1 = QtGui.QGridLayout()
        gridrow = 0
        label1 = QtGui.QLabel("Aggregate over:")
        form1.addWidget(label1, gridrow, 0, 1, 4)
        label2 = QtGui.QLabel("Complement data:")
        form1.addWidget(label2, gridrow, 9, 1, 4)
        gridrow += 1
        label1 = QtGui.QLabel("Taxon level (rank):               ")
        label2 = QtGui.QLabel("Trophic type:")
        label3 = QtGui.QLabel("Life stage:")
        form1.addWidget(label1, gridrow, 0, 1, 1)
        form1.addWidget(label2, gridrow, 1, 1, 3)
        form1.addWidget(label3, gridrow, 4, 1, 3)
        form1.addWidget(QtGui.QLabel(""), gridrow, 3, 1, 6) # Stretch.
        gridrow += 1
        form1.addWidget(self._aggregate_rank_list, gridrow, 0, 1, 1)
        form1.addWidget(self._trophy_listview, gridrow, 1, 4, 3)
        form1.addWidget(self._lifestage_listview, gridrow, 4, 4, 3)
        form1.addWidget(self._addmissingtaxa_button, gridrow, 9, 1, 1)
        gridrow += 4
        form1.addWidget(self._reloaddata_button, gridrow, 0, 1, 1)
        form1.addWidget(self._aggregatedata_button, gridrow, 6, 1, 1)
        #
#        hbox1 = QtGui.QHBoxLayout()
#        hbox1.addStretch(5)
#        hbox1.addWidget(self._aggregatedata_button)
        #
        layout = QtGui.QVBoxLayout()
        layout.addWidget(introlabel)
        layout.addLayout(form1)
        layout.addStretch(5)
#        layout.addLayout(hbox1)
        self.setLayout(layout)                
        #
        return self

    def _aggregateData(self):
        """ """
        try:
#             if self._aggregate_rank_list.currentIndex() == 0:
#                 envmonlib.Logging().log("Taxon level is not selected. Please try again.")
#                 raise UserWarning("Taxon level is not selected. Please try again.")
            if not self._analysisdata.getData():
                envmonlib.Logging().log("No data is loaded for analysis. Please try again.")
                raise UserWarning("No data is loaded for analysis. Please try again.")                
            #
            selected_taxon_rank = unicode(self._aggregate_rank_list.currentText())
            selected_trophy_list = self._trophy_listview.getSelectedDataList()
            selected_trophy_text = u'-'.join(selected_trophy_list) 
            selected_lifestage_list = self._lifestage_listview.getSelectedDataList()
            selected_lifestage_text = u'-'.join(selected_lifestage_list) 
            #
            for visitnode in self._analysisdata.getData().getChildren()[:]: 
                for samplenode in visitnode.getChildren()[:]:
                    aggregatedvariables = {}
                    for variablenode in samplenode.getChildren()[:]:
                        value = variablenode.getData(u'value')
                        # Use values containing valid float data.
                        try:
#                            value = value.replace(u',', u'.').replace(u' ', u'')
                            value = float(value) 
                            #
                            if selected_taxon_rank == u"Biota (all levels)":
                                newtaxon = u'Biota' # Biota is above kingdom in the taxonomic hierarchy.
                            elif selected_taxon_rank == u"Plankton group":
                                newtaxon = envmonlib.Species().getPlanktonGroupFromTaxonName(variablenode.getData(u'taxon_name'))
                            elif selected_taxon_rank == u"Kingdom":
                                newtaxon = envmonlib.Species().getTaxonValue(variablenode.getData(u'taxon_name'), "Kingdom")
                            elif selected_taxon_rank == u"Phylum":
                                newtaxon = envmonlib.Species().getTaxonValue(variablenode.getData(u'taxon_name'), "Phylum")
                            elif selected_taxon_rank == u"Class":
                                newtaxon = envmonlib.Species().getTaxonValue(variablenode.getData(u'taxon_name'), "Class")
                            elif selected_taxon_rank == u"Order":
                                newtaxon = envmonlib.Species().getTaxonValue(variablenode.getData(u'taxon_name'), "Order")
                            elif selected_taxon_rank == u"Family":
                                newtaxon = envmonlib.Species().getTaxonValue(variablenode.getData(u'taxon_name'), "Family")
                            elif selected_taxon_rank == u"Genus":
                                newtaxon = envmonlib.Species().getTaxonValue(variablenode.getData(u'taxon_name'), "Genus")
                            elif selected_taxon_rank == u"Species": 
                                newtaxon = envmonlib.Species().getTaxonValue(variablenode.getData(u'taxon_name'), "Species")
                            elif selected_taxon_rank == u"Kingdom (from dataset)":
                                newtaxon = variablenode.getData(u'kingdom')
                            elif selected_taxon_rank == u"Phylum (from dataset)":
                                newtaxon = variablenode.getData(u'phylum')
                            elif selected_taxon_rank == u"Class (from dataset)":
                                newtaxon = variablenode.getData(u'class')
                            elif selected_taxon_rank == u"Order (from dataset)":
                                newtaxon = variablenode.getData(u'order')
                            elif selected_taxon_rank == u"Family (from dataset)":
                                newtaxon = variablenode.getData(u'family')
                            elif selected_taxon_rank == u"Genus (from dataset)":
                                newtaxon = variablenode.getData(u'genus')
                            elif selected_taxon_rank == u"Species (from dataset)": 
                                newtaxon = variablenode.getData(u'species')
                            # 
                            if not newtaxon:
                                newtaxon = u'not-designated' # Use this if empty.
                            #
                            taxontrophy = variablenode.getData(u'trophy')
                            if taxontrophy in selected_trophy_list:
                                taxontrophy = selected_trophy_text # Concatenated string of ranks.
                            else:
                                continue # Phytoplankton only: Use selected trophy only, don't use others.  
                            #
                            stage = variablenode.getData(u'stage')
                            sex = variablenode.getData(u'sex')
                            checkstage = stage
                            if sex:
                                checkstage += u'/' + sex
                            if checkstage in selected_lifestage_list:
                                stage = selected_lifestage_text
                                sex = u''
#                             else:
#                                 continue # Note: Don't skip for zooplankton.                 
                            #
                            parameter = variablenode.getData(u'parameter')
                            unit = variablenode.getData(u'unit')
                             
                            agg_tuple = (newtaxon, taxontrophy, stage, sex, parameter, unit)
                            if agg_tuple in aggregatedvariables:
                                aggregatedvariables[agg_tuple] = value + aggregatedvariables[agg_tuple]
                            else:
                                aggregatedvariables[agg_tuple] = value
                        except:
                            if variablenode.getData(u'value'):
                                envmonlib.Logging().warning(u"Value is not a valid float: " + unicode(variablenode.getData(u'Value')))
                    #Remove all variables for this sample.
                    samplenode.removeAllChildren()
                    # Add the new aggregated variables instead.  
                    for variablekeytuple in aggregatedvariables:
                        newtaxon, taxontrophy, stage, sex, parameter, unit = variablekeytuple
                        #
                        newvariable = envmonlib.VariableNode()
                        samplenode.addChild(newvariable)    
                        #
                        newvariable.addData(u'taxon_name', newtaxon)
                        newvariable.addData(u'trophy', taxontrophy)
                        newvariable.addData(u'stage', stage)
                        newvariable.addData(u'sex', sex)
                        newvariable.addData(u'parameter', parameter)
                        newvariable.addData(u'unit', unit)
                        newvariable.addData(u'value', aggregatedvariables[variablekeytuple])
                        # Add taxon class, etc. based on taxon name.
                        newvariable.addData(u'kingdom', envmonlib.Species().getTaxonValue(newtaxon, "Kingdom"))
                        newvariable.addData(u'phylum', envmonlib.Species().getTaxonValue(newtaxon, "Phylum"))
                        newvariable.addData(u'class', envmonlib.Species().getTaxonValue(newtaxon, "Class"))
                        newvariable.addData(u'order', envmonlib.Species().getTaxonValue(newtaxon, "Order"))
            #
            self._main_activity.updateViewedDataAndTabs()    
        except UserWarning, e:
            QtGui.QMessageBox.warning(self._main_activity, "Warning", unicode(e))

    def _updateSelectDataAlternatives(self):
        """ """
        analysisdata = self._analysisdata.getData()
        if not analysisdata:
            return # Empty data.
        #
        trophyset = set()
        lifestageset = set()
        for visitnode in analysisdata.getChildren():
            for samplenode in visitnode.getChildren():
                for variablenode in samplenode.getChildren():
                    #
                    trophyset.add(unicode(variablenode.getData(u'trophy')))
                    #
                    lifestage = variablenode.getData(u'stage')
                    if variablenode.getData(u'sex'):
                        lifestage += u'/' + variablenode.getData(u'sex')
                    lifestageset.add(lifestage)
        # Selection lists.
        self._trophy_listview.setList(sorted(trophyset))
        self._lifestage_listview.setList(sorted(lifestageset))
            
    def _addMissingTaxa(self):
        """ """
        try:
            analysisdata = self._analysisdata.getData()
            if not analysisdata:        
                return
            # 
            envmonlib.AnalysisPrepare().addMissingTaxa(analysisdata)
            #
            self._main_activity.updateViewedDataAndTabs()    
        except UserWarning, e:
            QtGui.QMessageBox.warning(self._main_activity, "Warning", unicode(e))

