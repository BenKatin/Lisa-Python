# -*- coding: utf-8 -*-
"""
Created on Sun Apr 10 21:00:04 2016

@author: avandenbroucke
"""

from collections import namedtuple
from ..ReadEchoFiles import ProcessPrintCSV
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

QuadStat = namedtuple('QuadStat','PlateType Fluid Q N ArbAmp ArbAmpSD FH FHSD') 



def processPrintDict(a, ptype='384PP_AQ_BP2', fluid='0Pct', Interleaved=False):
    alldat = []
    if (Interleaved):
        q1 = [ [float(r['ArbAmplitude (Volts)']), float(r['FluidThickness (mm)'])] for r in a if int(r['DestWellRow']) >= 0  and int(r['DestWellRow']) < 4 and r['SkipReason'] == '' ]
        q2 = [ [float(r['ArbAmplitude (Volts)']), float(r['FluidThickness (mm)'])] for r in a if int(r['DestWellRow']) >= 4 and int(r['DestWellRow']) < 8  and r['SkipReason'] == '' ]
        q3 = [ [float(r['ArbAmplitude (Volts)']), float(r['FluidThickness (mm)'])] for r in a if int(r['DestWellRow']) >= 8 and int(r['DestWellRow']) <12 and r['SkipReason'] == '' ]
        q4 = [ [float(r['ArbAmplitude (Volts)']), float(r['FluidThickness (mm)'])] for r in a if int(r['DestWellRow']) >= 12 and int(r['DestWellRow']) <16 and r['SkipReason'] == '' ]
    else:    
        q1 = [ [float(r['ArbAmplitude (Volts)']), float(r['FluidThickness (mm)'])] for r in a if int(r['DestWellCol']) < 12 and int(r['DestWellRow']) < 8 and r['SkipReason'] == '' ]
        q2 = [ [float(r['ArbAmplitude (Volts)']), float(r['FluidThickness (mm)'])] for r in a if int(r['DestWellCol']) < 12 and int(r['DestWellRow']) >= 8 and r['SkipReason'] == '' ]
        q3 = [ [float(r['ArbAmplitude (Volts)']), float(r['FluidThickness (mm)'])] for r in a if int(r['DestWellCol']) >= 12 and int(r['DestWellRow']) < 8 and r['SkipReason'] == '' ]
        q4 = [ [float(r['ArbAmplitude (Volts)']), float(r['FluidThickness (mm)'])] for r in a if int(r['DestWellCol']) >= 12 and int(r['DestWellRow']) >= 8 and r['SkipReason'] == '' ]
    allq =  [q1, q2, q3, q4]
    for k in range(0,4):
        npa = np.asarray(allq[k])
        S = QuadStat(ptype,fluid,k,len(allq[k]),npa[:,0].mean(),npa[:,0].std(),npa[:,1].mean(),npa[:,1].std() )
        alldat.append(S)
    return alldat

def processfolder(allprintfilefolders):
    cdir = os.getcwd()
    allprintlist = []
    alldata = []
    for d in allprintfilefolders:
        os.chdir(d)
        a = ProcessPrintCSV.getListOfPrintFiles()
        platetype = d.split('\\')[:-2][-1]
        print(platetype)
        if 'DMSO' in platetype:
            nftfiles = 7
        else:    
            if 'LDV' in platetype:
                nftfiles = 8
            else:
               if 'CP' in platetype:
                  nftfiles = 4
               else:
                  nftfiles = 3  
#        a = [ r for r in a if 'Old' not in r ]          
        printlist = a[len(a)-nftfiles:]
        print('files for ', platetype, ' : ', printlist)
#        print(' FYI :: ', a)
        allprintlist +=  printlist
        if '1536' in platetype:
            dointerleaved = True
        else:
             dointerleaved = False
        for file in printlist:
            fluid = file.split('__')[2]
            a = ProcessPrintCSV.ReadEchoPrintCSV(file)
            S = processPrintDict(a,platetype,fluid,dointerleaved)
            alldata += S
    os.chdir(cdir)
    return alldata
    
def findFTFolders():    
    allprintfilefolders = []
    for root, dirs, files in os.walk(os.getcwd()):
        for d in dirs:
            if d == 'TransferPlates' and 'FinalTest' in root:
                allprintfilefolders.append(os.path.join(root,d))    
    return allprintfilefolders        

def compareFinalTests(wdir1='Calibration_E1419\\Data',wdir2='Installation_E1476\\Test_Recal\\Data',filename='cal1419_recal1476',verbose=False):
    
    basedir = os.getcwd()    
    print('Processing ' + wdir1)
    os.chdir(wdir1)
    allprintfilefolders = findFTFolders()            
    cal_1 = processfolder(allprintfilefolders)
    os.chdir(basedir)
    
    print('Processing ' + wdir2)
    os.chdir(wdir2)
    inst_folders = findFTFolders()
    inst_recal = processfolder(inst_folders)
    os.chdir(basedir)
    
    if (verbose):
        for k in range(0,len(cal_1)):
            A = cal_1[k]
            B = inst_recal[k]
            RAT = A.ArbAmp /B.ArbAmp
            print(A.PlateType, ' ', A.Fluid, ' ', A.Q,' ','{:.3f}'.format(RAT), B.PlateType, ' ', B.Fluid, ' ',B.Q)
            
    df1 = pd.DataFrame(cal_1)
    df2 = pd.DataFrame(inst_recal)

    ddf1 = df1.drop_duplicates([0,1,2])
    ddf2 = df2.drop_duplicates([0,1,2])

    df_m = pd.merge(ddf1, ddf2, on=[0,1,2], how='inner')
    df_m['R'] = df_m['4_x']/df_m['4_y'] 
    df_m['R'] /= df_m['R'].mean()
    allplates = set(df_m[0]) 
    plotall(df_m,allplates,filename,filename + '.png')
    return
 
def plot(df_m, platetype='1536LDV_DMSO',ax=None):
    if ax == None:
        fig,ax = plt.subplots()
    df_tm = df_m.loc[df_m[0] == platetype].pivot(index=1,columns=2,values='R' )
    df_tm.index.name = None
    df_tm.columns = [ 'Q0', 'Q1', 'Q2', 'Q3' ]
    df_tm.plot(kind='bar', ylim=[0.95,1.05], title=platetype,ax=ax)

def plotall(data, allplates,titlestring='',filename=None):
    fig,ax = plt.subplots(nrows=3,ncols=3,figsize=(18,12))
    plt.subplots_adjust(hspace=.6)
    row = 0
    col = 0
    for p in allplates:
        print(' .. processing .. ', p)
        plot(data, p,ax[row,col])
        col += 1
        if (col > 2):
            col = 0;
            row +=1
    fig.suptitle(titlestring)    
    if (filename):
        fi = plt.gcf()
        fi.savefig(filename,bbox_inches='tight')
        plt.show()
		
def splitOctants(myArray):
    if len(np.shape(myArray)) != 2:
         print(' Something wrong with array shape: ', np.shape(myArray))
    rr = np.shape(myArray)[0]
    cc = np.shape(myArray)[1]
    octants = np.zeros([8,rr//2,cc//4])
    for i in range(0,2):
        octants[0+i*4] = myArray[::2,i:cc//2:2]    
        octants[1+i*4] = myArray[::2,cc//2+i::2]
        octants[2+i*4] = myArray[1::2,i:cc//2:2]
        octants[3+i*4] = myArray[1::2,cc//2+i::2]
    return octants    		