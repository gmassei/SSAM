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
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

from qgis.core import *
from qgis.gui import *


#from qgis.core import QgsMapLayer
# Initialize Qt resources from file resources.py
#from . import resources
import os
import sys
import webbrowser
import csv
import pickle
from itertools import chain

import numpy as np

from . import DOMLEM
from . import htmlGraph


class SSAMAnlisys(QWidget):
    """ Implement all Analysis option """
    def __init__(self,activeLayer,parameterList):
        #QWidget.__init__(self)
        super().__init__()
        self.activeLayer=activeLayer
        self.parameterList=parameterList
        self.listField=[f.name() for f in self.activeLayer.fields()]
        self.currentDIR = (os.path.dirname(str(self.activeLayer.source())))
        self.initUI()
        self.showMap()
        
    def initUI(self):
        """ set gui widget """
        self.setGeometry(300, 300, 300, 200)
        #self.groupBox = QGroupBox("Sustainability charts")
        self.layout = QGridLayout()
        self.setLayout(self.layout)
        
        self.groupBoxCharts = QGroupBox("Charts")
        self.layoutCharts = QGridLayout()
        self.label = QLabel("Name")
        self.layoutCharts.addWidget(self.label,0,0)
        self.cmBoxField=QComboBox()
        self.cmBoxField.addItems(self.listField)
        self.layoutCharts.addWidget(self.cmBoxField,0,1)
        self.chartsBtn = QPushButton('Charts')
        self.chartsBtn.clicked.connect(self.dimensionCharts)
        self.layoutCharts.addWidget(self.chartsBtn,0,2)
        self.groupBoxCharts.setLayout(self.layoutCharts)
        self.layout.addWidget(self.groupBoxCharts,0,0,1,2)

        self.groupBoxSustainability = QGroupBox("Sustainability")
        self.layoutSust = QGridLayout()
        self.sliders=[]
        i=1
        for parameters in self.parameterList:
            self.label = QLabel(str(parameters['dimension']))
            self.layoutSust.addWidget(self.label,i,0)
            self.slider=QSlider()
            self.slider.setProperty("value", 0)
            self.slider.setOrientation(Qt.Horizontal)
            #self.slider.setMinimum(1)
            #self.slider.setMinimum(100)
            self.slider.setSingleStep(25)
            self.slider.setSliderPosition(99)
            self.slider.setObjectName(parameters['dimension'])
            self.slider.valueChanged.connect(self.onSliderValueChanged)
            self.layoutSust.addWidget(self.slider,i,1)
            self.sliders.append(self.slider)
            self.layoutSust.addWidget(self.slider,i,1)
            self.valueLbl=QLabel()
            self.layoutSust.addWidget(self.valueLbl,i,2)
            i+=1
        
        self.overAllBtn=QPushButton('Overall assesment')
        self.overAllBtn.clicked.connect(self.runSustainability)
        self.layoutSust.addWidget(self.overAllBtn,i,0,1,2)
        self.groupBoxSustainability.setLayout(self.layoutSust)
        self.layout.addWidget(self.groupBoxSustainability,1,0,1,2)
        
        self.groupRules=QGroupBox("Rules")
        self.layoutRules = QGridLayout()
        
        self.RulesListWidget=QListWidget()
        self.extractRulesBtn=QPushButton('Extract rules')
        self.layoutRules.addWidget(self.extractRulesBtn,0,0,1,2)
        self.extractRulesBtn.clicked.connect(self.showRules)
        self.extractRulesBtn.setEnabled(False)
        
        self.layoutRules.addWidget(self.RulesListWidget,1,0,1,2)
        self.groupRules.setLayout(self.layoutRules) 
        self.layout.addWidget(self.groupRules,2,0,1,2)
        
        
    def onSliderValueChanged(self):
        value = str(self.slider.value())
        self.valueLbl.setText(value)
    
    def buildDataForCharts(self):
        labeField=self.cmBoxField.currentText()
        idxLabel=self.activeLayer.fields().indexFromName(labeField)
        labels=[f.attributes()[idxLabel] for f in self.activeLayer.getFeatures()]
        data=[]
        data.append(labels)
        for parameters in self.parameterList:
            idxs=self.activeLayer.fields().indexFromName(parameters['dimension'])
            #idxs = [self.activeLayer.fields().indexFromName(fName) for fName in  parameters['dimension']]
            feat = self.activeLayer.getFeatures()
            atts=[f.attributes()[idxs] for f in feat]
            data.append(atts)
        dimension=['Label']+[parameters['dimension'] for parameters in self.parameterList]
        result = [[data[j][i] for j in range(len(data))] for i in range(len(data[0]))]
        return dimension,result
        
    def dimensionCharts(self):
        dimension,result=self.buildDataForCharts()
        htmlGraph.HTMLCharts(result,dimension)
        pluginDir = os.path.abspath( os.path.dirname(__file__))
        webbrowser.open(os.path.join(pluginDir,"barGraph.html"))
        
        
    def showMap(self):
        cMAP=ChoroplethMAP(self.activeLayer,self.parameterList)
        cMAP.renderLayer()
        
    def runSustainability(self):
        self.sustainability=Sustainability(self.activeLayer,self.parameterList,self.sliders)
        self.sustainability.overallValue()
        self.extractRulesBtn.setEnabled(True)
        dimension,result=self.buildDataForCharts()
        #htmlGraph.plotlyCharts(result,dimension)
        
        
    def showRules(self):
        self.turnOfLayers()
        currentDIR = (os.path.dirname(str(self.activeLayer.source())))
        rules=open(os.path.join(currentDIR,"rules.rls"))
        R=rules.readlines()
        self.RulesListWidget.clear()
        for E in R:
            self.RulesListWidget.addItem(E)
        self.RulesListWidget.itemClicked.connect(self.selectFeatures)
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
        return listOfResults


    def selectFeatures(self):
        """select feature in attribute table based on rules"""
        currentDIR = (os.path.dirname(str(self.activeLayer.source())))        
        rulesPKL = open(os.path.join(currentDIR,"RULES.pkl"), 'rb')
        RULES=pickle.load(rulesPKL) #save RULES dict in a file for use it in geoRULES module
        rulesPKL.close()
        selectedRule=self.RulesListWidget.currentItem().text()
        selectedRule=int(selectedRule.split(":")[0])
        R=RULES[selectedRule-1]
        exp=self.queryByRule(R)
        idSel=self.extractFeaturesByExp(self.activeLayer,exp)
        self.activeLayer.selectByIds(idSel)
        return 0
    
    def turnOfLayers(self):
        layers=[layer for layer in QgsProject.instance().mapLayers().values()]
        for lyr in layers:
            node = QgsProject.instance().layerTreeRoot().findLayer(lyr.id())
            if node:
                if lyr.name()!=self.activeLayer.name():
                    node.setItemVisibilityChecked(False)
                else:
                    node.setItemVisibilityChecked(True)




