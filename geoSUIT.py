# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name            : SSAM - Spatial Sustainability Assessment Model
Description     : geographical MCDA for sustainability assessment
Date            : 10/05/2019
copyright       : ARPA Umbria - Università degli Studi di Perugia (C) 2019
email           : (developper) Gianluca Massei (g_massa@libero.it)

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
from PyQt5.QtWidgets import QDialog, QMessageBox, QTableWidget, QTableWidgetItem, QMenu, QFileDialog
from qgis.PyQt import QtGui
from qgis.core import *
from qgis.gui import *
	
import os
import webbrowser
import shutil
import csv
import pickle

from . import DOMLEM
from . import htmlGraph
from .cartogram import *

from .ui_geoSUIT import Ui_Dialog

class geoSUITDialog(QDialog, Ui_Dialog):
	def __init__(self, iface):
		'''costruttore'''
		
		QDialog.__init__(self, iface.mainWindow())
		self.setupUi(self)
		self.iface = iface
		self.active_layer = self.iface.activeLayer()
		self.base_Layer = self.iface.activeLayer()
		for i in range(1,self.toolBox.count()):
			self.toolBox.setItemEnabled (i,False)
		#self.SetBtnQuit.clicked.connect(self.reject)
		self.RetriveFileTBtn.clicked.connect(self.outFile)
		self.SetBtnBox.clicked.connect(self.settingStart)
		#self.SetBtnBox.clicked.connect(self.reject)
		self.SetBtnAbout.clicked.connect(self.about)
		self.SetBtnHelp.clicked.connect(self.open_help)
		self.EnvSaveCfgBtn.clicked.connect(self.saveCfg)
		self.EcoSaveCfgBtn.clicked.connect(self.saveCfg)
		self.SocSaveCfgBtn.clicked.connect(self.saveCfg)
		self.addLayerBtnENV.clicked.connect(self.addEnvLayers)
		self.removeLayerBtnENV.clicked.connect(self.removeEnvLayers)
		self.addLayerBtnECO.clicked.connect(self.addEcoLayers)
		self.removeLayerBtnECO.clicked.connect(self.removeEcoLayers)
		self.addLayerBtnSOC.clicked.connect(self.addSocLayers)
		self.removeLayerBtnSOC.clicked.connect(self.removeSocLayers)
		self.EnvGetWeightBtn.clicked.connect(self.elaborate)
		self.EcoGetWeightBtn.clicked.connect(self.elaborate)
		self.SocGetWeightBtn.clicked.connect(self.elaborate)

		
		self.sliders = [self.EnvSlider,self.EcoSlider,self.SocSlider]
		i=0
		slider_amount=10
		slider_precision = 10 
		for slider in self.sliders:
			i=i+1
			slider.setRange(0, slider_amount*slider_precision)
			slider.setSingleStep(slider.maximum()/100.0)
			slider.setPageStep(slider.maximum()/20.0)
			slider.valueChanged.connect(self.onSliderValueChanged)
			slider.float_value = (i+1)/((1+slider_amount)/2.0*slider_amount)
		self.updateSliderValues()
		
		self.pushBtnEval.clicked.connect(self.overalValue)
		self.RenderMapBtn.clicked.connect(self.renderLayer)
		self.RenderCarogramBtn.clicked.connect(self.renderCartogram)
		self.GraphBtn.clicked.connect(self.buildOutput)
		
		self.AnlsBtnBox.clicked.connect(self.reject)
		self.CritExtractBtn.clicked.connect(self.extractRules)
		self.SaveRulesBtn.clicked.connect(self.saveRules)

###############################ContextMenu########################################
		envHeaders = self.EnvWeighTableWidget.horizontalHeader()
		envHeaders.setContextMenuPolicy(Qt.CustomContextMenu)
		envHeaders.customContextMenuRequested.connect(self.popMenu)
		
		ecoHeaders = self.EcoWeighTableWidget.horizontalHeader()
		ecoHeaders.setContextMenuPolicy(Qt.CustomContextMenu)
		ecoHeaders.customContextMenuRequested.connect(self.popMenu)
		
		socHeaders = self.SocWeighTableWidget.horizontalHeader()
		socHeaders.setContextMenuPolicy(Qt.CustomContextMenu)
		socHeaders.customContextMenuRequested.connect(self.popMenu)
##################################################################################
		sourceIn=str(self.iface.activeLayer().source())
		self.BaseLayerLbl.setText(sourceIn)
		
		self.baseLbl.setText(sourceIn)
		pathSource=os.path.dirname(sourceIn)
		outputFile="geosustainability.shp"
		sourceOut=os.path.join(pathSource,outputFile)
		self.OutlEdt.setText(str(sourceOut))
		
		fields = [field.name() for field in self.active_layer.fields() ]
		self.LabelListFieldsCBox.addItems(fields) #all fields
		self.LabelCartogramCBox.addItems(['EnvIdeal','EcoIdeal','SocIdeal', 'SustIdeal'])
				
		self.EnvMapNameLbl.setText(self.active_layer.name())
		self.EcoMapNameLbl.setText(self.active_layer.name())
		self.SocMapNameLbl.setText(self.active_layer.name())
		
###############build list widget field#############################################
		allFields=self.getFieldNames(self.active_layer)
		self.listAllFields.addItems(allFields)
