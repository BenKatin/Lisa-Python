# -*- coding: utf-8 -*-
"""
Created on Thu Jun 29 22:28:37 2017

@author:    avandenbroucke
            lchang: added h5survey class, Aug 20, 2018
"""

if __package__ is None or __package__ == '':
    from pyCyte.SigPro import FineMipAna
    from pyCyte.ToolBox import SimpleTools
else:
    from ..SigPro import FineMipAna
    from ..ToolBox import SimpleTools

import numpy as np
import h5py
import pandas as pd

class h5ana():
    
    def __init__(self,filename=None):
        self.fma = FineMipAna.FineMipAna(filename)
        self.PrintDat, n = self.fma.getPrintDat() 
        self.ClassifiedPlateType = self.fma.h5file.attrs['ClassifiedPlateType']
        self.surveydat = self.fma.surveydat

    def applyTOFCorrection(self):
        # check if we already applied the correction :
        if (self.TOFCorrected):
            return
        FL = self.hfile.attrs['TransducerFocalLengthUs']
        for c in self.Candidates:
            label = 'BBVpp' + '_'+ c
            for i in range(0,len(self.Attempts)):
                self.ClasData[i][label] = self.ClasData[i]['BBVpp'] * np.interp( self.SurveyTOF, self.tof_corr[c]['X'], self.tof_corr[c]['Y'])/ np.interp( (self.ClasData[i]['BBTOF'] / FL ) , self.tof_corr[c]['X'],self.tof_corr[c]['Y'] )
        self.TOFCorrected = True
        return    
        
    def plotvar(self, var='Out. Compos.',R=[65,100]):
        m = np.zeros([16,24])
        for index, row in self.PrintDat.iterrows():
            rc = self.getRowCol(row['DW'])
            m[rc[0],rc[1]] = row[var]
        SimpleTools.plotMatrix(m,range=R,title=self.ClassifiedPlateType)
        return m
        
    def getRowCol(self,SW='A1'):
        if len(SW) < 4 :
            row = SW[0].upper()
            col = SW[1:]
        else:
            print('1536 well plates not supported yet')
            return 0,0
            row =SW[0:2]
            col = SW[2:] 
        return ord(row)-65, int(col)-1    

class h5survey():
    def readH5file(self,filename=None):
        f = h5py.File(filename, 'r')
        dataset = f['PlateSurvey']
        arr1ev  = dataset['SurveyAnalysis']
        
        df = pd.DataFrame()
        for i in range(0, len(arr1ev)):
            a = pd.DataFrame([list(arr1ev[i])])
            df = pd.concat([df, a], axis = 0, ignore_index = True)
#        df[0] = df[0].map(lambda x: x.lstrip("b'").rstrip("'"))
        df.columns = ['Well','Row','Col','NFeatures','WellCode','TBTOF','TBVpp','BBBTOF','BBVpp','SRTOF','SRVpp','SR2TOF','SR2Vpp','FillHeightMM','ImpedanceMRayl','ConcentrationPct']
        df['Well'] = df['Well'].values.astype('str')
        f.close()
        return df