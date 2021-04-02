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

class TOPSIS:
    def __init__(self,activeLayer,parameters):
        self.activeLayer=activeLayer
        self.parameters=parameters
        #self.atts=self.getCriteriaValue(self)
	
    def stepOne(self):
        idxs = [self.activeLayer.fields().indexFromName(fName) for fName in  self.parameters['criteria']]
        feat = self.activeLayer.getFeatures()
        atts=[[f.attributes()[i] for i in idxs ] for f in feat]
        expMat=[[x**2 for x in row] for row in atts]
        sumMat=[sum(col) for col in zip(*expMat)] #The asterisk in a zip() function converts the elements of the iterable into separate elements
        self.sumSqrtMat=[(s**(1/2)) for s in sumMat]
        self.step1Mtx=[[(x/y) for x,y in zip(row,self.sumSqrtMat)] for row in atts]
        
    def stepTwo(self):
        weights=self.parameters['weights']
        self.step2Mtx=[[(x*w) for x,w in zip(row,weights)] for row in self.step1Mtx]
        
    def stepThree(self):
        self.ideal=[x/s*w for x,s,w in zip(self.parameters['idealPoint'],self.sumSqrtMat,self.parameters['weights'])]
        self.worst=[x/s*w for x,s,w in zip(self.parameters['worstPoint'],self.sumSqrtMat,self.parameters['weights'])]
        
    def stepFour(self):
        idealMat=[[(x-ip)**2 for x,ip in zip(row,self.ideal)] for row in self.step2Mtx]
        self.idealSeparation=[(sum(row))**(1/2) for row in idealMat]
        
        worstMat=[[(x-ip)**2 for x,ip in zip(row,self.worst)] for row in self.step2Mtx]
        self.worstSeparation=[(sum(row))**(1/2) for row in worstMat]
        
    def stepFive(self):
        self.relativeCloseness=[(w/(w+p)) for w,p in zip(self.worstSeparation,self.idealSeparation)]
        
        		
    def runTOPSIS(self):
        """process the matrix and get the ranking values for each alternative"""
        self.stepOne()
        print('step 1:',self.step1Mtx)
        self.stepTwo()
        print('step 2:', self.step2Mtx)
        self.stepThree()
        print('ideal:', self.ideal)
        print('worst', self.worst)    
        self.stepFour()
        print('worstSep:', self.worstSeparation)
        print('idealSep:', self.idealSeparation)
        self.stepFive()
        print('closeness:',self.relativeCloseness)
        
def main():
	print("topsis mcda model")
	return 0

if __name__ == '__main__':
	main()