#################################################################################
		currentDir=unicode(os.path.abspath( os.path.dirname(__file__)))
		self.LblLogo.setPixmap(QtGui.QPixmap(os.path.join(currentDir,"icon.png")))


	def addEnvLayers(self):
		"add criteria fiends in environmental list"
		selectedItems = self.listAllFields.selectedItems()
		[self.listAllFields.takeItem(self.listAllFields.row(item)) for item in selectedItems]
		self.listEnvFields.addItems([item.text() for item in selectedItems])

	def removeEnvLayers(self):
		"remove criteria fields from environmental list"
		selectedItems = self.listEnvFields.selectedItems()
		[self.listEnvFields.takeItem(self.listEnvFields.row(item)) for item in selectedItems]
		self.listAllFields.addItems([item.text() for item in selectedItems])

	def addEcoLayers(self):
		"add criteria fiends in environmental list"
		selectedItems = self.listAllFields.selectedItems()
		[self.listAllFields.takeItem(self.listAllFields.row(item)) for item in selectedItems]
		self.listEcoFields.addItems([item.text() for item in selectedItems])

	def removeEcoLayers(self):
		"remove criteria fields from environmental list"
		selectedItems = self.listEcoFields.selectedItems()
		[self.listEcoFields.takeItem(self.listEcoFields.row(item)) for item in selectedItems]
		self.listAllFields.addItems([item.text() for item in selectedItems])
		
	def addSocLayers(self):
		"add criteria fiends in environmental list"
		selectedItems = self.listAllFields.selectedItems()
		[self.listAllFields.takeItem(self.listAllFields.row(item)) for item in selectedItems]
		self.listSocFields.addItems([item.text() for item in selectedItems])

	def removeSocLayers(self):
		"remove criteria fields from environmental list"
		selectedItems = self.listSocFields.selectedItems()
		[self.listSocFields.takeItem(self.listSocFields.row(item)) for item in selectedItems]
		self.listAllFields.addItems([item.text() for item in selectedItems])
		

	def popMenu(self):
		fields=range(10)
		menu = QMenu()
		removeAction = menu.addAction("Remove selected fields")
		#reloadAllFields=menu.addAction("Add deleted fields")
		action = menu.exec_(self.mapToGlobal(QPoint(100,100)))
		if action == removeAction:
			if self.toolBox.currentIndex()==1:
				self.removePopup(self.EnvWeighTableWidget)
			elif self.toolBox.currentIndex()==2:
				self.removePopup(self.EcoWeighTableWidget)
			elif self.toolBox.currentIndex()==3:
				self.removePopup(self.SocWeighTableWidget)
			
		
			
	def removePopup(self,table):
		#selected = sorted(self.EnvWeighTableWidget.selectedColumns(),reverse=True)
		selected = sorted(table.selectionModel().selectedColumns(),reverse=True)
		if len(selected) > 0:
			for s in selected:
				self.removeField(s.column(),table)
			table.setCurrentCell(-1,-1)
			table.setCurrentCell(-1,-1)
		else:
			QMessageBox.warning(self.iface.mainWindow(), "SSAM",
			("column must to be selected"), QMessageBox.Ok, QMessageBox.Ok)
		return 0
		
	def removeField(self,i,table):
		"""Remove field in table in GUI"""
		table.removeColumn(i)
		return 0
		
	def getFieldNames(self, layer):
		"""retrive field names from active map/layer"""
		fields = layer.dataProvider().fields()
		field_list = []
		for field in fields:
			if field.typeName()!='String':
				field_list.append(str(field.name()))
		return field_list


	def outFile(self):
		"""Display file dialog for output  file"""
		self.OutlEdt.clear()
		outvLayer = QFileDialog.getSaveFileName(self, "Output map",".", "ESRI Shapefile (*.shp)")
		self.OutlEdt.insert(outvLayer[0])
		return outvLayer


	def settingStart(self):
		""" Prepare file for processing """
		outputFilename=self.OutlEdt.text()
		for i in range(1,(self.toolBox.count()-1)):
			self.toolBox.setItemEnabled (i,True)
		alayer = self.base_Layer #self.iface.activeLayer()
		provider = alayer.dataProvider()
		fields = provider.fields()
		writer = QgsVectorFileWriter(outputFilename, "CP1250", fields, alayer.wkbType(), alayer.crs(), "ESRI Shapefile")
		outFeat = QgsFeature()
		self.LoadProgressBar.setRange(1,alayer.featureCount())
		progress=0
		for inFeat in alayer.getFeatures():
			progress=progress+1
			outFeat.setGeometry(inFeat.geometry() )
			outFeat.setAttributes(inFeat.attributes() )
			writer.addFeature( outFeat )
			self.LoadProgressBar.setValue(progress)
		del writer
		newlayer = QgsVectorLayer(outputFilename, os.path.basename(outputFilename), "ogr")
		#QgsMapLayerRegistry.instance().addMapLayer(newlayer)
		QgsProject.instance().addMapLayer(newlayer)
		self.active_layer=newlayer
		self.active_layer=QgsVectorLayer(self.OutlEdt.text(), self.active_layer.name(), "ogr") ##TODO check
		self.toolBox.setEnabled(True)
		######build tables###############
		self.EnvGetWeightBtn.setEnabled(True)
		envFields =  [str(self.listEnvFields.item(i).text()) for i in range(self.listEnvFields.count())]
		self.buildTables(self.EnvWeighTableWidget,envFields)
		self.updateGUIIdealPointFctn(self.EnvWeighTableWidget,provider)
		
		self.EcoGetWeightBtn.setEnabled(True)
		ecoFields =[str(self.listEcoFields.item(i).text()) for i in range(self.listEcoFields.count())]
		self.buildTables(self.EcoWeighTableWidget,ecoFields)
		self.updateGUIIdealPointFctn(self.EcoWeighTableWidget,provider)
		
		self.SocGetWeightBtn.setEnabled(True)
		socFields =[str(self.listSocFields.item(i).text()) for i in range(self.listSocFields.count())]
		self.buildTables(self.SocWeighTableWidget,socFields)
		self.updateGUIIdealPointFctn(self.SocWeighTableWidget,provider)
		self.readSettingFile(self.EnvWeighTableWidget,envFields) #load setting data stored in setting.csv
		self.readSettingFile(self.EcoWeighTableWidget,ecoFields) #load setting data stored in setting.csv
		self.readSettingFile(self.SocWeighTableWidget,socFields) #load setting data stored in setting.csv
		return 0
		

	def buildTables(self,weighTableWidget,fields):
		"""base function for updateTable()"""
		Envfields=self.getFieldNames(self.active_layer) #field list
		setLabel=["Label","Weigths","Preference","Ideal point", "Worst point "]
		weighTableWidget.setColumnCount(len(fields))
		weighTableWidget.setHorizontalHeaderLabels(fields)
		weighTableWidget.setRowCount(5)
		weighTableWidget.setVerticalHeaderLabels(setLabel)
		for r in range(len(fields)):
			weighTableWidget.setItem(0,r,QTableWidgetItem("-"))
			weighTableWidget.setItem(1,r,QTableWidgetItem("1.0"))
			weighTableWidget.setItem(2,r,QTableWidgetItem("gain"))
		
		#retrieve signal for modified cells
		try:
			weighTableWidget.cellClicked[(int,int)].connect(self.changeValue)
		except:
			pass
		
	def readSettingFile(self,WeighTableWidget,fields):
		pathSource = (os.path.dirname(str(self.base_Layer.source())))
		print("reading setting file")
		try:
			if (os.path.exists(os.path.join(pathSource,"setting.csv"))==True):
				setting=[i.strip().split(';') for i in open(os.path.join(pathSource,"setting.csv")).readlines()]
				for i in range(len(fields)):
					for l in range(len(setting[1])):
						if fields[i]==setting[1][l]:
							WeighTableWidget.horizontalHeaderItem(i).setToolTip((str(setting[0][l])))
							WeighTableWidget.setItem(0,i,QTableWidgetItem(str(setting[0][l])))
							WeighTableWidget.setItem(1,i,QTableWidgetItem(str(setting[2][l])))
							WeighTableWidget.setItem(2,i,QTableWidgetItem(str(setting[3][l])))
							WeighTableWidget.setItem(3,i,QTableWidgetItem(str(setting[4][l])))
							WeighTableWidget.setItem(4,i,QTableWidgetItem(str(setting[5][l])))
		except:
				QgsMessageLog.logMessage("Problem in reading setting file","SSAM")
				#self.fillTableFctn(fields,WeighTableWidget)
		return 0
				

	def updateGUIIdealPointFctn(self,WeighTableWidget,provider):
		"""base function for updateGUIIdealPoint()"""
		criteria=[WeighTableWidget.horizontalHeaderItem(f).text() for f in range(WeighTableWidget.columnCount())]
		preference=[str(WeighTableWidget.item(2, c).text()) for c in range(WeighTableWidget.columnCount())]
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		minField=[provider.minimumValue( f ) for f in fids]
		maxField=[provider.maximumValue( f ) for f in fids]
		for r in range(len(preference)):
			if preference[r]=='gain':
				WeighTableWidget.setItem(3,r,QTableWidgetItem(str(maxField[r])))#ideal point
				WeighTableWidget.setItem(4,r,QTableWidgetItem(str(minField[r])))#worst point
			elif preference[r]=='cost':
				WeighTableWidget.setItem(3,r,QTableWidgetItem(str(minField[r])))
				WeighTableWidget.setItem(4,r,QTableWidgetItem(str(maxField[r])))
			else:
				WeighTableWidget.setItem(3,r,QTableWidgetItem("0"))
				WeighTableWidget.setItem(4,r,QTableWidgetItem("0"))
	


	def changeValue(self):
		"""Event for change gain/cost"""
		if self.toolBox.currentIndex()==1:
			cell=self.EnvWeighTableWidget.currentItem()
			r=cell.row()
			c=cell.column()
			first=self.EnvWeighTableWidget.item(3, c).text()
			second=self.EnvWeighTableWidget.item(4, c).text()
			if cell.row()==2:
				val=cell.text()
				if val=="cost":
					self.EnvWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("gain"))
				elif val=="gain":
					self.EnvWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("cost"))
				else:
					self.EnvWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem(str(val)))
				self.EnvWeighTableWidget.setItem(3,c, QTableWidgetItem(second))
				self.EnvWeighTableWidget.setItem(4,c, QTableWidgetItem(first))
		elif self.toolBox.currentIndex()==2:
			cell=self.EcoWeighTableWidget.currentItem()
			r=cell.row()
			c=cell.column()
			first=self.EcoWeighTableWidget.item(3, c).text()
			second=self.EcoWeighTableWidget.item(4, c).text()
			if cell.row()==2:
				val=cell.text()
				if val=="cost":
					self.EcoWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("gain"))
				elif val=="gain":
					self.EcoWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("cost"))
				else:
					self.EcoWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem(str(val)))
				self.EcoWeighTableWidget.setItem(3,c, QTableWidgetItem(second))
				self.EcoWeighTableWidget.setItem(4,c, QTableWidgetItem(first))
		elif self.toolBox.currentIndex()==3:
			cell=self.SocWeighTableWidget.currentItem()
			c=cell.column()
			first=self.SocWeighTableWidget.item(3, c).text()
			second=self.SocWeighTableWidget.item(4, c).text()
			if cell.row()==2:
				val=cell.text()
				if val=="cost":
					self.SocWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("gain"))
				elif val=="gain":
					self.SocWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem("cost"))
				else:
					self.SocWeighTableWidget.setItem(cell.row(),cell.column(),QTableWidgetItem(str(val)))
				self.SocWeighTableWidget.setItem(3,c, QTableWidgetItem(second))
				self.SocWeighTableWidget.setItem(4,c, QTableWidgetItem(first))
		else:
			pass
		
		
	def onSliderValueChanged(self, value):
		changed_slider = self.sender()
		changed_slider.float_value = float(value)/changed_slider.maximum()
		delta = sum(slider.float_value for slider in self.sliders)-1
		while abs(delta)>0.00001:
			d = len(self.sliders)-1
			for slider in self.sliders:
				if slider is changed_slider:
					continue
				old_value = slider.float_value
				slider.float_value = min(max(0, old_value-delta/d), 1)
				delta -= old_value-slider.float_value
				d -= 1
		self.updateSliderValues()
		
		
	def updateSliderValues(self):
		for slider in self.sliders:
			slider_signals_blocked = slider.blockSignals(True)
			slider.setValue(round(slider.float_value*slider.maximum()))
			slider.blockSignals(slider_signals_blocked)
			#slider.label.setText('{:.2f}'.format(slider.float_value))

		
	def setEnvSlider(self):
		envDelta=self.EnvSlider.maximum()-self.EnvSlider.value()
		ecoDelta=self.EcoSlider.maximum()-self.EcoSlider.value()
		socDelta=self.SocSlider.maximum()-self.SocSlider.value()
		if self.ecoCheckBox.isChecked():
			ecoMove=self.EcoSlider.value()
		else:
			ecoMove=float(ecoDelta)/float(ecoDelta+socDelta)*envDelta
		if self.socCheckBox.isChecked():
			socMove=self.SocSlider.value()
		else:
			socMove=float(socDelta)/float(ecoDelta+socDelta)*envDelta
		self.EcoSlider.setValue(ecoMove)
		self.SocSlider.setValue(socMove)
		
	def setEcoSlider(self):
		envDelta=self.EnvSlider.maximum()-self.EnvSlider.value()
		ecoDelta=self.EcoSlider.maximum()-self.EcoSlider.value()
		socDelta=self.SocSlider.maximum()-self.SocSlider.value()
		envMove=float(envDelta)/float(envDelta+socDelta)*ecoDelta
		socMove=float(socDelta)/float(envDelta+socDelta)*ecoDelta
		self.EnvSlider.setValue(envMove)
		self.SocSlider.setValue(socMove)
	
	def setSocSlider(self):
		envDelta=self.EnvSlider.maximum()-self.EnvSlider.value()
		ecoDelta=self.EcoSlider.maximum()-self.EcoSlider.value()
		socDelta=self.SocSlider.maximum()-self.SocSlider.value()
		ecoMove=float(ecoDelta)/float(ecoDelta+envDelta)*socDelta
		envMove=float(envDelta)/float(ecoDelta+envDelta)*socDelta
		self.EcoSlider.setValue(ecoMove)
		self.EnvSlider.setValue(envMove)
		
	def elaborate(self):
		self.standardizationIdealPoint()
		self.relativeCloseness()
		#self.OveralValue()
		self.saveCfg()
		#self.setModal(True)
		return 0
