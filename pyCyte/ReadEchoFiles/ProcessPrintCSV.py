# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 13:56:36 2016

@author: avandenbroucke
"""

import os
import fnmatch
#import arrow
from ..ReadEchoFiles import ReadCSV 
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

def getListOfPrintFiles(wdir=None):
     """Finds all *_print.csv files in all subfolders of cwd. Returns list"""      
     printfilelist = []
     if wdir == None :
         wdir = os.getcwd()
     for root, dirs, files in os.walk(wdir):
         for k in fnmatch.filter(files,'*_print.csv'):
             printfilelist.append(os.path.join(root,k))  
     return printfilelist        
                   
def ReadEchoPrintCSV(filename):
     """This function will return a matrix of all entries in a print.csv file as a dict.
     Note that the returned dict contains strings, not numbers. """
     headerrow = 9
     if not filename.endswith('print.csv'):
         print(' Expected a file ending with \'print.csv\', filename submitted is :', filename)
     # read in header::
     header = ReadCSV.getCSVHeader(filename, headerrow) 
     # read all entries in file:
     tmpdat = ReadCSV.readCSV(filename, True, tuple(header))
     tmdat = [ row for row in tmpdat if row['SrcWellCol'] != None and row['SrcWellRow'] != None ] 
     printdat = [ row for row in tmdat if row['SrcWellCol'].isdigit() and row['SrcWellRow'].isdigit() and not (row['SrcWell'].isdigit()) ]
     return printdat
    
    
def getTotalTransferTime(printfilelist):
    """ Function that prints the total transfer time for each file in a printfilelist """
    import arrow
    deltas = []
    for file in printfilelist:
        printdat = ReadEchoPrintCSV(file)
        timestamps_arrow = [ arrow.get(row['Time'], 'HH:mm:ss.SSS') for row in printdat ]
        timestamps_arrow.sort()
        delta = timestamps_arrow[-1] - timestamps_arrow[0]
        print(' file: ', file, ' Delta: ', delta)
        deltas.append(delta.total_seconds())
    return deltas
    
def comparePrints(flist,leg=None):
    dflist = []    
    for file in flist:
        p1 = ReadEchoPrintCSV(file)
        p1df = pd.DataFrame(p1)
        dflist.append(p1df.dropna())
    
    if leg == None or len(leg) != len(flist):
        leg = [ l.split('/')[-1] for l in flist]
    colors=['blue','red','hotpink'] 
    rows=2
    cols=3
    fig, ax = plt.subplots(nrows=rows,ncols=cols,figsize=(16,12)) 
    xplots=['CurrentFluidThickness (mm)']
    yplots=['TransducerZ (um)','ArbAmplitude (Volts)','CenterFreq (MHz)','EjectionOffset (um)','FluidComposition','FocusToF (us)']
   
    for i in range(0,rows): 
        for j in range(0,cols):
            k = i*cols + j;
            for l in range(0,len(dflist)):
                ax[i][j].plot(np.asarray(dflist[l][xplots[0]],dtype='float'),np.asarray(dflist[l][yplots[k]],dtype='float'),'o',color=colors[l%len(colors)],label=leg[l])
                if k == 0:
                    ax[i][j].legend(numpoints=1,loc='upper left')
                
            ax[i][j].set_ylabel(yplots[k])
            ax[i][j].set_xlabel(xplots[0])
   