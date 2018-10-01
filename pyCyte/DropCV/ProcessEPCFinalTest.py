# -*- coding: utf-8 -*-
"""
Created on Mon May 30 15:04:34 2016

@author: avandenbroucke
"""

from ..ReadEchoFiles import ProcessMIOutputCSV 
from ..ReadEchoFiles import ProcessPlateSurveyCSV
from ..ReadEchoFiles import ProcessPrintCSV
from ..ReadEchoFiles import ReadCSV
from ..DropCV import ReaderDat

import pandas as pd
import os
import matplotlib.pyplot as plt
import fnmatch
import time
import numpy as np

# this needs to be a class for EPC only
# need to specify standard folders users can go to like EastCoastDat, TasmanDat, WestCoastDat, TSwapDat
EASTCOASTDAT = '\\\\seg\\data\\REDPilot\EastCoast'
WESTCOASTDAT = '\\\\seg\\data\\REDPilot\WestCoast'
EUROPEDAT = '\\\\seg\\data\\REDPilot\Europe'
TASMANDAT = '\\\\seg\\data\\REDPilot\Tasman'
TSWAPDAT = '\\\\seg\\transducer\\Transducers'

def getEPCData(useMap=True, wdir=None):
    if wdir == None:
        wdir = os.getcwd()
    thisdir = os.path.basename(wdir)
    if not (thisdir == 'FinalTest' or 'FT' in thisdir ):
        print('**** ERROR -- need to be in \' FinalTest \' folder')
        return 
    # We will do all analysis on existence of printfiles  
    ppf = ProcessPrintCSV.getListOfPrintFiles(wdir) 
    if 'FT' in thisdir:
        pf = [ f for f in ppf if thisdir in f ]
    else:   
        pf = [ f for f in ppf if 'FT' not in os.path.dirname(f) ]    
    if '384PPG_AQ_CP' in wdir or '384PP_AQ_CP' in wdir or '384PPL_AQ_CP' in wdir:
        conc = [ f.split('__')[2] for f in pf if len(f.split('__')) > 2 ]
    else:    
        conc = [ f.split('__')[1] for f in pf if len(f.split('__')) > 2 ]
    alldata =[]
    l = os.listdir(wdir+'/TransferPlates') 
    r = os.listdir(wdir+'/ReaderResults/')
    if (useMap):
        mapfilelist = fnmatch.filter(r,'*barcodemap.csv')
        if len(mapfilelist) == 0:
          print(' *** MAPFILE required when useMap is set to True ( Barcoded plates )' )
          platename = pf[0].split('FinalTest')[0].split('\\')[-2]
          mapfilename = genBarCodeMap(platename) 
          if not mapfilename:
              print(' *** Mapfile could not be created in folder ', os.getcwd() )
              print(' see e.g. \'\\\\seg\\data\\Automation\\Access1619\\BMG\\384LDV_AQ_B2\\FinalTest\\ReaderResults for an example')
              return 
        else:
          mapfile = mapfilelist[0]  
        destbarcodemap = ReadCSV.readCSV('./ReaderResults/' + mapfile,True)
        # some manipulation because volumes should be int's except when they are floats ;-)  
        #( e.g. for 384LDV_AQ_B2, 2.75 forces all concentration to be floats, but that is not what we want)        
        for k in destbarcodemap:
            try:
                thisconc = float(k['concentration'])
                if ( (thisconc % 1) < 0.1 ):
                   k['concentration'] = str(int(thisconc))
            except:
                thisconc = k['concentration']
    for k in conc:  
       thisconc = [ wdir+'/TransferPlates/' + file for file in l if '__' + k + '__' in file and file.endswith('.csv')]
       # this is to deal with CP fluids referenced as AQ, MPD, etc
       kk = k.split('_')[0]  
       if (useMap):
           thisread = [ wdir+'/ReaderResults/' + t['destplate'] for t in destbarcodemap if t['concentration'] == kk ]
       else:    
           thisread = [ wdir+'/ReaderResults/' + file for file in r if ( '_' + kk + '_' in file or file.startswith(kk + '_' ) or '_' + kk + '.' in file or file.startswith(kk +'p_') or file.startswith(kk+'.0')) and 'matech' not in file.lower()]
           print(thisread)
       data = [ k, thisconc + thisread ]
       alldata.append(data)   
    return alldata   