#############################################################################################################

	def addDecisionField(self,layer,Label):
		"""Add field on attribute table"""
		caps = layer.dataProvider().capabilities()
		if caps & QgsVectorDataProvider.AddAttributes:
			res = layer.dataProvider().addAttributes( [QgsField(Label, QVariant.Double,"",24,4,"")] )
		return 0


###########################################################################################
	def extractFieldSumSquare(self,field):
		"""Retrive single field value from attributes table"""
		provider=self.base_Layer.dataProvider()
		fid=provider.fieldNameIndex(field)
		listValue=[]
		for feat in self.base_Layer.getFeatures():
			attribute=feat.attributes()[fid]
			listValue.append(attribute)
		listValue=[pow(l,2) for l in listValue]
		return (sum(listValue)**(0.5))
	
	def standardizationIdealPoint(self):
		"""Perform STEP 1 and STEP 2 of TOPSIS algorithm"""
		if self.toolBox.currentIndex()==1:
			criteria=[self.EnvWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.EnvWeighTableWidget.columnCount())]
			weight=[float(self.EnvWeighTableWidget.item(1, c).text()) for c in range(self.EnvWeighTableWidget.columnCount())]
			weight=[ round(w/sum(weight),4) for w in weight ]
			for c,w in zip(range(len(criteria)),weight):
				self.EnvWeighTableWidget.setItem(1,c,QTableWidgetItem(str(w))) 
			self.EnvGetWeightBtn.setEnabled(False)
		elif self.toolBox.currentIndex()==2:
			criteria=[self.EcoWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.EcoWeighTableWidget.columnCount())]
			weight=[float(self.EcoWeighTableWidget.item(1, c).text()) for c in range(self.EcoWeighTableWidget.columnCount())]
			weight=[ round(w/sum(weight),4) for w in weight ]
			for c,w in zip(range(len(criteria)),weight):
				self.EcoWeighTableWidget.setItem(1,c,QTableWidgetItem(str(w))) 
			self.EcoGetWeightBtn.setEnabled(False)
		elif self.toolBox.currentIndex()==3:
			criteria=[self.SocWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.SocWeighTableWidget.columnCount())]
			weight=[float(self.SocWeighTableWidget.item(1, c).text()) for c in range(self.SocWeighTableWidget.columnCount())]
			weight=[ round(w/sum(weight),4) for w in weight ]
			for c,w in zip(range(len(criteria)),weight):
				self.SocWeighTableWidget.setItem(1,c,QTableWidgetItem(str(w))) 
			self.SocGetWeightBtn.setEnabled(False)
		else:
			pass
		provider=self.active_layer.dataProvider()
		feat = QgsFeature()
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		#self.EnvTEdit.append(str(dict(zip(fids,[(field) for field in criteria]))))
		sumSquareColumn=dict(zip(fids,[self.extractFieldSumSquare(field) for field in criteria]))
		#provider.select(fids)
		self.active_layer.startEditing()
		for f,w in zip(fids,weight): #N.B. verifica corretto allineamento con i pesi
			for feat in self.active_layer.getFeatures():
				attributes=feat.attributes()[f]
				value=(float(attributes)/float(sumSquareColumn[f]))*w   # TOPSIS algorithm: STEP 1 and STEP 2
				#print sumSquareColumn[f]
				self.active_layer.changeAttributeValue(feat.id(),f,round(value,4))
		self.active_layer.commitChanges()
		return 0
		
			
	def relativeCloseness(self):
		""" Calculate Environmental and Socio-Economicos distance from ideal point"""
		if self.toolBox.currentIndex()==1:
			criteria=[self.EnvWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.EnvWeighTableWidget.columnCount())]
			weight=[float(self.EnvWeighTableWidget.item(1, c).text()) for c in range(self.EnvWeighTableWidget.columnCount())]
			idealPoint=[float(self.EnvWeighTableWidget.item(3, c).text()) for c in range(self.EnvWeighTableWidget.columnCount())]
			sumSquareColumnList=[self.extractFieldSumSquare(field) for field in criteria]
			idealPoint=[float(self.EnvWeighTableWidget.item(3, c).text())/sumSquareColumnList[c]*weight[c] \
				for c in range(self.EnvWeighTableWidget.columnCount())]
			worstPoint=[float(self.EnvWeighTableWidget.item(4, c).text())/sumSquareColumnList[c]*weight[c] \
				for c in range(self.EnvWeighTableWidget.columnCount())]
			provider=self.active_layer.dataProvider()
			if provider.fieldNameIndex("EnvIdeal")==-1:
				self.addDecisionField(self.active_layer,"EnvIdeal")
			fldValue = provider.fieldNameIndex("EnvIdeal") #obtain classify field index from its name
			self.EnvTEdit.append("done") #   setText
		elif self.toolBox.currentIndex()==2:
			criteria=[self.EcoWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.EcoWeighTableWidget.columnCount())]
			weight=[float(self.EcoWeighTableWidget.item(1, c).text()) for c in range(self.EcoWeighTableWidget.columnCount())]
			sumSquareColumnList=[self.extractFieldSumSquare(field) for field in criteria]
			idealPoint=[float(self.EcoWeighTableWidget.item(3, c).text())/sumSquareColumnList[c]*weight[c] \
				for c in range(self.EcoWeighTableWidget.columnCount())]
			worstPoint=[float(self.EcoWeighTableWidget.item(4, c).text())/sumSquareColumnList[c]*weight[c] \
				for c in range(self.EcoWeighTableWidget.columnCount())]
			provider=self.active_layer.dataProvider()
			if provider.fieldNameIndex("EcoIdeal")==-1:
				self.addDecisionField(self.active_layer,"EcoIdeal")
			fldValue = provider.fieldNameIndex("EcoIdeal") #obtain classify field index from its name
			self.EcoTEdit.append("done")
		elif self.toolBox.currentIndex()==3:
			criteria=[self.SocWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.SocWeighTableWidget.columnCount())]
			weight=[float(self.SocWeighTableWidget.item(1, c).text()) for c in range(self.SocWeighTableWidget.columnCount())]
			sumSquareColumnList=[self.extractFieldSumSquare(field) for field in criteria]
			idealPoint=[float(self.SocWeighTableWidget.item(3, c).text())/sumSquareColumnList[c]*weight[c]\
				for c in range(self.SocWeighTableWidget.columnCount())]
			worstPoint=[float(self.SocWeighTableWidget.item(4, c).text())/sumSquareColumnList[c]*weight[c] \
				for c in range(self.SocWeighTableWidget.columnCount())]
			provider=self.active_layer.dataProvider()
			if provider.fieldNameIndex("SocIdeal")==-1:
				self.addDecisionField(self.active_layer,"SocIdeal")
			fldValue = provider.fieldNameIndex("SocIdeal") #obtain classify field index from its name
			self.SocTEdit.append("done")
		else:
			pass
		#self.EnvTEdit.append(str(idealPoint)+"#"+str(worstPoint))
		features=provider.featureCount() #Number of features in the layer.
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its name
		self.active_layer.startEditing()
		self.EnvProgressBar.setRange(1,features)
		self.EcoProgressBar.setRange(1,features)
		self.SocProgressBar.setRange(1,features)
		progress=0
		for feat in self.active_layer.getFeatures():
			IP=WP=0
			for f,idp,wrp in zip(fids,idealPoint,worstPoint):
				progress=progress+1
				attributes = feat.attributes()
				IP =IP+(float(attributes[f]-idp)**2)   # TOPSIS algorithm: STEP 4
				WP =WP+(float(attributes[f]-wrp)**2)
			relativeCloseness=(WP**(0.5))/((WP**(0.5))+(IP**(0.5)))
			self.active_layer.changeAttributeValue(feat.id(), fldValue, round(float(relativeCloseness),4))
			self.EnvProgressBar.setValue(progress)
			self.EcoProgressBar.setValue(progress)
			self.SocProgressBar.setValue(progress)
		self.active_layer.commitChanges()
		self.EnvProgressBar.setValue(1)
		self.EcoProgressBar.setValue(1)
		self.SocProgressBar.setValue(1)
		return 0

		
		
	def overalValue(self):
		"""Sum Environmental and Socio-economics value for calculate  Sustainable value"""
		weight=[self.EnvSlider.value(),self.EcoSlider.value(),self.SocSlider.value()]
		provider=self.active_layer.dataProvider()
		if provider.fieldNameIndex("SustIdeal")==-1:
			self.addDecisionField(self.active_layer,"SustIdeal")
		fldValue = provider.fieldNameIndex("SustIdeal") #obtain classify field index from its name
		fids=[provider.fieldNameIndex(c) for c in ['EnvIdeal','EcoIdeal','SocIdeal']]
		if -1 not in fids:
			self.active_layer.startEditing()
			for feat in self.active_layer.getFeatures():
				attributes=feat.attributes()
				#self.EnvTEdit.append(str(fids)+"-"+str([(attributes[att]) for att in fids]))
				value=sum([float(str(attributes[att]))*w for att,w in zip(fids,weight)])
				#print [attributes[att] for att in fids], [w for w in weight], value
				self.active_layer.changeAttributeValue(feat.id(), fldValue, round(float(value),4))
			self.active_layer.commitChanges()
			
			#self.LabelCartogramCBox.addItems(self.getFieldNames(self.active_layer)) #numeric fields
			
			self.pushBtnEval.setEnabled(False)
			self.toolBox.setItemEnabled(5,True) #activate last toolbox
			self.symbolize('SustIdeal')
			return 0
		else:
			return -1
		