class Sustainability:
    def __init__(self,activeLayer,parameterList,sliders):
        self.activeLayer=activeLayer
        self.parameterList=parameterList
        self.sliders=sliders
    
    def extractDimension(self):
        labeField=self.cmBoxField.currentText()
        for parameters in self.parameterList:
            idxs=self.activeLayer.fields().indexFromName(parameters['dimension'])
            feat = self.activeLayer.getFeatures()
            atts=[f.attributes()[idxs] for f in feat]
            print(parameters['dimension'],idxs,atts)
            
    def overallValue(self):
        for s,p in zip(self.sliders,self.parameterList):
            print("{},{},{}",s.value(),s.objectName(),p['dimension'])
        dimension=[p['dimension'] for p in self.parameterList]
        sliderWeight=[s.value() for s in self.sliders]
        provider = self.activeLayer.dataProvider()
        if provider.fieldNameIndex('Sustainability')==-1:
            self.activeLayer.dataProvider().addAttributes([QgsField('Sustainability', QVariant.Double,"",24,4,"")] )
			#edit is a shortcut that replaces layer.beginEditCommand and layer.endEditCommand
        with edit(self.activeLayer):
            for f in self.activeLayer.getFeatures():
                row=[f[d] for d in dimension]
                wrow=[r*w for r,w in zip(row,sliderWeight)]
                f['Sustainability'] = sum(wrow) # f[self.parameters['criteria'][0]] + f[self.parameters['criteria'][1]]
                self.activeLayer.updateFeature(f)
        sMAP=ChoroplethMAP(self.activeLayer,self.parameterList)
        sMAP.symbolize('Sustainability')
        self.rules=RSDB(self.activeLayer,self.parameterList)
        self.rules.extractRules()


