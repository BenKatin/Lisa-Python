# -*- coding: utf-8 -*-
"""
Created on Sat Nov  5 10:05:07 2016

@author: avandenbroucke

File to process ACCESS Run Data for Classification


"""

import pandas
import os
import numpy as np
import matplotlib.pyplot as plt
from ..ReadEchoFiles import ProcessPlateSurveyCSV

rundict= {
 '307' : '70%EtOh',
  '308': '70%EtOh',
  '309': 'HEPES',
  '310': 'HEPES',
  '311':  'H20',
  '312':  'H20',
  '313':   '80%DMSO',
  '314':   '80%DMSO',
  '315': '80%DMSO',
  '316': '80%DMSO'
}

legend=['HEPES','HEPES','H20','H20','DMSO','DMSO','DMSO','DMSO','EtOH','EtOH']

markercolor=['b', 'g', 'r', 'c', 'm', 'y', 'k','hotpink','fuchsia','sage','azure','slategray','tan']

wdir='\\\\seg\\data\\Seahorse_123A_lot102116\\Peel_Seal_Survey\\Formatted_Files'

#gg_tofdelta = np.array( [0.5862,  0.587 ,  0.5932,  0.5978,  0.6406,  0.6324,  0.6346,
#        0.6446,  0.6362,  0.6266,  0.6228,  0.625 ,  0.6112,  0.5906,
#        0.6126,  0.6222,  0.6658,  0.6564,  0.6364,  0.6766,  0.6214,
 #       0.6062,  0.61  ,  0.5896])
  
gg_tofdelta = np.array([ 0.59863636,  0.59860606,  0.60184848,  0.59936364,  0.5930303 ,
        0.58581818,  0.58686364,  0.59513636,  0.60231818,  0.60115152,
        0.60318182,  0.60298485,  0.6029697 ,  0.60416667,  0.60233333,
        0.60456061,  0.59768182,  0.59022727,  0.58780303,  0.59483333,
        0.60119697,  0.60315152,  0.59963636,  0.59786364])
        
gg_bbvpp = np.array([ 2.4918,  2.4278,  2.4384,  2.3434,  2.2418,  2.3278,  2.3027,
        2.223 ,  2.3199,  2.4322,  2.4107,  2.4309,  2.4323,  2.3886,
        2.4107,  2.3152,  2.2105,  2.2901,  2.2776,  2.1901,  2.2481,
        2.3479,  2.3231,  2.3496])        

sea_tofdelta = np.array([ 0.6098,  0.6242,  0.6293,  0.6316,  0.6331,  0.6345,  0.6359,
        0.6366,  0.6379,  0.638 ,  0.637 ,  0.637 ,  0.6342,  0.6364,
        0.6368,  0.637 ,  0.636 ,  0.6348,  0.6337,  0.6322,  0.6308,
        0.6282,  0.6229,  0.6104])

sea_bbvpp = np.array([ 2.29395,  2.2473 ,  2.2167 ,  2.17915,  2.1488 ,  2.1224 ,
        2.08635,  2.06745,  2.0589 ,  2.04795,  2.04715,  2.0682 ,
        2.0432 ,  2.0386 ,  2.0433 ,  2.0457 ,  2.04715,  2.0675 ,
        2.0932 ,  2.1122 ,  2.12625,  2.1557 ,  2.17995,  2.21605])

def findRunNr(filename):
    p1 = filename.split('_')[0]
    run = p1.split('-')[-1]
    return run

def scratch():
   
    return

def plotDF(GG, title='LAM'):
    fig, ax = plt.subplots(nrows=1,ncols=1,figsize=(15,6))
    GG['tot_gg'] = GG['c_bbvpp_gg']+GG['c_tof_gg']
    GG['tot_sea'] = GG['c_bbvpp_sea']+GG['c_tof_sea']
    GG[['c_bbvpp_gg', 'c_bbvpp_sea', 'c_tof_gg', 'c_tof_sea', 'tot_gg', 'tot_sea']].plot(kind='box', title=title,ax=ax)
    return  

def processRun(A, run=0,runnr=0):
    alld = []; ct = ['c_tof_sea','c_tof_gg']; ca  = ['c_bbvpp_sea','c_bbvpp_gg']
    for i,s in enumerate(A):
        cor ={}
        cor['run'] = run
        cor['runnr'] = runnr
        cor['file'] = s['filename']
        tofdelta = np.array(s['TBBBToFProfile'])
        bbvpp = np.array(s['BBVppProfile'])
        if len(tofdelta) != 24 :
            continue
        if len(bbvpp) != 24:
            continue
        for j,p in enumerate([ sea_tofdelta, gg_tofdelta ]):
            ind = ct[j]
            cor[ind] = np.corrcoef(tofdelta, p)[0][1]
        for j,p in enumerate([ sea_bbvpp, gg_bbvpp ]):
           ind = ca[j]
           cor[ind] = np.corrcoef(bbvpp, p)[0][1]
        alld.append(cor)
    return alld    



def processFolder(header=6):
    fl = [ f for f in os.listdir() if f.endswith('.csv') ] #and f.startswith('Sea-10-25') ]
    return processList(fl, header)    
 
   
    