###########################################################################################

	def symbolize(self,field):
		"""Prepare legends for environmental, socio economics and sustainable values"""
		numberOfClasses=self.spinBoxClasNum.value()
		if(numberOfClasses==5):
			classes=['very low', 'low','medium','high','very high']
		else:
			classes=range(1,numberOfClasses+1)
		fieldName = field
		layer=self.active_layer
		fieldIndex = layer.fields().indexFromName(fieldName)
		provider = layer.dataProvider()
		minimum = provider.minimumValue( fieldIndex )
		maximum = provider.maximumValue( fieldIndex )
		string="%s,%s,%s" %(minimum,maximum,layer.name() )
		#self.SocTEdit.append(string)
		RangeList = []
		Opacity = 1
		for c,i in zip(classes,range(len(classes))):
		# Crea il simbolo ed il range...
			Min = round(minimum + (( maximum - minimum ) / numberOfClasses * i),4)
			Max = round(minimum + (( maximum - minimum ) / numberOfClasses * ( i + 1 )),4)
			Label = "%s [%.2f - %.2f]" % (c,Min,Max)
			if field=='SustIdeal':
				Colour = QColor((255-85*i/numberOfClasses),\
								(255-255*i/numberOfClasses),\
								(127-127*i/numberOfClasses)) #red to green
			elif field=='EnvIdeal':
				Colour = QColor((255-255*i/numberOfClasses),\
								(255-170*i/numberOfClasses),\
								(127-127*i/numberOfClasses)) #yellow to green
			elif field=='EcoIdeal':
				Colour = QColor(255,255-255*i/numberOfClasses,0) #yellow to red
			elif field=='SocIdeal':
				Colour = QColor((255-255*i/numberOfClasses),\
								(255-85*i/numberOfClasses),\
								(127+128*i/numberOfClasses)) #yellow to cyan 255,255,127
			Symbol = QgsSymbol.defaultSymbol(layer.geometryType())
			Symbol.setColor(Colour)
			Symbol.setOpacity(Opacity)
			Range = QgsRendererRange(Min,Max,Symbol,Label)
			RangeList.append(Range)
		Renderer = QgsGraduatedSymbolRenderer('', RangeList)
		Renderer.setMode(QgsGraduatedSymbolRenderer.EqualInterval)
		Renderer.setClassAttribute(fieldName)
		add=QgsVectorLayer(layer.source(),field,'ogr')
		add.setRenderer(Renderer)
		QgsProject.instance().addMapLayer(add)

	def renderLayer(self):
		""" Load thematic layers in canvas """
		#self.setModal(False)
		layer = self.active_layer
		fields=['EnvIdeal','EcoIdeal','SocIdeal']
		for f in fields:
			self.symbolize(f)
		