class RSDB:
    def __init__(self,activeLayer,parameterList):
        self.activeLayer=activeLayer
        self.parameterList=parameterList
        self.listField=[f.name() for f in self.activeLayer.fields()]
        self.currentDIR = (os.path.dirname(str(self.activeLayer.source())))

    def discretizeDecision(self,value,listClass,numberOfClasses):
        DiscValue=-1
        for o,t in zip(range(numberOfClasses),range(1,numberOfClasses+1)) :
            if ((float(value)>=float(listClass[o])) and (float(value)<=float(listClass[t]))):
                DiscValue=o+1
        return DiscValue
            
    def addDiscretizedField(self):
        """add new field"""
        field="Sustainability"
        numberOfClasses=5
        
        provider = self.activeLayer.dataProvider()
        if provider.fieldNameIndex('Classified')==-1:
            self.activeLayer.dataProvider().addAttributes([QgsField('Classified', QVariant.Double,"",24,4,"")] )
        fidClass = provider.fieldNameIndex("Classified") #obtain classify field index from its name

        idxs=self.activeLayer.fields().indexFromName(field)
        feat = self.activeLayer.getFeatures()
        listInput=[f.attributes()[idxs] for f in feat]        

        widthOfClass=float((max(listInput))-float(min(listInput)))/float(numberOfClasses)
        listClass=[(min(listInput)+(widthOfClass)*i) for i in range(numberOfClasses+1)]
        #self.EnvTEdit.setText(str(listClass))
        self.activeLayer.startEditing()
        decision=[]
        for feat in self.activeLayer.getFeatures():
            print("listInput:{} - feat.id():{}-{}".format(listInput,int(feat.id()),listInput[int(feat.id())-1]))
            DiscValue=self.discretizeDecision(listInput[int(feat.id()-1)],listClass,numberOfClasses)
            self.activeLayer.changeAttributeValue(feat.id(), fidClass, float(DiscValue))
            decision.append(DiscValue)
        self.activeLayer.commitChanges()
        return list(set(decision))
    
    

    def usedCriteria(self):
        #criteria=[parameters['criteria'] for parameters in self.parameterList]
        criteria = list(chain.from_iterable([parameters['criteria'] for parameters in self.parameterList])) 
        weights= list(chain.from_iterable([parameters['weights'] for parameters in self.parameterList]))
        preference= list(chain.from_iterable([parameters['preference'] for parameters in self.parameterList]))
        idealPoint= list(chain.from_iterable([parameters['idealPoint'] for parameters in self.parameterList]))
        worstPoint= list(chain.from_iterable([parameters['worstPoint'] for parameters in self.parameterList]))
        print(criteria,weights)
        return criteria, preference,weights,idealPoint,worstPoint
        
    def writeISFfile(self,decision):
        #currentDIR = (os.path.dirname(str(self.base_layer.source())))
        currentDIR = (os.path.dirname(str(self.activeLayer.source())))
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
        provider=self.activeLayer.dataProvider()
        fids=[provider.fieldNameIndex(c) for c in criteria]  #obtain array fields index from its names
        for feat in self.activeLayer.getFeatures():
            attribute = [feat.attributes()[j] for j in fids]
            for i in (attribute):
                out_file.write(" %s " % (i))
            out_file.write("\n")
        out_file.write("\n**END")
        out_file.close()
        return 0
        

    def extractRules(self):
        pathSource=os.path.dirname(str(self.activeLayer.source()))
        #pathSource=os.path.dirname(str(self.iface.activeLayer().source()))
        decision=self.addDiscretizedField()
        self.writeISFfile(decision)
        DOMLEM.main(pathSource)