# will have to specify reader and standard curve, guess would do that in the class
# also PMT correction factor
    
def processTransferFiles(filelist):
    surveyfile = [ f for f in filelist if f.endswith('_platesurvey.csv')]
    if len(surveyfile) != 1:
        print('*** Error, no unique surveyfile found in list:', filelist)
        return
    print('---  processing ', surveyfile[0])    
    ps = ProcessPlateSurveyCSV.ReadEchoPlateSurveyCSV(surveyfile[0])
    ps_df = pd.DataFrame(ps)    
    printfile = [ f for f in filelist if f.endswith('_print.csv') ]
    if len(printfile) != 1:
        print('*** Error, no unique printfile found in list:', filelist)
        return
    print('---  processing ', printfile[0])     
    pr = ProcessPrintCSV.ReadEchoPrintCSV(printfile[0])
    pr_df = pd.DataFrame(pr)
    # merging survey and print:
    ps_df['SrcWell'] = ps_df['WellName']
    m_surveyprint = pd.merge(ps_df,pr_df,on='SrcWell',how='left')
    mifile = [ f for f in filelist if f.endswith('_MIPOutput.csv')]
    if len(mifile) != 0:
        if len(mifile) > 1:
            print('*** Error, more than one mipoutputfile found in list:', filelist)
            return
        print('---  processing ', mifile[0])       
        mi_df = ProcessMIOutputCSV.MIPOutputasDF(mifile[0])
        m_transfer = pd.merge(m_surveyprint,mi_df,on='DestWell',how='left')
    else:
        m_transfer = m_surveyprint
    return m_transfer

def processTransferData(datalist,r,pattern=0xFFFF):
    filelist = datalist[1]
    concentration = datalist[0]
    m_transfer = processTransferFiles(filelist)
    # now:: processing reader data
    if ('bmg' in r.reader.lower()):    
        readerfile = [ f for f in filelist if 'readerresults' in f.lower() and f.lower().endswith('.csv')]
    else:
        readerfile = [ f for f in filelist if f.lower().endswith('.xls')] 
    if len(readerfile) != 1:
        print('*** Error, no unique readerdata found in list:', filelist)
        return
    print('---  processing ', readerfile[0])     
    dr = r.processReaderFile(readerfile[0], 24, 16, pattern)
    if (r.bUseInternalStd):
        r.setInternalRefCorr(dr)
    if dr  is None:
        return   
    dc = r.applyCalCurve(dr)
    if dc is None:
        return
    s = r.getPrintStats(dc)
    dc_df = r.readertoDF(dc, concentration)
    m_all = pd.merge(dc_df,m_transfer,on='DestWell')
    m_all = m_all.convert_objects(convert_numeric=True)
    try:
        m_all['PowerState'] = m_all['PowerState'].apply(hex)
    except:
        pass
    thisdata = {}
    thisdata['Conc']=concentration
    thisdata['Reader']=dc
    thisdata['Stats']=s
    thisdata['Merged']=m_all
    return thisdata
    
    