###########################################################################################
	def refreshLayer(self):
		self.active_layer.setCacheImage( None )
		self.active_layer.triggerRepaint()
		self.EnvTEdit.append("refresced")
		
		
	def createMemoryLayer(self,layer):
		"""Create an in-memory copy of an existing vector layer."""
		data_provider = layer.dataProvider()

		# create the layer path defining geometry type and reference system
		#geometry_type = QGis.vectorGeometryType(layer.geometryType())
		geometry_type = QgsWkbTypes.geometryDisplayString(layer.geometryType())
		crs_id = layer.crs().authid()
		path = geometry_type + '?crs=' + crs_id + '&index=yes'

		# create the memory layer and get a reference to the data provider
		memory_layer = QgsVectorLayer(path, 'Cartogram', 'memory')
		memory_layer_data_provider = memory_layer.dataProvider()

		# copy all attributes from the source layer to the memory layer
		memory_layer.startEditing()
		memory_layer_data_provider.addAttributes(
			data_provider.fields().toList())
		memory_layer.commitChanges()

		# copy all features from the source layer to the memory layer
		for feature in data_provider.getFeatures():
			memory_layer_data_provider.addFeatures([feature])

		return memory_layer
		
		
	def extractAttributeValue(self,field):
		"""Retrive single field value from attributes table"""
		fields=self.active_layer.fields()
		provider=self.active_layer.dataProvider()
		fid=provider.fieldNameIndex(field)
		listValue=[]
		if fields[fid].typeName()=='Real' or fields[fid].typeName()=='Integer':
			for feat in self.active_layer.getFeatures():
				attribute=feat.attributes()[fid]
				listValue.append(float(attribute))
		else:
			for feat in self.active_layer.getFeatures():
				attribute=feat.attributes()[fid]
				listValue.append(str(attribute))
		return listValue

	def buildOutput(self):
		"""General function for all graphical and tabula output"""
		currentDir = unicode(os.path.abspath( os.path.dirname(__file__)))
		self.exportTable()
		if os.path.isfile(os.path.join(currentDir,"points.png"))==True:
			os.remove(os.path.join(currentDir,"points.png"))
		if os.path.isfile(os.path.join(currentDir,"histogram.png"))==True:
			os.remove(os.path.join(currentDir,"histogram.png"))
		self.buildHTML()
		webbrowser.open(os.path.join(currentDir,"barGraph.html"))
		#self.setModal(False)
		return 0

	def renderCartogram(self):
		layer=self.createMemoryLayer(self.active_layer)
		input_field=self.LabelCartogramCBox.currentText()
		iterations=5
		Cartogram=CartogramWorker(layer, input_field, iterations)
		Cartogram.run()
		if layer is not None:
			QgsProject.instance().addMapLayer(layer)
		else:
			"None!"
		#export2JSON(layer)


		
	def buildHTML(self):
		EnvValue=self.extractAttributeValue('EnvIdeal')
		EcoValue=self.extractAttributeValue('EcoIdeal')
		SocValue=self.extractAttributeValue('SocIdeal')
		SustValue=self.extractAttributeValue('SustIdeal')
		#SuitValue=[x+y+z for (x,y,z) in zip(EnvValue,EcoValue,SocValue)]
		label=self.LabelListFieldsCBox.currentText()
		labels=self.extractAttributeValue(label)
		labels=[str(l) for l in labels]
		htmlGraph.BuilHTMLGraph(SustValue,EnvValue,EcoValue,SocValue,labels)
		return 0
		
	def exportTable(self):
		try:
			criteria=[self.EnvWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.EnvWeighTableWidget.columnCount())]
			currentDIR = (os.path.dirname(str(self.base_Layer.source())))
			bLayer=self.base_Layer
			field_names = [field.name() for field in bLayer.fields()]+['EnvIdeal','EcoIdeal','SocIdeal','SustIdeal']
			EnvValue=self.extractAttributeValue('EnvIdeal')
			EcoValue=self.extractAttributeValue('EcoIdeal')
			SocValue=self.extractAttributeValue('SocIdeal')
			SustValue=self.extractAttributeValue('SustIdeal')
			att2csv=[]
			for feature,env,eco,soc in zip(bLayer.getFeatures(),EnvValue,EcoValue,SocValue):
				row=feature.attributes()+[env,eco,soc]
				att2csv.append(row)
			with open(os.path.join(currentDIR,'attributes.csv'), 'wb') as csvfile:
				spamwriter = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
				spamwriter.writerow(field_names)
				spamwriter.writerows(att2csv)
			return 0
		except:
			QgsMessageLog.logMessage("Problem in writing export table file","SSAM")
		
