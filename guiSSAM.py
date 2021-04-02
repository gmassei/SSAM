# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name            : SSAM - Spatial Sustainability Assessment Model
Description     : geographical MCDA for sustainability assessment
Date            : 6/2/2021
copyright       : ARPA Umbria - Università degli Studi di Perugia (C) 2019
email           : (developper) Gianluca Massei (geonomica@gmail.com)

 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                   *
 *                                                                         *
 ***************************************************************************/
"""
from __future__ import print_function
from __future__ import absolute_import
from builtins import zip
from builtins import str
from builtins import range

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qgis.PyQt import QtGui
from qgis.core import *
from qgis.gui import *
    
import os
import sys
import webbrowser
import shutil
import json
import pickle

from .TOPSIS import *
from . import DOMLEM
from . import htmlGraph
from .analysis import *

#from .ui_geoSUST import Ui_Dialog


class guiSSAMDialog(QDialog):
    """Main gui control"""
    def __init__(self,iface):
        title="SSAM (Spatial Sustainability Assessment Model)"
        QDialog.__init__(self, iface.mainWindow())
        self.iface = iface
        self.activeLayer = self.iface.activeLayer()
        #self.currentDIR = (os.path.dirname(str(self.activeLayer.source())))
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.initUi()
        self.resize(650, 400)
        self.setWindowTitle(title)
        self.setWindowModality(Qt.ApplicationModal)
        # Add toolbar and items
        self.evalTableList=[] #list of evalTables added on pages

        
    def initUi(self):
        """Inizialize SSAM dialog """
        pluginDir = os.path.abspath( os.path.dirname(__file__))
        self.pages=QTabWidget()
        
        self.allFields=[f.name() for f in self.activeLayer.fields() if f.typeName()=='Real'or f.typeName()=='Integer64'] 
        self.getField=CollectField(self.allFields) #Object for selsect correct fields
        self.layout.addWidget(self.getField,0,0)
        
        self.pageNameCbBx = QComboBox(self)
        self.pageNameCbBx.setToolTip("Set dimension (page) name")
        dimList = ["Environmental", "Economic", "Social"]
        self.pageNameCbBx.addItems(dimList)
        self.pageNameCbBx.setEditable(True)
        self.layout.addWidget(self.pageNameCbBx,0,1)
               
        self.add_button = QPushButton()#"Add page")
        self.add_button.setToolTip("Add dimension")
        self.layout.addWidget(self.add_button, 1, 1)
        self.add_button.clicked.connect(self.addPage)
        iconAdd = os.path.join(pluginDir, "icons","add.png")
        self.add_button.setIcon(QIcon(iconAdd))
        self.add_button.setIconSize(QSize(48,48))
        self.add_button.setShortcut('Ctrl++')
  
        self.rem_button=QPushButton()
        self.rem_button.setToolTip("Remove dimension")
        self.layout.addWidget(self.rem_button, 2, 1)
        self.rem_button.clicked.connect(self.removePage)
        iconRemove = os.path.join(pluginDir, "icons","remove.png")
        self.rem_button.setIcon(QIcon(iconRemove))
        self.rem_button.setIconSize(QSize(48,48))
        self.rem_button.setShortcut('Ctrl+-')
                
        self.reaload_button = QPushButton()
        self.reaload_button.setToolTip("Reload")
        self.layout.addWidget(self.reaload_button, 3, 1)
        self.reaload_button.clicked.connect(self.reload)
        iconReload = os.path.join(pluginDir, "icons","reload.png")
        self.reaload_button.setIcon(QIcon(iconReload))
        self.reaload_button.setIconSize(QSize(48,48))
        self.reaload_button.setShortcut('Ctrl+R')
        
        self.run_button=QPushButton()
        self.run_button.setToolTip("Process")
        self.layout.addWidget(self.run_button,4,1)
        self.run_button.clicked.connect(self.run)
        iconProcess = os.path.join(pluginDir, "icons","process.png")
        self.run_button.setIcon(QIcon(iconProcess))
        self.run_button.setIconSize(QSize(48,48))
        self.run_button.setShortcut('Ctrl+P')
        
        self.layout.addWidget(self.pages, 0,0,6,1)
        self.pages.addTab(self.getField, "Setting")
        
        #activePage = self.pages.currentIndex()
        self.pages.setContextMenuPolicy(Qt.CustomContextMenu)
        self.pages.customContextMenuRequested.connect(self.popMenu)
        

        

    def popMenu(self):
        """Build pop menu """
        menu = QMenu()
        addAction = menu.addAction("Add new dimension")
        removeAction = menu.addAction("Remove current dimension")
        jsonAction=menu.addAction("Load data from JSON")
        runAction = menu.addAction("Process")
        action = menu.exec_(self.mapToGlobal(QPoint(100,100)))
        if action==addAction:
            self.addPage()
        elif action == removeAction:
            self.removePage()
        elif action==jsonAction:
            self.addPagesFromJSON()
        elif action==runAction:
            self.run()

            
            
            
    def addPage(self):
        """Add a page to self.pages (QTabWidget()) and insert EvalTable object in each one;
        append new EvalTable object in evalTableList """
        selectedItems = self.getField.listAllFields.selectedItems()
        fieldList=[item.text() for item in selectedItems]
        [self.getField.listAllFields.takeItem(self.getField.listAllFields.row(item)) for item in selectedItems]
        self.eTable=EvalTable(fieldList,self.activeLayer)#new table object
        self.evalTableList.append(self.eTable)#Object table added in each new page
        pageName = str(self.pageNameCbBx.currentText())
        if pageName!='':
            self.pages.addTab(self.eTable, pageName)
        else:
            pageName="dimension {}".format(self.pages.count())
        idTab=self.pages.addTab(self.eTable, pageName)
        self.pages.setCurrentIndex(idTab)
        self.pages.currentWidget().setObjectName(pageName)
                
        allItems = [self.pageNameCbBx.itemText(i) for i in range(self.pageNameCbBx.count())]
        if pageName in allItems:
            allItems.remove(pageName)
            self.pageNameCbBx.clear()
            self.pageNameCbBx.addItems(allItems)

    def addPagesFromJSON(self):
        """Retrieve parameter from JSON file and setting pages and parameters"""
        currentDIR = (os.path.dirname(str(self.activeLayer.source())))
        parameterFile=(os.path.join(currentDIR,"parameteres.jsonl"))
        if os.path.exists(parameterFile):
            parameterList=[]
            with open(parameterFile, "r",encoding='utf-8') as fp:
                for l in fp:
                    parameterList.append(json.loads(l.rstrip('\n|\r')))
            for parameter in parameterList:
                self.eTable=EvalTable(parameter['criteria'],self.activeLayer)#new table object
                idTab=self.pages.addTab(self.eTable, parameter['dimension'])
                self.pages.setCurrentIndex(idTab)
                self.pages.currentWidget().setObjectName(parameter['dimension'])
                self.eTable.updateTable(parameter['criteria'],parameter['weights'],
                                        parameter['preference'],parameter['idealPoint'],
                                        parameter['worstPoint'])
                self.evalTableList.append(self.eTable)
            self.parameterList=parameterList
            

    def removePage(self):
        """Remove selected page to self.pages (QTabWidget()) and the 
        EvalTable from object in evalTableList """
        idTab=self.pages.currentIndex()
        name=self.pages.currentWidget().objectName()
        print(id,name,self.evalTableList)
        #id=self.toolbox.currentIndex()
        if idTab==0:
            QMessageBox.warning(self.iface.mainWindow(), "SSAM",
            ("Setting page isn't removable"), QMessageBox.Ok, QMessageBox.Ok)
        else:
            self.pages.removeTab(idTab)
            [self.evalTableList.remove(o) for o in self.evalTableList if o.objectName()==name]
            
    def reload(self):
        """Reload all field in setting page"""
        self.getField.listAllFields.clear()
        self.getField.listAllFields.addItems(self.allFields)
        
        
    def retrieveParameters(self):
        """For each page/dimension retrieve all parameters and build [parametersList]
        as a list of {parameters} dictionary"""
        self.parameterList=[]
        dimensions=[w.objectName() for w in self.evalTableList ] #retrieve table name for each dimension page
        for i in range(len(self.evalTableList)):
            dimension=dimensions[i] 
            if "Analysis" != dimension:
                criteria=[self.evalTableList[i].tableWidget.horizontalHeaderItem(f).text() for f in range(self.evalTableList[i].tableWidget.columnCount())]
                weights=[float(self.evalTableList[i].tableWidget.item(0, c).text()) for c in range(self.evalTableList[i].tableWidget.columnCount())]
                preference=[self.evalTableList[i].tableWidget.item(1, c).text() for c in range(self.evalTableList[i].tableWidget.columnCount())]
                idealPoint=[float(self.evalTableList[i].tableWidget.item(2, c).text()) for c in range(self.evalTableList[i].tableWidget.columnCount())]
                worstPoint=[float(self.evalTableList[i].tableWidget.item(3, c).text()) for c in range(self.evalTableList[i].tableWidget.columnCount())]
                parameters={'dimension':dimension,'criteria':criteria,'weights':weights,'preference':preference,'idealPoint':idealPoint,'worstPoint':worstPoint}
                self.parameterList.append(parameters)
                
                
    def addAnalisysPage(self):
        """Add Analysis page """
        analysis=SSAMAnlisys(self.activeLayer,self.parameterList)
        for i in range(self.pages.count()):
            if self.pages.tabText(i) == "Analysis":
                page = self.pages.findChild(QWidget, "Analysis")
                index = self.pages.indexOf(page)
                self.pages.setCurrentIndex(index)
                self.pages.removeTab(index)
        index=self.pages.addTab(analysis, "Analysis")
        self.pages.setCurrentIndex(index)
        self.pages.currentWidget().setObjectName("Analysis")
            

    def parameterToJSON(self):
        """Save parameter dictionary to JSON file"""
        currentDIR = (os.path.dirname(str(self.activeLayer.source())))
        parameterFile=(os.path.join(currentDIR,"parameteres.jsonl"))
        with open(parameterFile, 'w',encoding='utf-8') as fp:
            for parameterDict in self.parameterList:
                parameterLine=json.dumps(parameterDict,  ensure_ascii=False)
                fp.write(parameterLine+'\n')
                

    
    def run(self):
        """Run TOPSIS models """
        self.retrieveParameters()
        for parameters in self.parameterList:
            topsis=TOPSIS(self.activeLayer, parameters)
            topsis.runTOPSIS()
            self.process=Processor(self.pages.count(),self.activeLayer,parameters,topsis.relativeCloseness)
            print(topsis.relativeCloseness)
        self.addAnalisysPage()
        self.parameterToJSON()
        #name = self.findChild(self.pages, "Analysis")

        
        
class CollectField(QWidget):
    """ List all fileds, select and manage critaria in setting tab"""
    def __init__(self,allFields):
        QWidget.__init__(self)
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        self.listAllFields = QListWidget(self)
        #self.listAllFields.setFixedSize(150, 150)
        self.listAllFields.setSelectionMode(QAbstractItemView.MultiSelection)
        self.layout.addWidget(self.listAllFields,0,0,4,1)
        self.listAllFields.addItems(allFields)

    def selectFields(self):
        "add criteria fiends in selected list"
        selectedItems = self.listAllFields.selectedItems()
        [self.listAllFields.takeItem(self.listAllFields.row(item)) for item in selectedItems]
        self.selectedField.addItems([item.text() for item in selectedItems])

    def deselectFields(self):
        "Remove criteria fields from selected list"
        selectedItems = self.selectedField.selectedItems()
        [self.selectedField.takeItem(self.selectedField.row(item)) for item in selectedItems]
        self.listAllFields.addItems([item.text() for item in selectedItems])
        
        

class EvalTable(QWidget):
    """Build evaluation table for each page/dimension"""
    def __init__(self,selectedField,activeLayer):
        QWidget.__init__(self)
        self.selectedField=selectedField
        self.activeLayer=activeLayer
        self.central = QWidget(self)
        self.mainLayout = QVBoxLayout(self.central)
        # add a "margin"
        self.mainLayout.addStretch(1)
        self.buttonLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.buttonLayout)
        # add a "margin"
        self.buttonLayout.addStretch(1)
        # add a "margin"
        self.mainLayout.addStretch(1)  
        self.tableLayout = QVBoxLayout()
        self.mainLayout.addLayout(self.tableLayout)
        # add a top "margin"
        self.tableLayout.addStretch(1)
        self.setTable()

    def setTable(self):    
        """Set table for new page with default values """
        setLabel=["weights","Preference","Ideal point", "Worst point "]
        self.tableWidget = QTableWidget()
        self.tableLayout.addWidget(self.tableWidget)
        self.tableWidget.setFixedSize(600, 180)
        self.tableWidget.setColumnCount(len(self.selectedField))
        self.tableWidget.setHorizontalHeaderLabels(self.selectedField)
        self.tableWidget.setRowCount(len(setLabel))
        self.tableWidget.setVerticalHeaderLabels(setLabel)
        for r in range(len(self.selectedField)): #TODO: remove duplicated code
            idx = self.activeLayer.fields().indexFromName(self.selectedField[r])
            self.tableWidget.setItem(0,r,QTableWidgetItem("1.0"))
            self.tableWidget.setItem(1,r,QTableWidgetItem("gain"))
            self.tableWidget.setItem(2,r,QTableWidgetItem(str(self.activeLayer.maximumValue(idx))))
            self.tableWidget.setItem(3,r,QTableWidgetItem(str(self.activeLayer.minimumValue(idx))))
        self.tableLayout.addStretch(1)
        # add a margin to the right
        self.mainLayout.addStretch(1)
        self.tableWidget.cellClicked[(int,int)].connect(self.changeValue)
       
    def updateTable(self,criteria,weights,preference,idealPoint,worstPoint):
        """ update table in a paage from json values or by parameters input """
        print(criteria,weights,preference,idealPoint,worstPoint)
        for r in range(len(criteria)): #TODO: remove duplicated code
            self.tableWidget.setItem(0,r,QTableWidgetItem(str(weights[r])))
            self.tableWidget.setItem(1,r,QTableWidgetItem(str(preference[r])))
            self.tableWidget.setItem(2,r,QTableWidgetItem(str(idealPoint[r])))
            self.tableWidget.setItem(3,r,QTableWidgetItem(str(worstPoint[r])))
        
    def changeValue(self):
        """Function for clicked signal change values """
        cell=self.tableWidget.currentItem()
        r=cell.row()
        c=cell.column()
        first=self.tableWidget.item(2, c).text()
        second=self.tableWidget.item(3, c).text()
        if cell.row()==1:
            val=cell.text()
            if val=="cost":
                self.tableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("gain"))
            elif val=="gain":
                self.tableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("cost"))
            else:
                self.tableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem(str(val)))
            self.tableWidget.setItem(2,c, QTableWidgetItem(second))
            self.tableWidget.setItem(3,c, QTableWidgetItem(first))
        
        
class Processor(QWidget):
    """Run elaborate options"""
    def __init__(self,numPages,activeLayer,parameters,relativeCloseness):
        QWidget.__init__(self)
        self.layout = QGridLayout()
        self.activeLayer=activeLayer
        self.parameters=parameters
        self.relativeCloseness=relativeCloseness
        self.lblNum = QLabel("pages count {}".format(self.activeLayer.name()), self)
        self.layout.addWidget(self.lblNum,0,0)
        #self.getCriteriaValue()
        self.process()
        
    def sumCriteria(criteria):
        """ Sum up all criteria values NOT YET USED"""
        feat = aLayer.getFeatures()
        criteriaValues=[f[criteria] for f in feat]
        return sum(criteriaValues)
            
    def process(self):
        """ Elaborate """
        provider = self.activeLayer.dataProvider()
        if provider.fieldNameIndex(self.parameters['dimension'])==-1:
            print(provider.fieldNameIndex(self.parameters['dimension']))
            self.activeLayer.dataProvider().addAttributes([QgsField(self.parameters['dimension'], QVariant.Double,"",24,4,"")] )
            #edit is a shortcut that replaces layer.beginEditCommand and layer.endEditCommand
        with edit(self.activeLayer):
            for f,i in zip(self.activeLayer.getFeatures(),range(len(self.relativeCloseness))):
                f[self.parameters['dimension']] = self.relativeCloseness[i] # f[self.parameters['criteria'][0]] + f[self.parameters['criteria'][1]]
                self.activeLayer.updateFeature(f)
        

