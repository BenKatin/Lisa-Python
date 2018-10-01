# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 20:45:04 2017

@author: lchang
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 08:15:06 2016

@author: lchang
"""

import sys, getopt
#import argparse
import os
import shutil
import tkinter
import tkinter.filedialog as FD
import errno
import pandas as pd
import datetime
import time
import subprocess
import fnmatch
from ..ToolBox import SimpleTools as st
from ..EjectSweep import processEjectSweep as ess
from ..Access import ProcessAccess as PA
from ..Access import calAnalysis as CA
from ..Access import RTDBAdjust as RA
import warnings
import numpy as np


def main(argv):
    
    warnings.filterwarnings("ignore")
    infoLoc = 'C:\\temp'
    transducerInfoFile = pd.read_csv(infoLoc+'\\TransducerSwapInfo.txt', header=None)
    transducer = transducerInfoFile.iloc[0][0]
    LUTdate = transducerInfoFile.iloc[4][0]
    reader = transducerInfoFile.iloc[3][0]
    
#    destroot = 'C:\\'+transducer+'\\Calibration_E1419'
    destroot = '\\\\seg\\transducer\\Transducers\\'+transducer+'\\Calibration_E1419'
    
#   Looks for the latest Swissard generated folder:

    if 'Calibration' in destroot:
        folderlist = fnmatch.filter(next(os.walk(destroot))[1], '*-*-*_*-*-*')
        folderlist.sort()
        destination = destroot+'\\'+folderlist[-1]+'\\Calibration'
    
    if not os.path.exists(destination):
        print('Filepath not found')
        return
    
    try:
        opts, args = getopt.getopt(argv,"Dhr:s:pt:st",["RunID=","RunStartDate=","PlateType=", "Style="])
    except getopt.GetoptError:
        print( 'Unknown argument .. please specify: ') 
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(' Help function .. ')
            sys.exit()
        elif opt in ("-pt", "--PlateType"):
            plateType = arg
            print(plateType)
        elif opt in ("-st", "--Style"):
            style = arg
            print(style)
#        elif opt in ("-end","--RunEndDate"):
#            conc = arg
#            print(conc)
    runInfofile = infoLoc+'\\'+plateType+'_RunInfo.csv'
    runInfo = pd.read_csv(runInfofile)
    runID = runInfo.loc[0][1]
    runStart = runInfo.loc[1][1]
    
    try:
        runEnd = float(runInfo.loc[3][1])
    except:
        runEnd = datetime.datetime.now()
        runEnd = time.time()
        runInfo = runInfo['0'].append(pd.DataFrame([runEnd]))
        runInfo.to_csv(runInfofile)
#    runEnd = datetime.datetime.strptime(str('2017-04-20 09:54:24'), '%Y-%m-%d %H:%M:%S')
#    runEnd = time.mktime(runEnd.timetuple())
    runS = datetime.datetime.strptime(str(runStart), '%Y-%m-%d %H:%M:%S')
    runStrt = time.mktime(runS.timetuple())
    
    if str(style) == 'FT':
        test = 'FinalTest'        
    elif str(style) == 'ES':
        test = 'Ejectsweep'            
    else:
        test = str(style)
        print('Non-standard Test Folder')
        return        
        
    destinationT = destination+'\\'+plateType+'\\'+test+'\\TransferPlates'
    destinationR = destination+'\\'+plateType+'\\'+test+'\\ReaderResults'
    if not os.path.exists(destinationT):
        os.makedirs(destinationT)
    if not os.path.exists(destinationR):
        os.makedirs(destinationR)   
    
    os.chdir(destinationT)
    runlog = fnmatch.filter(os.listdir(),'Run_*')
    for r in runlog:
        if r.split('_')[-1] != runID:
            shutil.rmtree(r)
        
    if str(style) == 'FT':
        dest = destination+'\\'+plateType+'\\'+test
        destana = dest+'\\Analysis'
        if os.path.exists(destana):
            os.chdir(destana)
            if os.path.isfile('ReaderData__'+plateType+'__FinalTest.png') == True:
                j = 1
                while os.path.exists(dest+'\\FT%s' % j):
                    j += 1
                newfolder = dest+('\\FT%s' % j)
                os.makedirs(newfolder)
                os.chdir(dest)
                files = os.listdir()
                for f in files:
                    if not 'FT' in f:
                        shutil.move(f, newfolder)
                if not os.path.exists(destinationT):
                    os.makedirs(destinationT)
                if not os.path.exists(destinationR):
                    os.makedirs(destinationR) 
        os.chdir(destinationT)
        anyMIPfiles = fnmatch.filter(os.listdir(),'*__platesurvey*.csv')
        if len(anyMIPfiles) > 0:
            os.chdir(dest)
            PA.ProcessAccess(LUTdate, reader)
            os.chdir('C:\\')        #Change working directory to local to avoid UNC path error
            os.system('start '+dest)
            return
        
    elif str(style) == 'ES':
        dest = destination+'\\'+plateType+'\\'+test
        os.chdir(dest)
        bowlfile = fnmatch.filter(os.listdir(),'*_dBAdjust.csv')
#        if os.path.isfile(bowlfile) == True:
        if len(bowlfile) > 0:
            j = 1
            while os.path.exists(dest+'\\ES%s' % j):
                print('yup')
                j += 1
            newfolder = dest+('\\ES%s' % j)
            os.makedirs(newfolder)
            files = os.listdir()
            for f in files:
                if not 'ES' in f:
                    shutil.move(f, newfolder)
        if not os.path.exists(destinationT):
            os.makedirs(destinationT)
        if not os.path.exists(destinationR):
            os.makedirs(destinationR) 
            
        
#   Copy Run Log
    source = 'C:\\Labcyte\Tempo\Logs'
    
    folder = '\\Run_'+str(runID.split('--')[-1])
    indir = source + folder
    print(folder)
    outdir = destinationT + folder
    if not os.path.exists(outdir):
        if os.path.exists(outdir):
           shutil.rmtree(outdir)
           shutil.copytree(indir, outdir)
        shutil.copytree(indir,outdir)
    
#   Read plate information to get barcode information
    os.chdir(outdir)
    platefile= st.getFileList('PlateData*.csv')
    plateinfo = pd.read_csv(platefile[0])
    plateinfo.columns = [x.strip().replace(' ', '') for x in plateinfo.columns]
    plateinfo.PlateBarcode = [x.strip().replace(' ', '') for x in plateinfo.PlateBarcode]
    platearray = np.array(plateinfo.PlateBarcode)
    
    surveyloc = 'C:\\Labcyte\\Echo\\Cache\\Logs\\Survey'
    for (dirpath, dirnames, filenames) in os.walk(surveyloc):
        for filename in filenames:
            f = '/'.join([dirpath,filename])
            ctime = os.stat(f)[-1]
            if ctime>=runStrt and ctime <=runEnd: 
                shutil.copy(f, destinationT)
                print('Copying Survey Logs...')
    
    transferloc = 'C:\\Labcyte\\Echo\\Cache\\Logs\\Transfer'
    for (dirpath, dirnames, filenames) in os.walk(transferloc):
        for filename in filenames:
            f = '/'.join([dirpath,filename])
            ctime = os.stat(f)[-1]
#            with open(filename) as openfile:
#                for line in openfile:
#                    if 'date' in line:
#                        ctime0 = line.split('date=')[1].split('"')[1].split('.')[0]
#                        ctimet = datetime.datetime.strptime(str(ctime0), '%Y-%m-%d %H:%M:%S')
#                        ctime = time.mktime(ctimet.timetuple())
            if ctime>=runStrt and ctime <=runEnd: 
                shutil.copy(f, destinationT)
                print('Copying Transfer Logs...')
    
#    serverlogsloc = '\\\\seg\\data\\Echo_Logs\\E5XX-1419\\Echo\\Server\\Logs'
    serverlogsloc = 'C:\\Labcyte\\Echo\\Server\\Logs'
    for (dirpath, dirnames, filenames) in os.walk(serverlogsloc):
        if dirpath == serverlogsloc:       
            print('true')
            for filename in filenames:
                f = '/'.join([dirpath,filename])
                print(f)
                ctime = os.stat(f)[-1]
                print(ctime)
                if ctime>=runStrt and ctime <=runEnd: 
                    print('<<< Copying '+filename+' >>>')
                    shutil.copy(f, destinationT)
        
    print('transfer files copied')
    
    bmgloc = 'C:\\Program Files\\BMG\\CLARIOstar\\User\\Data'
    for (dirpath, dirnames, filenames) in os.walk(bmgloc):
        print('Copying BMG files...')
        for filename in filenames:
            print('<<< Processing '+filename+' >>>')
            f = '/'.join([dirpath,filename])
            ctime = os.stat(f)[-1]
            if 'PlateBC' in filename:
                if ctime>=runStrt and ctime <=runEnd: 
                    shutil.copy(f, destinationR)     
    
    os.chdir(destinationT)
    MIPfiles = fnmatch.filter(os.listdir(),'*MIP*')
    for mfile in MIPfiles:
        try:
            dt = pd.read_csv(mfile, nrows = 2, header=None)
            ctime0 = str(dt.iloc[0][1])+' '+str(dt.iloc[1][1])
            ctimet = datetime.datetime.strptime(str(ctime0), '%Y-%m-%d %H:%M:%S')
            ctime = time.mktime(ctimet.timetuple())
            if ctime<=runStrt or ctime >=runEnd: 
                print('removing '+mfile)               
                os.remove(mfile)
        except:
            pass
#    echofiles = fnmatch.filter(os.listdir(),'*-*.xml')
#    for efile in echofiles:
##        if not '.h5' in efile:
#        print('Processing '+efile)
#        with open(efile) as openfile:
##        openfile = open(efile)
#            for line in openfile:
#                if 'date' in line:
#                    ctime0 = line.split('date=')[1].split('"')[1].split('.')[0]
#                    ctimet = datetime.datetime.strptime(str(ctime0), '%Y-%m-%d %H:%M:%S')
#                    ctime = time.mktime(ctimet.timetuple())
#                    if ctime<=runStrt or ctime >=runEnd:
#                        print('removing '+efile)
#                        os.remove(efile)

    os.chdir(destinationR)
    bmgfiles = os.listdir()
    for bmgfile in bmgfiles:
        if 'PlateBC' in bmgfile:
            print ('<< Processing '+bmgfile+' >>')
            dt = pd.read_csv(bmgfile, nrows = 3, header = None)
            ctime0 = dt.iloc[1][0]
            ctimet = datetime.datetime.strptime(str(ctime0), 'Date: %m/%d/%Y  Time: %I:%M:%S %p (UTC--7)')
            ctime = time.mktime(ctimet.timetuple())
            if ctime<=runStrt or ctime >=runEnd: 
                os.remove(bmgfile)
            else:
                plateBC = dt.iloc[2][0].split(' ')[4]
                if not plateBC in platearray:
                    os.remove(bmgfile)
                    
    if style == 'ES':
        es = ess.processEjectSweep()
        testfolder = destination+'\\'+plateType+'\\'+test
        os.chdir(testfolder+'\\TransferPlates')
        
        PA.removeDuplicateSurvey()
        
        dp = PA.plateMap()
        os.chdir(testfolder+'\\ReaderResults')
        files = fnmatch.filter(os.listdir(),'*PlateBC*')
        if files != 0:
            for f in files:
                dest = f.split('_')[1]
                x = dp[dp['Destination_Barcode'].str.contains(dest)].index[0]
                source = dp['Concentration'].loc[x]
                fout = f.replace('PlateBC',str(source)+'_')
                os.rename(f, fout)
            os.chdir(testfolder)
            es.processRawEjectSweep([os.getcwd()], readertype = reader, lutdate=LUTdate, UseInternalStd=True, numTestsPerPlate=1, CCT=False, AspectRatio= 3, Scale = 4)
#            es.processRawEjectSweep([os.getcwd()],readertype=reader,readercal=LUTdate,UseInternalStd=True)
            if not 'HT' in plateType:
                dbA = RA.DBAdjust()
                dbA.updateDB(GUI = False,plateType = plateType, parameter = 'T2T')
            
            os.chdir('C:\\')        #Change working directory to local to avoid UNC path error
            os.system('start '+testfolder)      #Open the folder of the processed data
            
    if style == 'FT':
        testfolder = destination+'\\'+plateType+'\\'+test
        os.chdir(testfolder)
##If using EPR without picklist, specificy concentration
#        if 'DMSO' in plateType.split('_')[-1]:
#            conc = [70, 75, 80, 85, 90, 95, 100]
#        elif 'GP' in plateType.split('_')[-1]:
#            conc = [20, 40, 50]
#        elif 'BP' in plateType.split('_')[-1]:
#            conc = [0, 10, 30]
#        elif 'SP' in plateType.split('_')[-1]:
#            conc = [5, 14, 200]
#        elif 'B2' in plateType.split('_')[-1]:
#            conc = ['2.75', '4', '6', '7', '8' , '9', '10', '12']
#        elif 'CP' in plateType:
#            conc = ['1.48__AQ', '1.763__PEG', '2.247__HEPES']
        PA.ProcessAccess(LUTdate, reader)
        os.chdir(testfolder+'\\Analysis')
        C = CA.calAnalysis()
        C.anaFT()
        os.chdir(destination)
        C.calStatus()
        
        os.chdir('C:\\')        #Change working directory to local to avoid UNC path error
        os.system('start '+testfolder+'\\Analysis')      #Open the folder of the processed data
    
    else:
        print('Files copied.  No further processing...')
        
    return

if __name__ == "__main__":
   main(sys.argv[1:])