###################################################################################################
	def saveCfg(self):
		currentDIR = (os.path.dirname(str(self.base_Layer.source())))
		setting=(os.path.join(currentDIR,"setting.csv"))
		fileCfg = open(os.path.join(currentDIR,"setting.csv"),"w")
		envLabel=[(self.EnvWeighTableWidget.item(0, c).text()) for c in range(self.EnvWeighTableWidget.columnCount())]
		ecoLabel=[(self.EcoWeighTableWidget.item(0, c).text()) for c in range(self.EcoWeighTableWidget.columnCount())]
		socLabel=[(self.SocWeighTableWidget.item(0, c).text()) for c in range(self.SocWeighTableWidget.columnCount())]
		label=envLabel+ecoLabel+socLabel
		print(label)
		criteria,preference,weight,ideal,worst=self.usedCriteria()
		for l in label:
			fileCfg.write(str(l)+";")
		fileCfg.write("\n")
		for c in criteria:
			fileCfg.write(str(c)+";")
		fileCfg.write("\n")
		fileCfg.write(";".join(weight))
		fileCfg.write("\n")
		for p in preference:
			fileCfg.write(str(p)+";")
		fileCfg.write("\n")
		fileCfg.write(";".join(ideal))
		fileCfg.write("\n")
		fileCfg.write(";".join(worst))
		fileCfg.close()

		
	def about(self):
		"""    Visualize an About window."""
		QMessageBox.about(self, "About geoSustainability",
		"""
			<p>SSAM Spatial Sustainability Assessment Model<br />2019-05-10<br />License: GPL v. 3</p>
			<hr>
			<p>Universita' degli Studi di Perugia - Dipartimento di scienze agrarie, alimentari e ambientali <a href="http://www.unipg.it">www.unipg.it</a></p>
			<p>ARPA Umbria - Agenzia Regionale per la Protezione Ambientale <a href="http://www.arpa.umbria.it">www.arpa.umbria.it</a></p>
			<hr>
			<p>Documents, data and tutorial: <a href="http://maplab.alwaysdata.net/SSAM.html">maplab.alwaysdata.net</a></p>
			<p>Please report any bug to <a href="mailto:g_massa@libero.it">g_massa@libero.it</a></p>
		""")



	def open_help(self):
		currentDir = unicode(os.path.abspath( os.path.dirname(__file__)))
		webbrowser.open(os.path.join(currentDir,"data.html"))
		webbrowser.open("http://maplab.alwaysdata.net/SSAM.html")

