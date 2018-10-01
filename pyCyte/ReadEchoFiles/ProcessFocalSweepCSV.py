# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 13:56:36 2016

@author: avandenbroucke
"""

#import os
#import fnmatch
#import numpy as np
from ..ReadEchoFiles import ReadCSV 
from ..ToolBox import SimpleTools 
import pandas as pd
import matplotlib.pyplot as plt

def getListOfFocalSweepFiles():
     """Finds all FocalSweep_*.csv files in all subfolders of cwd. Returns list"""      
     return SimpleTools.getFileList('FocalSweep*.csv')        
 
    
def FocalSweepasDF(filename):
     """This function will return a pandas dataframe of all entries in a FocalSweep*.csv.
     """
     headerrow = 13
     if not 'FocalSweep' in filename and filename.endswith('.csv'):
         print(' Expected a file like \'*FocalSweep*csv\', filename submitted is :', filename)
     # read in header::
     cols = ReadCSV.getCSVHeader(filename,headerrow)    
     # edit columns beacuse first two columns are empty:
     cols[0] = 'NA1'
     cols[1] = 'NA2'
     dataframe = pd.read_csv(filename, names=cols, skiprows=13 )
     return dataframe.drop([0]).dropna(axis=1, how='all').apply(pd.to_numeric)
    

def plotFocalSweepdata(filelist, columns = ['BB ToF (us)','TB1 Amp (Vpp)']):
    """ Fucntion will plot all an x,y plot of all files in filelits. Columns can be specified as arguments """
    for f in filelist:
        dframe = FocalSweepasDF(f)
        label = f.split('.csv')[0].split('-')[-1]
        d = dframe.as_matrix(columns=columns)
        plt.plot(d[:,0],d[:,1]/d[:,1].sum(),label=label)
    plt.legend(loc='upper left')    
    plt.show()    
