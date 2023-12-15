# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name            : SSAM - Spatial Sustainability Assessment Model
Description     : geographical MCDA for sustainability assessment
Date            : 6/2/2021
copyright       : ARPA Umbria - Università degli Studi di Perugia (C) 2019
email           : (developper) Gianluca Massei (geonomica@gmail.com)

 ***************************************************************************/
Based on Scikit-Criteria is a collection of Multiple-criteria decision 
analysis (MCDA) methods integrated into scientific python stack
/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                   *
 *                                                                         *
 ***************************************************************************/
"""  

try:
    import skcriteria as skc
    
except ImportError as e:
    import pip
    pip.main(['install', 'scikit-criteria'])
    
from skcriteria.preprocessing import invert_objectives, scalers
from skcriteria.madm import similarity  # here lives TOPSIS
from skcriteria.madm import electre
from skcriteria.madm import moora
from skcriteria.pipeline import mkpipe  # this function is for create pipelines

#from skcriteria.madm.moora import FullMultiplicativeForm

class TOPSIS:
    def __init__(self,activeLayer,parameters):
        self.activeLayer=activeLayer
        self.parameters=parameters
        #self.atts=self.getCriteriaValue(self)
	
    def setting(self):
        idxs = [self.activeLayer.fields().indexFromName(fName) for fName in  self.parameters['criteria']]
        feat = self.activeLayer.getFeatures()
        atts=[[f.attributes()[i] for i in idxs ] for f in feat]
        self.alternatives=[feat.id() for feat in self.activeLayer.getFeatures()]
        self.expMat=[[x**2 for x in row] for row in atts]
        sumMat=[sum(col) for col in zip(*self.expMat)] #The asterisk in a zip() function converts the elements of the iterable into separate elements
        self.matrix=atts
        
        
    def solvus(self):
 
        dm = skc.mkdm(
            self.matrix, 
            self.parameters['preference'],
            alternatives=self.alternatives,
            weights=self.parameters['weights'],
            criteria=self.parameters['criteria'])
        print(dm.objectives,dm.alternatives)

        pipe = mkpipe(
            invert_objectives.NegateMinimize(),
            scalers.VectorScaler(target="matrix"),  # this scaler transform the matrix
            scalers.SumScaler(target="weights"),  # and this transform the weights
            similarity.TOPSIS(),
        )
        rank = pipe.evaluate(dm)
        print(rank)

        self.score=rank.e_.similarity
    
    def runTOPSIS(self):
        """process the matrix and get the ranking values for each alternative"""
        self.setting()
        #self.preprocessing()
        self.solvus()


class ELECTRE1:
    def __init__(self,activeLayer,parameters):
        self.activeLayer=activeLayer
        self.parameters=parameters
        #self.atts=self.getCriteriaValue(self)
	
    def setting(self):
        idxs = [self.activeLayer.fields().indexFromName(fName) for fName in  self.parameters['criteria']]
        feat = self.activeLayer.getFeatures()
        atts=[[f.attributes()[i] for i in idxs ] for f in feat]
        self.alternatives=[feat.id() for feat in self.activeLayer.getFeatures()]
        self.expMat=[[x**2 for x in row] for row in atts]
        sumMat=[sum(col) for col in zip(*self.expMat)] #The asterisk in a zip() function converts the elements of the iterable into separate elements
        self.matrix=atts
        
        
    def solvus(self):
 
        dm = skc.mkdm(
            self.matrix, 
            self.parameters['preference'],
            alternatives=self.alternatives,
            weights=self.parameters['weights'],
            criteria=self.parameters['criteria'])
        print(dm.objectives,dm.alternatives)

        pipe_vector = mkpipe(
            invert_objectives.InvertMinimize(),
            scalers.VectorScaler(target="matrix"),  # this scaler transform the matrix
            scalers.SumScaler(target="weights"),  # and this transform the weights
            electre.ELECTRE1(),
        )
        
        pipe_sum = mkpipe(
            invert_objectives.InvertMinimize(),
            scalers.SumScaler(target="weights"),  # transform the matrix and weights
            electre.ELECTRE1(),
        )

        rank = pipe_vector.evaluate(dm)
        print(rank)

        self.score=rank.e_.outrank
    
    def runELECTRE1(self):
        """process the matrix and get the ranking values for each alternative"""
        self.setting()
        #self.preprocessing()
        self.solvus()
        
class MOORA:
    def __init__(self,activeLayer,parameters):
        self.activeLayer=activeLayer
        self.parameters=parameters
        #self.atts=self.getCriteriaValue(self)
	
    def setting(self):
        idxs = [self.activeLayer.fields().indexFromName(fName) for fName in  self.parameters['criteria']]
        feat = self.activeLayer.getFeatures()
        atts=[[f.attributes()[i] for i in idxs ] for f in feat]
        self.alternatives=[feat.id() for feat in self.activeLayer.getFeatures()]
        self.expMat=[[x**2 for x in row] for row in atts]
        sumMat=[sum(col) for col in zip(*self.expMat)] #The asterisk in a zip() function converts the elements of the iterable into separate elements
        self.matrix=atts
        
        
    def solvus(self):
 
        dm = skc.mkdm(
            self.matrix, 
            self.parameters['preference'],
            alternatives=self.alternatives,
            weights=self.parameters['weights'],
            criteria=self.parameters['criteria'])
        #print(dm.objectives,dm.alternatives)

        pipe_vector = mkpipe(
            invert_objectives.InvertMinimize(),
            scalers.VectorScaler(target="matrix"),  # this scaler transform the matrix
            scalers.SumScaler(target="weights"),  # and this transform the weights
            moora.multimoora(),
        )
        
        pipe_sum = mkpipe(
            invert_objectives.InvertMinimize(),
            scalers.SumScaler(target="weights"),  # transform the matrix and weights
            moora.multimoora(),
        )
        
        rank = moora.multimoora.ranking(dm)
        print(dir(rank))

        self.score=rank.e_.outrank
    
    def runMOORA(self):
        """process the matrix and get the ranking values for each alternative"""
        self.setting()
        #self.preprocessing()
        self.solvus()
        
def main():
	print("scikit-criteria mcda models")
	return 0

if __name__ == '__main__':
	main()