###################################################################################################

	def discretizeDecision(self,value,listClass,numberOfClasses):
		DiscValue=-1
		for o,t in zip(range(numberOfClasses),range(1,numberOfClasses+1)) :
			if ((float(value)>=float(listClass[o])) and (float(value)<=float(listClass[t]))):
				DiscValue=o+1
		return DiscValue
	
			
	def addDiscretizedField(self):
		"""add new field"""
		field="SustIdeal"
		numberOfClasses=5
		provider=self.base_Layer.dataProvider()
		#provider=self.active_layer.dataProvider()
		if provider.fieldNameIndex("Classified")==-1:
			self.addDecisionField(self.base_Layer,"Classified")
		fidClass = provider.fieldNameIndex("Classified") #obtain classify field index from its name
		listInput=self.extractAttributeValue(field)
		widthOfClass=float((max(listInput))-float(min(listInput)))/float(numberOfClasses)
		listClass=[(min(listInput)+(widthOfClass)*i) for i in range(numberOfClasses+1)]
		#self.EnvTEdit.setText(str(listClass))
		self.base_Layer.startEditing()
		decision=[]
		for feat in self.base_Layer.getFeatures():
			DiscValue=self.discretizeDecision(listInput[int(feat.id())],listClass,numberOfClasses)
			self.base_Layer.changeAttributeValue(feat.id(), fidClass, float(DiscValue))
			decision.append(DiscValue)
		self.base_Layer.commitChanges()
		return list(set(decision))

	def usedCriteria(self):
		criteria=[self.EnvWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.EnvWeighTableWidget.columnCount())] + \
			[self.EcoWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.EcoWeighTableWidget.columnCount())] + \
			[self.SocWeighTableWidget.horizontalHeaderItem(f).text() for f in range(self.SocWeighTableWidget.columnCount())]
		weight=[str(self.EnvWeighTableWidget.item(1, c).text()) for c in range(self.EnvWeighTableWidget.columnCount())] +\
			[str(self.EcoWeighTableWidget.item(1, c).text()) for c in range(self.EcoWeighTableWidget.columnCount())] + \
			[str(self.SocWeighTableWidget.item(1, c).text()) for c in range(self.SocWeighTableWidget.columnCount())]
		preference=[str(self.EnvWeighTableWidget.item(2, c).text()) for c in range(self.EnvWeighTableWidget.columnCount())] +\
			[str(self.EcoWeighTableWidget.item(2, c).text()) for c in range(self.EcoWeighTableWidget.columnCount())] + \
			[str(self.SocWeighTableWidget.item(2, c).text()) for c in range(self.SocWeighTableWidget.columnCount())] 
		ideal=[str(self.EnvWeighTableWidget.item(3, c).text()) for c in range(self.EnvWeighTableWidget.columnCount())] +\
			[str(self.EcoWeighTableWidget.item(3, c).text()) for c in range(self.EcoWeighTableWidget.columnCount())] + \
			[str(self.SocWeighTableWidget.item(3, c).text()) for c in range(self.SocWeighTableWidget.columnCount())] 
		worst=[str(self.EnvWeighTableWidget.item(4, c).text()) for c in range(self.EnvWeighTableWidget.columnCount())] +\
			[str(self.EcoWeighTableWidget.item(4, c).text()) for c in range(self.EcoWeighTableWidget.columnCount())] + \
			[str(self.SocWeighTableWidget.item(4, c).text()) for c in range(self.SocWeighTableWidget.columnCount())] 
		return criteria, preference,weight,ideal,worst
		
	def writeISFfile(self,decision):
		currentDIR = (os.path.dirname(str(self.base_Layer.source())))
		out_file = open(os.path.join(currentDIR,"example.isf"),"w")
		criteria,preference,weight,ideal,worst=self.usedCriteria()
		criteria.append("Classified")
		preference.append("gain")
		#decision=list(set(self.extractAttributeValue("Classified")))
		decision=[int(i) for i in decision]
		out_file.write("**ATTRIBUTES\n") 
		for c in (criteria):
			if(str(c)=="Classified"):
				out_file.write("+ Classified: %s\n"  % (decision))
			else:
				out_file.write("+ %s: (continuous)\n"  % (c))
		out_file.write("decision: Classified")
		out_file.write("\n\n**PREFERENCES\n")
		for c,p in zip(criteria,preference):
			out_file.write("%s: %s\n"  % (c,p))
		out_file.write("\n**EXAMPLES\n")
		provider=self.base_Layer.dataProvider()
		fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its names
		for feat in self.base_Layer.getFeatures():
			attribute = [feat.attributes()[j] for j in fids]
			for i in (attribute):
				out_file.write(" %s " % (i))
			out_file.write("\n")
		out_file.write("\n**END")
		out_file.close()
		return 0


	def showRules(self):
		currentDIR = (os.path.dirname(str(self.base_Layer.source())))
		rules=open(os.path.join(currentDIR,"rules.rls"))
		R=rules.readlines()
		self.RulesListWidget.clear()
		for E in R:
			self.RulesListWidget.addItem(E)
		#self.RulesListWidget.itemClicked.connect(self.selectFeatures)
		rules.close()
		return 0

	def queryByRule(self,R):
		"""perform query based on extracted rules"""
		E=R[0]
		exp="%s %s %s" % (E['label'],E['sign'],E['condition'])
		if len(R)>1:
			for F in R[1:]:
				exp=exp + " AND %s %s %s" % (F['label'],F['sign'],F['condition'])
		return exp


	def extractFeaturesByExp(self,layer,exp):
		exp = QgsExpression(exp)
		it=layer.getFeatures(QgsFeatureRequest(exp))
		listOfResults=[i.id() for i in it]
		print(it,exp)
		return listOfResults


	def selectFeatures(self):
		"""select feature in attribute table based on rules"""
		layer= self.iface.activeLayer()
		#currentDIR = QgsProject.instance().readPath("./")
		currentDIR = (os.path.dirname(str(self.base_Layer.source())))		
		rulesPKL = open(os.path.join(currentDIR,"RULES.pkl"), 'rb')
		RULES=pickle.load(rulesPKL) #save RULES dict in a file for use it in geoRULES module
		rulesPKL.close()
		selectedRule=self.RulesListWidget.currentItem().text()
		selectedRule=int(selectedRule.split(":")[0])
		R=RULES[selectedRule-1]
		exp=self.queryByRule(R)
		idSel=self.extractFeaturesByExp(layer,exp)
		layer.selectByIds(idSel)
		return 0
		


	def extractRules(self):
		pathSource=os.path.dirname(str(self.iface.activeLayer().source()))
		decision=self.addDiscretizedField()
		self.writeISFfile(decision)
		DOMLEM.main(pathSource)
		self.showRules()
		#self.setModal(False)
		return 0
		
	def saveRules(self):
		currentDIR = (os.path.dirname(str(self.base_Layer.source())))
		rules=(os.path.join(currentDIR,"rules.rls"))
		#filename = QFileDialog.getSaveFileName(self, 'Save File', os.getenv('HOME'),".rls")
		filename = QFileDialog.getSaveFileName(self, 'Save File', ".rls") 
		print (filename[0],filename)
		shutil.copy2(rules, filename[0])
		return 0

	def openFile(self):
		filename = QFileDialog.getOpenFileName(self, 'Open File', os.getenv('HOME')) 
		f = open(filename, 'r') 
		filedata = f.read() 
		self.text.setText(filedata) 
		f.close()

