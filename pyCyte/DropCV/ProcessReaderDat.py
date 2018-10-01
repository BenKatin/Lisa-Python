# -*- coding: utf-8 -*-
"""
Created on Wed Nov  2 22:08:00 2016

@author: avandenbroucke
"""

import os
if ( __package__ is None ):
    from ..DropCV  import ReaderDat
else:
    from DropCV import ReaderDat
import matplotlib.pyplot as plt
import pandas 
import time
from tkinter import filedialog

 
def processReaderFiles(reader='BMGUK',date='102016', outfilename='ReaderData',useIntStd=True):
    f = os.listdir()
    ff = [ i for i in f if i.startswith('Final')  and i.endswith('csv')]
    return processReaderFileList(ff, reader=reader, date=date, outfilename=outfilename, useIntStd=useIntStd)

def parser(filename):
    a = filename.replace(' ','_')
    parts= a.split('_')
    plastic = parts[3][-1]
    echo = parts[3][4:8]
    fluid = 'unknown'
    if len(parts) > 4:
        fluid = parts[4].split('.')[0]
    if len(parts) > 5:
        fluid += parts[5].split('.')[0]
    return plastic, echo, fluid    
    
    
def processReaderFileList(filelist, reader='BMGUK', date='102016', outfilename='ReaderData', outdir=None, useIntStd=True):
    r = ReaderDat.ReaderDat()
    r.setStdCurve(lutdate=date,reader=reader,UseInternalStd=useIntStd)
    r.PMTCorrectionTolerance = 0.5
    
    if len(filelist) < 1:
        print(' please specify at least one file')
        return 
    if outdir :
        basedir = outdir
    else:    
        basedir = os.path.dirname(filelist[0])    
    fulloutfilename = basedir + './' + outfilename    
    
    ncols = 4
    nrows = (len(filelist)+(ncols-1))//ncols
    if (nrows == 1 ):
        nrows += 1 
    fig, ax = plt.subplots(figsize=(18*ncols,10*nrows),nrows=nrows,ncols=ncols);
    row = 0
    col = 0
    allstats = []
    for file in filelist:
        print('Processing ', file)
        raw = r.processReaderFile(file)
#        If BMG reader is used, most extract process date from file and get relevant curves
        if reader == 'BMG':
            procdate = r.getProcessDate(file)
            caldate = r.getCalDate(reader=reader,lutdate=date,processdate=procdate,useInternalStd=useIntStd)
            r.setStdCurve(lutdate=date, reader=reader, UseInternalStd=useIntStd, caldate=caldate)
        cal = r.applyCalCurve(raw)
        stats = r.getPrintStats(cal)
        print(' ---- Std Curve Slope :: ', r.StdCurveSlope, ' Offset :: ', r.StdCurveOffset, ' ---- ')
        print('PMT correction: ', r.StdCurvePMTCorr)
        statdict = stats._asdict()
        statdict['File'] = file
        plastic, echosn, fluid = parser(file)
        statdict['Plastic'] = plastic
        statdict['Fluid'] = fluid
        statdict['EchoSN'] = echosn
        allstats.append(statdict)
        print( ' row .. ', row, ' col ..', col)
        r.plotReaderDat(cal,stats, ax=ax[row][col], title=os.path.basename(file))
        if col < (ncols-1) :
             col +=1
        else:
            col = 0
            row +=1
    plt.savefig(fulloutfilename + '.png')
    AllStats = pandas.DataFrame(allstats)
    CC = ['File','EchoSN','Plastic', 'Fluid','Mean','RawCV','CV','Empties','Outlier','Reliability','PMTCorr']
    AllStats = AllStats[CC]
    AllStats.to_csv(fulloutfilename +'_Summary.csv', index=False)
          
    return AllStats, basedir        
    
def selectReaderFiles(reader='BMGUK',date='112016',outfilename='ReaderData',useIntStd=True,initialdir='C:\\Temp'):
    ff =  filedialog.askopenfilenames(title='please select files you want to process',initialdir=initialdir)  
    outfilename += '_'
    outfilename +=  time.strftime("%Y%m%d-%H%M%S")
    return processReaderFileList(ff, reader=reader, date=date, outfilename=outfilename, useIntStd=useIntStd)