def processList(fl, header=6):    
    allsurveydat = []
    for file in fl:        
        s = pandas.read_csv(file,header=header)
        s = s.rename(columns=lambda x: x.strip())
        V7,T7 = extractRow(s, 7)
        V8,T8 = extractRow(s,8)
        VAve = ( V7 + V8 ) / 2
        TAve = ( T7 + T8 ) / 2
        surveydat = {}
        surveydat['filename'] = file
        surveydat['BBVppProfile'] = VAve
        surveydat['TBBBToFProfile'] = TAve
        allsurveydat.append(surveydat)
    return allsurveydat    

def plotSurveydat(allsurveydat, title='Empty Wells'):
    fig, ax = plt.subplots(figsize=(12,6), nrows=1, ncols=2)
    for i,s in enumerate(allsurveydat):
        r = findRunNr(s['filename'])
        if r in rundict :
            fluid = rundict[r]
        else:
            fluid = legend[i]
        ax[1].plot(s['TBBBToFProfile'], label=fluid, color=markercolor[i%len(markercolor)])
    for i,s in enumerate(allsurveydat):
        ax[0].plot(s['BBVppProfile'], color=markercolor[i%len(markercolor)])    
    ax[0].set_xlabel('column')
    ax[1].set_xlabel('column')
    ax[0].set_ylabel('BB Vpp')
    ax[1].set_ylabel('TB-BB ToF (us)')
    box = ax[1].get_position()
    ax[1].set_position([box.x0, box.y0, box.width * 0.8, box.height])
       #   Put a legend to the right of the current axis
    ax[1].legend(loc='center left', bbox_to_anchor=(1, 0.5))
    fig.suptitle(title)
    return    
     
def extractRow(s, WellRow=7, jandata=False):
    bbvppprof = []; 
    deltatofprof = []
    for i,row in s.iterrows():
        if row['WellRow'] == WellRow :
            ewvpp = float(row['EW BB Vpp'] )
            if ewvpp > 0 :
                bbvpp = ewvpp
                tbvpp = float(row['EW TB Vpp'])
                bbtof = float(row['EW BB ToF (us)'])
                tbtof = float(row['EW TB ToF (us)'])
            else:  
                bbvpp = float(row['FW BB Vpp'])
                tbvpp = float(row['FW TB1 Vpp'])
                bbtof = float(row['FW BB ToF (us)'])
                tbtof = float(row['FW TB1 ToF (us)']) 
            bbvppprof.append(bbvpp)
            deltatofprof.append(tbtof-bbtof)
    return np.asarray(bbvppprof), np.asarray(deltatofprof)  

def extractKernel(A):
    sea_tofdelta = np.zeros(24)
    sea_bbvpp = np.zeros(24)
    for i,s in enumerate(A):
        if len(s['TBBBToFProfile']) != 24:
            continue
        sea_tofdelta += np.array(s['TBBBToFProfile'])
        sea_bbvpp += np.array(s['BBVppProfile'])
    return sea_bbvpp/len(A), sea_tofdelta/len(A) 

def plotKernel():
    fig, ax = plt.subplots(nrows=1,ncols=2, figsize=(12,6))
    ax[1].plot(gg_tofdelta, label='Greiner')
    ax[1].plot(sea_tofdelta, label='SeaHorse')
    ax[0].plot(gg_bbvpp, label='Greiner')
    ax[0].plot(sea_bbvpp, label='SeaHorse')
    ax[0].legend(loc='upper right')
    ax[1].legend(loc='upper right')
    ax[0].set_xlabel('column')
    ax[1].set_xlabel('column')
    ax[0].set_ylabel('BB Vpp')
    ax[1].set_ylabel('TB-BB ToF (us)')
    return

def processMFGUnit(unit='16XX'):
     d = ProcessPlateSurveyCSV.getListOfPlateSurveyFiles()
     d_pp = [ f for f in d if '384PP' in f ]
     G = processList(d_pp,4)
     G_PROC = processRun(G,0,0)
     G_DF = pandas.DataFrame(G_PROC)
     plotDF(G_DF, title= unit + '- ALL PP')
     return G_DF
     
def processPeelSeal():
    os.chdir('\\\\seg\\data\\Seahorse_123A_lot102116\\Peel_Seal_Survey\\Formatted_Files')
    runs = os.listdir()
    return processRunList(runs,'Seahorse Peel and Seal')

def processFilled():
    os.chdir('\\\\seg\\data\\Seahorse_123A_lot102116\\Filled_Plate_Survey\\Formatted_Files')
    runs = os.listdir()
    return processRunList(runs,'Seahorse - Filled')

def processEmpty():
     os.chdir('\\\\seg\\data\\Seahorse_123A_lot102116\\Empty_Plate_Survey\\Formatted_Files') 
     A = processFolder()
     D= processRun(A)
     D_DF = pandas.DataFrame(D)
     plotDF(D_DF, title='Empty Seahorse Plates')
     return D_DF
     
    
def processRunList(runs, title=''): 
    ALLD_PS = []
    for run in runs:
        if os.path.isdir(run):
            os.chdir(run)
            runnr = run.split('Run')[1]
            A = processFolder()
            D= processRun(A, run,int(runnr))
            ALLD_PS +=D 
            os.chdir('../')
    PS_DF = pandas.DataFrame(ALLD_PS)
    plotDF(PS_DF, title=title)    
    return PS_DF
    
    

     