def processEPCData(reader='Biotek2',cal='042016', pattern=0xFFFF, useMatech=True, usebarcodemap=False, UseInternalStd = False, applyPMTCorr = False):
    fl = getEPCData(usebarcodemap)
    if not fl:
        print(' **** ERROR **** :  No files found matching expected EPC pattern' )
        return
    r = ReaderDat.ReaderDat();
    r.setStdCurve(cal,reader, UseInternalStd); 
    if ( os.path.exists('./ReaderResults') ):
        readerfiles = os.listdir('./ReaderResults')
    else:
        print(' **** ERROR **** : no \'ReaderResults\' folder found')
        return
    if (len(readerfiles) < 2):
        print(' **** ERROR **** : not enough reader files found')
        return
    if (useMatech): 
        if ('bmg' in reader.lower()):
            matechfiles = [ './ReaderResults/' + f for f in readerfiles if 'matech' in f.lower() and f.endswith('.csv')]  
        else:    
            matechfiles = [ './ReaderResults/' + f for f in readerfiles if 'matech' in f.lower() and f.endswith('.xls')]    
        if (len(matechfiles) != 2):
           print(' **** ERROR **** : not enough or too many matech files found: ', matechfiles)
           return        
        r.setPMTCorr(matechfiles[0],matechfiles[1]);
        print(' ---- PMT Correction:: ', r.StdCurvePMTCorr, ' ---- Cal:: ', cal, ' ---- ')  
    if applyPMTCorr:
        r.applyPMTCorr = True
    if not ( os.path.exists('./Analysis') ):
        os.makedirs('./Analysis')
    allall = []
    for datalist in fl:
        print('processing ', datalist[1][-1])
        ftstyle = os.getcwd().split('\\')[-1]
        if ( 'FT' in ftstyle ):         
            platetype = os.getcwd().split('\\')[-3]
        else:    
            platetype = os.getcwd().split('\\')[-2]
        d = processTransferData(datalist,r,pattern)
        if not (d) :
            print(' Invalid return in processEPCData while processing concentration ', datalist[0] )
            return  
        allall.append(d) 
        # check if RT MIP enabled
        if (len(d['Merged'].columns) > 60 ):
            genMergeSumPlots(d['Merged'],datalist[0] + '__' + platetype + '__' + ftstyle )
        else:
            genMergeSumPlots(d['Merged'],datalist[0] + '__' + platetype + '__' + ftstyle ,  ['ReaderVol','ReaderVol','ReaderVol', 'ArbAmplitude (Volts)'],
                                                               ['FluidComposition','FluidThickness (mm)','ArbAmplitude (Volts)', 'FluidThickness (mm)'])
    mergedat = allall[0]['Merged']
    for k in range(1,len(allall)):
        mergedat = mergedat.append(allall[k]['Merged'])
        
    mergedat.to_excel('./Analysis/MergeDat__' + platetype + '__' + ftstyle + '.xls')   
    allstats = {}    
    for k in range(0,len(allall)):
        allstats[allall[k]['Conc']]=allall[k]['Stats']
    df = pd.DataFrame(allstats).T  
    df.columns = r.PRINTSTATS_FIELDS
    if  not ( '384PPG_AQ_CP' in os.getcwd() or '384PP_AQ_CP' in os.getcwd() or '384PPL_AQ_CP' in os.getcwd()): 
        df.index = [ float(i) for i in df.index ]    
    df.sort_index().to_csv('./Analysis/DataSummary__' + platetype + '__' + ftstyle + '.csv',  float_format='%.2f', date_format='%Y-%m-%d_%H:%M:%S')
    print(' ---- generating matrix plots ----')
    ncols = 3
    if len(allall) == ncols :
        ncols = 2 
    nrows = (len(allall)-1)//ncols + 1
    if (nrows==1):
        nrows = 2
    fig,ax = plt.subplots(ncols=ncols,nrows=nrows,figsize=(18*ncols,12*nrows))
#    if (len(allall)%ncols):
#        ax[-1,-1].axis('off')    
    for i in range(0,nrows):
        for j in range(0,ncols):
            index = i*ncols + j
            if (index < len(allall)):
                r.plotReaderDat(allall[index]['Reader'],allall[index]['Stats'],ax[i][j],str(allall[index]['Conc']))
            else:
                ax[i,j].axis('off')
    fi = plt.gcf()
#    print("Current working dir: ", os.getcwd(), "saving to ", basedir)
    filename = './Analysis/ReaderData__' + platetype + '__' + ftstyle
   # if (pattern != 0xFFFF ):
   #     filename += '__' + str(pattern) 
    filename += '.png'
    fi.savefig(filename,bbox_inches='tight')  
    plt.close(fi)
    print( df.sort_index() ) 
    return
    
def genMergeSumPlots(merge_df, title='Concentration', yfields=['ReaderVol','ReaderVol','ReaderVol','ReaderVol', 'ArbAmplitude (Volts)','Total Iterations'],
                                                               fields=['FluidComposition','FluidThickness (mm)','ArbAmplitude (Volts)','Total Iterations', 'FluidThickness (mm)','FluidThickness (mm)'],
                                                               foldername = './Analysis'):
    if len(yfields) != len(fields):
        print('ERROR in genMergeSumPlots :: length xfields and yfields don\'t match')
        return
    nrows = len(fields)//2
    ncols=2
    fig, ax = plt.subplots(figsize=(12,8), nrows=nrows,ncols=ncols)
    ind = 0;
    for k in range(0,nrows):
        for j in range(0,ncols):
            val = fields[ind]
            yval = yfields[ind]
            for i in range(0,len(merge_df)):
                if merge_df[val].iloc[i] == '':
                    merge_df[val].iloc[i] = np.nan
            merge_df[val] = merge_df[val].astype('float')
            merge_df[yval] = merge_df[yval].astype('float')
            merge_df.plot(kind='scatter', y=yval, x=val, ax=ax[k][j])
            ind += 1
    plt.subplots_adjust(hspace=.6,top=.85)
    plt.suptitle(title,size=16,x=.5,y=.999) 
    filename = foldername+'/Graph_' + title + '.png'
    print('Saving as file', filename)
    plt.savefig( filename, dpi=200, bbox_inches='tight')
    plt.close(fig)                   
    
    return    
    
