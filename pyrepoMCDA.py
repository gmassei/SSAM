# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name            : SSAM - Spatial Sustainability Assessment Model
Description     : geographical MCDA for sustainability assessment
Date            : 6/2/2021
copyright       : ARPA Umbria - Università degli Studi di Perugia (C) 2019
email           : (developper) Gianluca Massei (geonomica@gmail.com)

 ***************************************************************************/

Based on pyrepo-mcda (https://pyrepo-mcda.readthedocs.io/)


/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                   *
 *                                                                         *
 ***************************************************************************/
"""  

import numpy as np
import pandas as pd


try:
    from .pyrepo_mcda.mcda_methods import CODAS, VIKOR, COPRAS, SAW, PROMETHEE_II, TOPSIS, WASPAS
    from .pyrepo_mcda import normalizations as norms
    from .pyrepo_mcda import distance_metrics as dists
    from .pyrepo_mcda.additions import rank_preferences
    print(dir(CODAS))
    
except ImportError as e:
    print(e)
    #pip.main(['install', 'pyrepo-mcda'])
    


# from pyrepo_mcda.mcda_methods import CODAS, TOPSIS, VIKOR, COPRAS, SAW, PROMETHEE_II

# from pyrepo_mcda import distance_metrics as dists
# from pyrepo_mcda import correlations as corrs
# from pyrepo_mcda import normalizations as norms
# from pyrepo_mcda import weighting_methods as mcda_weights
# from pyrepo_mcda import compromise_rankings as compromises
# from pyrepo_mcda.additions import rank_preferences
# from pyrepo_mcda.sensitivity_analysis_weights_percentages import Sensitivity_analysis_weights_percentages
# from pyrepo_mcda.sensitivity_analysis_weights_values import Sensitivity_analysis_weights_values

class pyCODAS:
    def __init__(self,activeLayer,parameters):
        self.activeLayer=activeLayer
        self.parameters=parameters
        #self.atts=self.getCriteriaValue(self)
	
    def setting(self):
        idxs = [self.activeLayer.fields().indexFromName(fName) for fName in  self.parameters['criteria']]
        feat = self.activeLayer.getFeatures()
        atts=[[f.attributes()[i] for i in idxs ] for f in feat]
        self.alternatives=[feat.id() for feat in self.activeLayer.getFeatures()]
        self.matrix=np.array(atts)
        self.weights = np.array(self.parameters['weights'] / np.sum(self.parameters['weights']))        
        self.preference=np.array([-1 if p=="MIN" else 1 for p in self.parameters['preference']])
        self.criteria=self.parameters['criteria']
        self.rank_results = pd.DataFrame()
        self.rank_results['Ai'] = self.alternatives
        # print("matrix", self.matrix)
        # print("preference", self.preference)
        # print("weight", self.weights)
        # print("alternatives", self.rank_results['Ai'])
        
        
        
    def solvus(self):
        codas = CODAS(normalization_method = norms.linear_normalization, distance_metric = dists.euclidean, tau = 0.02)
        pref = codas(self.matrix, self.weights, self.preference)
        rank = rank_preferences(pref, reverse = True)
        self.scores=pref
        self.rank_results['CODAS'] = rank
        #print("rank:", self.rank_results['CODAS'])
        
    
    def runCODAS(self):
        """process the matrix and get the ranking values for each alternative"""
        self.setting()
        #self.preprocessing()
        self.solvus()

class pyCOPRAS:
    def __init__(self,activeLayer,parameters):
        self.activeLayer=activeLayer
        self.parameters=parameters
        #self.atts=self.getCriteriaValue(self)
	
    def setting(self):
        idxs = [self.activeLayer.fields().indexFromName(fName) for fName in  self.parameters['criteria']]
        feat = self.activeLayer.getFeatures()
        atts=[[f.attributes()[i] for i in idxs ] for f in feat]
        self.alternatives=[feat.id() for feat in self.activeLayer.getFeatures()]
        self.matrix=np.array(atts)
        self.weights = np.array(self.parameters['weights'] / np.sum(self.parameters['weights']))        
        self.preference=np.array([-1 if p=="MIN" else 1 for p in self.parameters['preference']])
        self.criteria=self.parameters['criteria']
        self.rank_results = pd.DataFrame()
        self.rank_results['Ai'] = self.alternatives
        # print("matrix", self.matrix)
        # print("preference", self.preference)
        # print("weight", self.weights)
        # print("alternatives", self.rank_results['Ai'])
        
        
        
    def solvus(self):
        copras = COPRAS(normalization_method = norms.sum_normalization)
        pref = copras(self.matrix, self.weights, self.preference)
        rank = rank_preferences(pref, reverse = True)
        self.scores=pref
        self.rank_results['COPRAS'] = rank
                
    
    def runCOPRAS(self):
        """process the matrix and get the ranking values for each alternative"""
        self.setting()
        #self.preprocessing()
        self.solvus()

class pyVIKOR:
    def __init__(self,activeLayer,parameters):
        self.activeLayer=activeLayer
        self.parameters=parameters
        #self.atts=self.getCriteriaValue(self)
	
    def setting(self):
        idxs = [self.activeLayer.fields().indexFromName(fName) for fName in  self.parameters['criteria']]
        feat = self.activeLayer.getFeatures()
        atts=[[f.attributes()[i] for i in idxs ] for f in feat]
        self.alternatives=[feat.id() for feat in self.activeLayer.getFeatures()]
        self.matrix=np.array(atts)
        self.weights = np.array(self.parameters['weights'] / np.sum(self.parameters['weights']))        
        self.preference=np.array([-1 if p=="MIN" else 1 for p in self.parameters['preference']])
        self.criteria=self.parameters['criteria']
        self.rank_results = pd.DataFrame()
        self.rank_results['Ai'] = self.alternatives
        # print("matrix", self.matrix)
        # print("preference", self.preference)
        # print("weight", self.weights)
        # print("alternatives", self.rank_results['Ai'])
        
        
        
    def solvus(self):
        vikor = VIKOR(normalization_method = norms.linear_normalization)
        pref = vikor(self.matrix, self.weights, self.preference)
        rank = rank_preferences(pref, reverse = True)
        self.scores=pref
        self.rank_results['VIKOR'] = rank
        #print("rank:", self.rank_results)
        
    
    def runVIKOR(self):
        """process the matrix and get the ranking values for each alternative"""
        self.setting()
        #self.preprocessing()
        self.solvus()
        
        
class pySAW:
    def __init__(self,activeLayer,parameters):
        self.activeLayer=activeLayer
        self.parameters=parameters
        #self.atts=self.getCriteriaValue(self)
	
    def setting(self):
        idxs = [self.activeLayer.fields().indexFromName(fName) for fName in  self.parameters['criteria']]
        feat = self.activeLayer.getFeatures()
        atts=[[f.attributes()[i] for i in idxs ] for f in feat]
        self.alternatives=[feat.id() for feat in self.activeLayer.getFeatures()]
        self.matrix=np.array(atts)
        self.weights = np.array(self.parameters['weights'] / np.sum(self.parameters['weights']))        
        self.preference=np.array([-1 if p=="MIN" else 1 for p in self.parameters['preference']])
        self.criteria=self.parameters['criteria']
        self.rank_results = pd.DataFrame()
        self.rank_results['Ai'] = self.alternatives
        # print("matrix", self.matrix)
        # print("preference", self.preference)
        # print("weight", self.weights)
        # print("alternatives", self.rank_results['Ai'])
        

        
    def solvus(self):
        saw = SAW(normalization_method = norms.linear_normalization)
        pref = saw(self.matrix, self.weights, self.preference)
        rank = rank_preferences(pref, reverse = True)
        self.scores=pref
        self.rank_results['SAW'] = rank
        #print("rank:", self.rank_results)
        
    
    def runSAW(self):
        """process the matrix and get the ranking values for each alternative"""
        self.setting()
        #self.preprocessing()
        self.solvus()
        
        
class pyPROMETHEE:
    def __init__(self,activeLayer,parameters):
        self.activeLayer=activeLayer
        self.parameters=parameters
        #self.atts=self.getCriteriaValue(self)
	
    def setting(self):
        idxs = [self.activeLayer.fields().indexFromName(fName) for fName in  self.parameters['criteria']]
        feat = self.activeLayer.getFeatures()
        atts=[[f.attributes()[i] for i in idxs ] for f in feat]
        self.alternatives=[feat.id() for feat in self.activeLayer.getFeatures()]
        self.matrix=np.array(atts)
        self.weights = np.array(self.parameters['weights'] / np.sum(self.parameters['weights']))        
        self.preference=np.array([-1 if p=="MIN" else 1 for p in self.parameters['preference']])
        self.criteria=self.parameters['criteria']
        self.rank_results = pd.DataFrame()
        self.rank_results['Ai'] = self.alternatives
        
    def solvus(self):
        promethee = PROMETHEE_II()
        pref = promethee(self.matrix, self.weights, self.preference)
        rank = rank_preferences(pref, reverse = True)
        self.scores=pref
        self.rank_results['PROMETHEE II'] = rank
        #print("rank:", self.rank_results)
		
    def runPROMETHEE(self):
        """process the matrix and get the ranking values for each alternative"""
        self.setting()
        #self.preprocessing()
        self.solvus()

class pyTOPSIS:
    def __init__(self,activeLayer,parameters):
        self.activeLayer=activeLayer
        self.parameters=parameters
        #self.atts=self.getCriteriaValue(self)
	
    def setting(self):
        idxs = [self.activeLayer.fields().indexFromName(fName) for fName in  self.parameters['criteria']]
        feat = self.activeLayer.getFeatures()
        atts=[[f.attributes()[i] for i in idxs ] for f in feat]
        self.alternatives=[feat.id() for feat in self.activeLayer.getFeatures()]
        self.matrix=np.array(atts)
        self.weights = np.array(self.parameters['weights'] / np.sum(self.parameters['weights']))        
        self.preference=np.array([-1 if p=="MIN" else 1 for p in self.parameters['preference']])
        self.criteria=self.parameters['criteria']
        self.rank_results = pd.DataFrame()
        self.rank_results['Ai'] = self.alternatives

        
    def solvus(self):
        topsis = TOPSIS(normalization_method = norms.minmax_normalization, distance_metric = dists.euclidean)
        pref = topsis(self.matrix, self.weights, self.preference)
        rank = rank_preferences(pref, reverse = True)
        self.scores=pref
        self.rank_results['TOPSIS'] = rank
        
    def runTOPSIS(self):
        """process the matrix and get the ranking values for each alternative"""
        self.setting()
        #self.preprocessing()
        self.solvus()
		

class pyWASPAS:
    def __init__(self,activeLayer,parameters):
        self.activeLayer=activeLayer
        self.parameters=parameters
        #self.atts=self.getCriteriaValue(self)
	
    def setting(self):
        idxs = [self.activeLayer.fields().indexFromName(fName) for fName in  self.parameters['criteria']]
        feat = self.activeLayer.getFeatures()
        atts=[[f.attributes()[i] for i in idxs ] for f in feat]
        self.alternatives=[feat.id() for feat in self.activeLayer.getFeatures()]
        self.matrix=np.array(atts)
        self.weights = np.array(self.parameters['weights'] / np.sum(self.parameters['weights']))        
        self.preference=np.array([-1 if p=="MIN" else 1 for p in self.parameters['preference']])
        self.criteria=self.parameters['criteria']
        self.rank_results = pd.DataFrame()
        self.rank_results['Ai'] = self.alternatives

        
    def solvus(self):
        waspas = WASPAS(normalization_method = norms.linear_normalization, lambda_param = 0.5)
        pref = waspas(self.matrix, self.weights, self.preference)
        rank = rank_preferences(pref, reverse = True)
        self.scores=pref
        self.rank_results['WASPAS'] = rank
    
    def runWASPAS(self):
        """process the matrix and get the ranking values for each alternative"""
        self.setting()
        #self.preprocessing()
        self.solvus()
        
def main():
	print("pyrepo mcda models")
	return 0

if __name__ == '__main__':
	main()
