# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 13:56:36 2016

@author: avandenbroucke
"""

import os
#import fnmatch
import numpy as np
from ..ReadEchoFiles import ReadCSV 
from ..ToolBox import SimpleTools
import pandas as pd
import matplotlib.pyplot as plt

def getListOfMIPOutputFiles(pattern='*MIPOutput.csv'):
     """Finds all *MIPOutput.csv files in all subfolders of cwd. Returns list"""      
     return SimpleTools.getFileList(pattern)        
                   
def ReadEchoMIPOutputCSV(filename):
     """This function will return a matrix of all entries in a MIPOutput.csv file as a dict.
     Note that the returned dict contains strings, not numbers. """
     headerrow = 9
     if not filename.endswith('MIPOutput.csv'):
         print(' Expected a file ending with \'print.csv\', filename submitted is :', filename)
     # read in header::
     header = ReadCSV.getCSVHeader(filename, headerrow) 
     # read all entries in file:
     tmpdat = ReadCSV.readCSV(filename, True, tuple(header))
     tmdat = [ row for row in tmpdat if row['SrcWell'] != None and row['DestWell'] != None ] 
     mipoutput = [ row for row in tmdat if row['Column'].isdigit() and row['Row'].isdigit() and not (row['SrcWell'].isdigit()) ]
     return mipoutput
    
def MIPOutputasDF(filename):
     """This function will return a pandas dataframe of all entries in a MIPOutput.csv.
     """
#     headerrow = 9
     if not filename.endswith('MIPOutput.csv'):
         print(' Expected a file ending with \'MIPoutput.csv\', filename submitted is :', filename)
     # read in header::
     dataframe = pd.read_csv(filename, header=6)
     # convert Powerstate to int
     dataframe['PowerState'] = dataframe['PowerState'].apply(lambda x: int(x,base=16))
     return dataframe
    
def getMIObservableArray(mifilelist, dictkey='Total Iterations', datatype='float'):
    """ Function that returns a np array of number of iterations for each file in an mifilelist.
    An Array of n*384 is returned. n being number of valid entries in the filelist
    Input arguments:
         mifilelist -- 
         dictkey    -- key in dictionary of  the variable fo interest
         dataype    -- datatype of the variable, e.g. float, int, string
    """
    alliterations = []
    for file in mifilelist:
        mi = ReadEchoMIPOutputCSV(file)
        iterations = [ row[dictkey] for row in mi ]
        alliterations.append(iterations)
    itnp = np.array(alliterations, datatype)
    return itnp
    
def genMISumPlots(pdframe, title='Generic', savedir=None, fields=['TransducerZ','NullSpace(MHz)','Total Iterations','PowerState','Calculated Eject Power(dB)','New EjectAmp(Volt)']):
    nrows = len(fields)//2
    fig, ax = plt.subplots(figsize=(24,8), nrows=nrows,ncols=4)
    c = 0;
    ind = 0;
    for k in range(0,nrows):
        c = 0
        for j in range(0,2):
            val = fields[ind]
            if val == 'PowerState':
                pdframe['PowerState'] = pdframe['PowerState'].apply(lambda x: x%16)
            pdframe.plot(kind='scatter', x='FluidHeight', y=val, ax=ax[k][c])
            pdframe.hist(val, ax = ax[k][c+1])
            ind += 1
            c = 2
    plt.subplots_adjust(hspace=.6,top=.85)
    plt.suptitle(title,size=16,x=.5,y=.999) 
    if savedir != None:
        filename = os.path.join(savedir, title)
    #    if (fileappendix != '' ):
     #       filename += '_' + fileappendix
        filename += '.png'
        print('Saving as file',filename)
        plt.savefig(filename,dpi=200,bbox_inches='tight')
    plt.show()                   
    
    return          
    
    
#def scratch():
#    mifiles = getListOfMIPOutputFiles()  
#    flist =[]
#    for files in mifiles:
#    if 'DMSO' in files:
#        print(files)
#        flist.append(files)
#      
#        flist =[]
#        for files in mifiles:
#            if 'DMSO' in files:
#        print(files)
#        flist.append(files)