def getListOfFTFolders(wdir=None):
     """Finds all *_print.csv files in all subfolders of cwd. Returns list"""      
     FTFolders = []
     if wdir == None :
         wdir = os.getcwd()
     for root, dirs, files in os.walk(wdir):
         for k in fnmatch.filter(dirs,'FinalTest'):
             FTFolders.append(os.path.join(root,k))  
         for k in fnmatch.filter(dirs,'FT?'):
             FTFolders.append(os.path.join(root,k))    
     return FTFolders    

def processListOfFTFolders(FTF,reader='Biotek2',cal='042016', useMatech='True', useBarCodeMap='False'):     
    curdir = os.getcwd()
    for f in FTF:
        os.chdir(f)
        processEPCData(reader,cal,0xFFFF,useMatech, useBarCodeMap)
        os.chdir(curdir)  
    return  
    
def processListOfOmicsFTFolders(FTF,reader='Biotek2',cal='062016UKOmics'):     
    curdir = os.getcwd()
    for f in FTF:
        if not (('DMSO' in f) or ('StdV' in f)):
            os.chdir(f)
            processEPCData(reader,cal)
            os.chdir(curdir)  
    return     
    
def processListOfDMSOFTFolders(FTF,reader='Biotek2',cal='062016UKDMSO'):     
    curdir = os.getcwd()
    for f in FTF:
        if 'DMSO' in f or 'StdV' in f:
            os.chdir(f)
            processEPCData(reader,cal)
            os.chdir(curdir)  
    return         
    
def processUKData(reader='Biotek2'):
     alld = getListOfFTFolders()
     alldmso = [ f for f in alld if 'DMSO' in f or 'StdV' in f ]
     allscreen = [ f for f in alld if not (('DMSO' in f) or ('StdV' in f)) ]
     processListOfDMSOFTFolders(alldmso,reader,'062016UKDMSO')  
     processListOfOmicsFTFolders(allscreen,reader,'062016UKOmics')
     return
     
def genBarCodeMap(plate='384PP_DMSO2'):
     if ( plate == '384PP_DMSO' ):
        plate = '384PP_DMSO2'
     if ( plate == '384LDV_AQ_B'):
         plate = '384LDV_AQ_B2'
     mapfilename='./destbarcodemap.csv'    
     fluidconcentrationsdict = {
       '384PP_DMSO2': [70,75,80,85,90,95,100],
       '384PP_AQ_BP2' : [0,10,30],
       '384PP_AQ_GP2' : [20,40,50],
       '384LDV_AQ_B2' : [2.75,4,6,7,8,9,10,12],
       '384PP_AQ_CP' : ['AQ','PEG','HEPES','MPD'],
     } 
     if ( os.path.basename(os.getcwd()) != 'ReaderResults' ) :
         print (' **** ERROR ***, need to be in *ReaderResults folder for genBarCodeMap to work ')
         return
     if plate not in fluidconcentrationsdict :
         print (' **** ERROR :: unsupported plate ', plate, ' in genBarCodeMap. Supported fluids: ', fluidconcentrationsdict.keys())
         return
     concentrations = fluidconcentrationsdict[plate]
     barcodedfiles= fnmatch.filter(os.listdir(),'*PlateBC_*Labcyte_*csv')
     filemap = []
     for i,f in enumerate(barcodedfiles):
         if i < len(concentrations):
             index = i
         else:
             index = i%len(concentrations)
         filemap.append([f,concentrations[index]])
     df = pd.DataFrame(filemap,columns=['destplate','concentration'])    
     print(' Creating file ./destbarcodemap.csv')
     df.to_csv(mapfilename,index=False)
     return mapfilename
     
     