#        self.showRules()
        #self.setModal(False)
        return 0
        
    def saveRules(self):
        currentDIR = (os.path.dirname(str(self.activeLayer.source())))
        rules=(os.path.join(currentDIR,"rules.rls"))
        #filename = QFileDialog.getSaveFileName(self, 'Save File', os.getenv('HOME'),".rls")
        filename = QFileDialog.getSaveFileName(self, 'Save File', ".rls") 
        shutil.copy2(rules, filename[0])
        return 0

    def openFile(self):
        filename = QFileDialog.getOpenFileName(self, 'Open File', os.getenv('HOME')) 
        f = open(filename, 'r') 
        filedata = f.read() 
        self.text.setText(filedata) 
        f.close()
        

        
class ChoroplethMAP:
    def __init__(self,activeLayer,parameterList):
        self.activeLayer=activeLayer
        self.parameterList=parameterList
        
    def symbolize(self,field):
        """Prepare legends for environmental, socio economics and sustainable values"""
        numberOfClasses=5 #=self.spinBoxClasNum.value()
        if(numberOfClasses==5):
            classes=['very low', 'low','medium','high','very high']
        else:
            classes=range(1,numberOfClasses+1)
        fieldName = field
        fieldIndex = self.activeLayer.fields().indexFromName(fieldName)
        provider = self.activeLayer.dataProvider()
        minimum = provider.minimumValue( fieldIndex )
        maximum = provider.maximumValue( fieldIndex )
        string="%s,%s,%s" %(minimum,maximum,self.activeLayer.name() )
        RangeList = []
        Opacity = 1 #"Environmental", "Economic", "Social"
        for c,i in zip(classes,range(len(classes))):
        # Crea il simbolo ed il range...
            Min = (minimum + (( maximum - minimum ) / numberOfClasses * i))
            Max = (minimum + (( maximum - minimum ) / numberOfClasses * ( i + 1 )))
            Label = "%s [%.2f - %.2f]" % (c,Min,Max)
            if field=='Environmental':
                Colour = QColor((255-255*i/numberOfClasses),\
                                (255-170*i/numberOfClasses),\
                                (127-127*i/numberOfClasses)) #yellow to green
            elif field=='Economic':
                Colour = QColor(255,255-255*i/numberOfClasses,0) #yellow to red
            elif field=='Social':
                Colour = QColor((255-255*i/numberOfClasses),\
                                (255-85*i/numberOfClasses),\
                                (127+128*i/numberOfClasses)) #yellow to cyan 255,255,127
            else:
                Colour = QColor((255-85*i/numberOfClasses),\
                                (255-255*i/numberOfClasses),\
                                (127-127*i/numberOfClasses)) #red to green
            Symbol = QgsSymbol.defaultSymbol(self.activeLayer.geometryType())
            Symbol.setColor(Colour)
            Symbol.setOpacity(Opacity)
            Range = QgsRendererRange(Min,Max,Symbol,Label)
            RangeList.append(Range)
        Renderer = QgsGraduatedSymbolRenderer('', RangeList)
        Renderer.setMode(QgsGraduatedSymbolRenderer.EqualInterval)
        Renderer.setClassAttribute(fieldName)
        add=QgsVectorLayer(self.activeLayer.source(),field,'ogr')
        add.setRenderer(Renderer)
        QgsProject.instance().addMapLayer(add)

    def renderLayer(self):
        """ Load thematic layers in canvas """
        for parameters in self.parameterList:
            f=parameters['dimension']
            self.symbolize(f)
        
