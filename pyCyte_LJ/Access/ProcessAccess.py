# -*- coding: utf-8 -*-
"""
Created on Mon Oct 31 00:00:31 2016

@author: lchang
"""
import os
import pandas as pd
import numpy as np
import zipfile
import fnmatch
import xml.etree.ElementTree as ET
import subprocess
from ..ToolBox import SimpleTools as st
from ..DropCV import ProcessEPCFinalTest as EPCFT

# Needs :  PlateData file from Tempo, print and survey file from Echo Cache (on Tempo PC), and MIP and H5 files from Echo)

def ProcessAccess(LUTdate, reader):
    thisdir = os.getcwd().split('\\')[-1]
    if not (thisdir == 'FinalTest' or 'FT' in thisdir ):
        print('**** ERROR -- need to be in \' FinalTest \' folder')
        return
    if not os.path.exists('./Analysis'):
        os.makedirs('./Analysis')
    os.chdir('./TransferPlates')
    removeDuplicateSurvey()
    extractPlateData()
#    renameSource(conc)
    plateMap()
    renameFiles()
    renameMIP()
    print2csv()
    survey2csv()
    os.chdir('./..')
    genBCMapAccess()
    EPCFT.processEPCData(reader = reader, cal = LUTdate, useMatech=False, usebarcodemap=True, UseInternalStd=True)
    return

def renameSource(conc = [70, 75, 80, 85, 90, 95, 100]):
    # Enter conc, e.g. [70, 75, 80, 85, 90, 95, 100]
    plateD = st.getFileList('*PlateData*.csv')
    if len(plateD) == 1:
        dp = pd.read_csv(plateD[0])
        print('length of conc: '+str(len(conc)))
        print('length of plateD: '+str(len(dp)))
        if len(dp)/2 != len(conc):
            print('Error:  Concentrations provided does not match number of source plates in print info')
        if len(dp)/2 == len(conc):
    #        source = dp[' Plate Name']
            for index, i in enumerate(dp[' Plate Name']):
                for ii in range(0,len(conc)):
                    PlateName = ' Source['+str(ii+1)+']'
                    if dp[' Plate Name'].loc[index] == PlateName:
                       dp[' Plate Name'].loc[index] = conc[ii]  
            dp.to_csv(plateD[0])
            print('Source Plates renamed')
    else:
        print('Too many / not enough PlateData files found')
    return    
    
def extractPlateData ():
    zfile = st.getFileList('*.zip')
    if len(zfile) == 1:
        z = zipfile.ZipFile(zfile[0])
        for name in z.namelist():
            if fnmatch.fnmatch(name,'*PlateData*.csv'):
                print(name)
                outpath = os.getcwd()
                z.extract(name,outpath)
        z.close()        
    else:
        print('No zip file found')
    return
    

def bcformat (files):
    for i in range(0,len(files)):
        f = open(files[i])
        for line in f:
            if 'barcode' in line:
                l = line.split(' ')[2].split('=')[1].replace('"','')
                print(l)
                fout = l+'_'+files[i]
                print(fout)
        f.close()
        os.rename(files[i],fout)
    return
    
def renameFiles ():
    files = os.listdir()
    files.sort(key=os.path.getmtime)
    platetype = os.getcwd().split('\\')[-3]
    p = pd.read_csv((st.getFileList('platemap.csv'))[0])
    for i in range(0,len(files)):
        if len(files[i].split('--'))>1:
            print('processing transferfile ...')

            sbc, dbc, platetype = getBC(files[i])
            x = p[p['Source_Barcode'].str.contains(sbc)].index[0]
            conc = p['Concentration'].loc[x]
            foutprint = files[i].split('.')[0].replace('--','_')+'__'+str(conc).replace('.0','')+'__'+platetype+'_'+'FT'+'__'+'print.xml'
            print('renaming file')
            os.rename(files[i],foutprint)

        if len(files[i].split('-')) == 2:
            print ('processing surveyfile ...')

            sbc, dbc, platetype = getBC(files[i])
            x = p[p['Source_Barcode'].str.contains(sbc)].index[0]
            conc = p['Concentration'].loc[x]
#            foutsurvey = files[i].split('.')[0].replace('-','_')+'_'+sbc+'__'+str(conc)+'__'+platetype+'_'+'FT'+'__'+'platesurvey.xml'
            foutsurvey = files[i].split('.')[0].replace('-','_')+'__'+str(conc).replace('.0','')+'__'+platetype+'_'+'FT'+'__'+'platesurvey.xml'
#            files[i].close()
            print('renaming file')
            os.rename(files[i],foutsurvey)  
        else:
            print('All files renamed')
    if platetype == '384LDVS_AQ_B2':
        B2files = fnmatch.filter(os.listdir(), '*.0')
        for b in B2files:
            bout = b.replace('.0', '')
            os.rename(b, bout)
    return            

def renameMIP ():

#Remove zero-byte files    
    for dirpath, dirs, files in os.walk('.'):
        for file in files: 
            path = os.path.join(dirpath, file)
            if os.stat(path).st_size == 0:
                os.remove(path)

#Search and rename MIP and h5 files
    mfiles = st.getFileList('*MIPInfo*.csv')
    if len(mfiles) > 0:
        print ('MIP files found')
        mipInfofiles = st.getFileList('*MIP*Info*.csv')
        s = mipInfofiles[0].split('\\')[-1].split('_')[2]
        
        if len(mipInfofiles[0].split('__')) == 1:
            mipInfofiles.sort(key=os.path.getmtime)
            mipOutputfiles = st.getFileList('*MIP*Output*.csv')
            mipOutputfiles.sort(key=os.path.getmtime)
            h5 = st.getFileList('*.h5')
            h5.sort(key=os.path.getmtime)
            p = pd.read_csv((st.getFileList('platemap.csv'))[0])
            
            for j in range(0,len(mipInfofiles)):
                conc = p['Concentration'].loc[j]
                mInfoout = mipInfofiles[j].split('_')[0]+'_'+mipInfofiles[j].split('_')[1]+'__'+str(conc).replace('.0','')+'_'+mipInfofiles[j].split(s)[1].replace('_M','__M')
                mOutputout = mipInfofiles[j].split('_')[0]+'_'+mipInfofiles[j].split('_')[1]+'__'+str(conc).replace('.0','')+'_'+mipOutputfiles[j].split(s)[1].replace('_M','__M')
#                h5out = h5[j].split(s[0:3])[0]+'_'+str(conc).replace('.0','')+'__'+h5[j].split(s[0:3])[-1]
    
                print('renaming MIP files')                    
                os.rename(mipInfofiles[j], mInfoout)
                os.rename(mipOutputfiles[j], mOutputout)
#                os.rename(h5[j], h5out)
        else:
            print('MIP files renamed')
    if len(mfiles) == 0:
        print('no MIP data')

   
def plateMap ():
    files = fnmatch.filter(os.listdir(),'*-*.xml')
    if len(files) == 0:
        print ('No xml files in correct format')
        return
    else:
        sourcebc = []
        destbc = []
        concentration = []
        platefile= st.getFileList('PlateData*.csv')
        plateinfo = pd.read_csv(platefile[0])
        plateinfo.columns = [x.strip().replace(' ', '') for x in plateinfo.columns]
        plateinfo.PlateBarcode = [x.strip().replace(' ', '') for x in plateinfo.PlateBarcode]
        
        for i in range(0,len(files)):
            
            if len(files[i].split('--')) >= 1:
                print('processing file: '+files[i])
                s, d, pt = getBC(files[i])
                
                if d != 'unknown':
                
                    if s == 'UnknownBarCode':
                        if d == 'UnknownBarCode':
                            print ('Both source and destination have unknown barcodes')
                            return
                        else:
                            print('Unknown source barcode, using information from Tempo...')
                            index1 = plateinfo[plateinfo['PlateBarcode'] == d].index.tolist()
                            s = plateinfo['PlateBarcode'].iloc[index1[0]-1]
                    
                    ind = plateinfo[plateinfo['PlateBarcode'] == s].index.tolist()  
                    conc = plateinfo['PlateName'].iloc[ind[0]]
                    concentration.append(conc)
                    sourcebc.append(s)
                    
                    if d == 'UnknownBarCode':
                        print('Unknown dest barcode for source '+s+', using information from Tempo...')
                        d = plateinfo.PlateBarcode.iloc[ind[0]+1]
#                        destbc.append(d)
#                    else:
                    destbc.append(d)
           
        platedata = pd.concat([pd.DataFrame(concentration), pd.DataFrame(sourcebc), pd.DataFrame(destbc)], axis = 1)
        platedata.columns = ['Concentration', 'Source_Barcode','Destination_Barcode']
#            platedata = platedata[platedata.Destination_Barcode.notnull()]
        
        p = platedata[platedata.Destination_Barcode != 'unknown']            
        print ('saving to file....')            
        p.to_csv('platemap.csv')                      
#                        platedata = [{'Concentration': concentration,'Source_Barcode':sourcebc, 'Destination_Barcode':destbc}]
#            platemap = pd.DataFrame(platedata)         
        return p
        
    
def getBC (file):
     if len(file.split('--'))>1 or len(file.split('-'))>1:
        f = open(file)
        for line in f:
            if 'barcode' in line:
                if 'survey' in line:
                    sbc = line.split(' ')[2].split('=')[1].replace('"','')
                    platetype = line.split(' ')[1].split('=')[1].replace('"','')
                    print ('platesurvey source barcode: '+sbc)
                    dbc = 'unknown'
                if 'source' in line:
                    sbc = line.split(' ')[13].split('=')[1].replace('"','')
                    platetype = line.split(' ')[12].split('=')[1].replace('"','')
                    print ('source barcode: '+sbc)
                if 'destination' in line:
                    dbc = line.split(' ')[13].split('=')[1].replace('"','')
                    print ('destination barcode: '+dbc)
                        
        sbc = sbc.replace('&lt;','<')
        sbc = sbc.replace('&gt;','>')
        f.close()
        return (sbc, dbc, platetype)
    
           
def genBCMapAccess(output = True):
    thisdir = os.getcwd().split('\\')[-1]
    if not (thisdir == 'FinalTest' or 'FT' or 'Ejectsweep' in thisdir ):
        print('**** ERROR -- need to be in \' FinalTest \' folder')
        return 
    os.chdir('./TransferPlates')
    p = pd.read_csv((st.getFileList('platemap.csv'))[0])
    os.chdir('./..')
    os.chdir('./ReaderResults')
    mapfilename='./destbarcodemap.csv'    
#    concentrations = fluidconcentrationsdict[plate]
    barcodedfiles= fnmatch.filter(os.listdir(),'*PlateBC_*Labcyte_*csv')
    filemap = []
    for f in barcodedfiles:
        if f.startswith('PlateBC'):
            BC = f.split('_')[1]
            ind = p[p.Destination_Barcode == BC].index.tolist()
            conc = str(p['Concentration'].loc[ind[0]]).split('_')[-1]
            fout = str(conc)+'__'+f
            os.rename(f, fout)
            filemap.append([fout,conc])
        else:
            BC = f.split('_')[3]
            ind = p[p.Destination_Barcode == BC].index.tolist()
            conc = str(p['Concentration'].loc[ind[0]]).split('_')[-1]
            filemap.append([f,conc])
    df = pd.DataFrame(filemap,columns=['destplate','concentration'])
    if (output):    
        print(' Creating file ./destbarcodemap.csv')
        df.to_csv(mapfilename,index=False)   
    os.chdir('./..')
    return 
    
def removeDuplicateSurvey():
    xmlfiles = fnmatch.filter(os.listdir(),'*-*xml')
    xfiles = [xm for xm in xmlfiles if '--' not in xm]
    if len(xfiles) == 2:                
        for i in range(0,len(xfiles)-1):
            if xfiles[i].split('-')[-1] == xfiles[i-1].split('-')[-1]:
                os.remove(xfiles[i]) 
    if len(xfiles) > 2:                
        for i in range(0,len(xfiles)):
            if xfiles[i].split('-')[-1] == xfiles[i-1].split('-')[-1]:
                os.remove(xfiles[i]) 
    return
     

def print2csv():
    printfiles = fnmatch.filter(os.listdir(),'*__print.xml')
    if len(printfiles) == 0:
        print('== No valid print xml files found for coversion ==')
        return
    if len(printfiles) != 0:
        for pf in printfiles:
            outfile = pf.replace('xml','csv')
            if not os.path.isfile(outfile):
                print('== Processing <<<'+pf+'>>> ==')
                xmlfile = ET.parse(pf)
                root = xmlfile.getroot()
                alldata = []
                headers = []
                date = root.get('date').split(' ')[0]
                time = root.get('date').split(' ')[1]
                for child in root:
                    for i, subchild in enumerate(child):
                        if 'barcode' in subchild.keys():
                            headers.append(subchild.attrib)
                            dh = pd.DataFrame(headers)                     
                        if not 'barcode' in subchild.keys():
                            alldata.append(subchild.attrib)
                            alld = pd.DataFrame(alldata)
                            printdata = pd.DataFrame({'Time': alld['t'],	'SrcWell':alld['n'], 'SrcWellRow':alld['r'], 
                            'SrcWellCol':alld['c'], 'DestWell':alld['dn'], 'DestWellRow':alld['dr'], 'DestWellCol':alld['dc'],
                            'GeometricX':alld['gx'],'GeometrixY':alld['gy'], 'SkipReason':alld['reason'],	
                            'TransducerZ (um)':alld['tz'], 'MeniscusX':alld['dx'], 'MeniscusY':alld['dy'], 'DeltaX':alld['dx'], 
                            'DeltaY':alld['dy'], 'Membrane Thickness (um)':alld['memt'],'FluidComposition':alld['fc'], 
                            'FluidThickness (mm)':alld['ft'], 'FluidSoundVelocity (m/s)':alld['sv'], 'FocusToF (us)':alld['tof'],
                            'EjectionOffset (um)':alld['eo'], 'ArbAmplitude (Volts)':alld['aa'], 'CenterFreq (MHz)':alld['cf'],
                            'VolumeTransferred (nL)':alld['avt']})
                printd = printdata[['Time','SrcWell','SrcWellRow','SrcWellCol','DestWell','DestWellRow','DestWellCol','GeometricX','GeometrixY','SkipReason','TransducerZ (um)','MeniscusX','MeniscusY','DeltaX','DeltaY','Membrane Thickness (um)','FluidComposition','FluidThickness (mm)','FluidSoundVelocity (m/s)','FocusToF (us)','EjectionOffset (um)','ArbAmplitude (Volts)','CenterFreq (MHz)','VolumeTransferred (nL)']]
                printd.to_csv(outfile, index = False)
                datetime = pd.DataFrame({0:['Date','Time','','Source Plate Name','Source Plate Barcode ID','','Dest Plate Name','Dest Plate Barcode ID',''],1:[date,time,'',dh['name'].iloc[0],dh['barcode'].iloc[0],'',dh['name'].iloc[1],dh['barcode'].iloc[1],'']})
                completefile = datetime.append(pd.read_csv(outfile, header = None))
                completefile.to_csv(outfile, index = False, header=False)        
    return
         
        
def survey2csv():
    surveyfiles = fnmatch.filter(os.listdir(),'*platesurvey.xml')
    if len(surveyfiles) == 0:
        print('== No valid survey xml files found for coversion ==')
        return
    if len(surveyfiles) != 0:
        for sf in surveyfiles:
            outfile = sf.replace('xml','csv')
            if not os.path.isfile(outfile):
                print('== Processing <<<'+sf+'>>> ==')
                xmlfile = ET.parse(sf)
                root = xmlfile.getroot()
                c = []
                s = []
                ss = []
                dss = pd.DataFrame()
                dss1 = pd.DataFrame()
                date = root.get('date').split(' ')[0]
                time = root.get('date').split(' ')[1]
                plate = root.get('name')
                plateBC = root.get('barcode')
                for child in root:
                    c.append(child.attrib)
                    dc = pd.DataFrame(c)
                    for i, subchild in enumerate(child):
                        s.append(subchild.attrib)
                        ds = pd.DataFrame(s)
    #                    print(' subchild :: ', enumerate(subchild))
                        for ii, supersubchild in enumerate(subchild): 
                            ss = pd.DataFrame(supersubchild.attrib,index=[0])
    #                        print('SSS:: ',ss ) 
    #                        print(' ( ii = ', ii, ')')
                            dss = pd.concat([dss, ss], axis=1)
    #                        print(dss)
                        if len(dss.columns) < 9:
                            add = pd.DataFrame({'o':'','t':'SR','v':''}, index = [0])
                            dss = pd.concat([dss, add], axis=1)
                        dss1 = pd.concat([dss1,dss])
                        ss = []
                        dss = pd.DataFrame()
    #            return dss1             
                dss1.columns = ('TOF_FWBB','BBtype','Vpp_FWBB','TOF_FWTB1','FWTB1','Vpp_FWTB1','TOF_SR','SR','Vpp_SR')
                survdata = pd.DataFrame({'WellName': dc['n'],'WellRow': dc['r'],'WellColumn':dc['c'],'TransducerX (um)':ds['x'],
                                         'TransducerY (um)':ds['y'],'TransducerZ (um)':ds['z'],'Wall ToF (us)':'','Wall Vpp':'',
                                         'EW BB ToF (us)':'','EW BB Vpp':'','EW TB ToF (us)':'','EW TB Vpp':'', 
                                         'FW BB ToF (us)':dss1['TOF_FWBB'].values,'FW BB Vpp':dss1['Vpp_FWBB'].values,'FW TB1 ToF (us)':dss1['TOF_FWTB1'].values,'FW TB1 Vpp':dss1['Vpp_FWTB1'].values,
                                         'FW TB2 ToF (us)':'','FW TB2 Vpp':'','SR ToF (us)':dss1['TOF_SR'].values,'SR Vpp':dss1['Vpp_SR'].values,'Unknown ToF (us)':'',
                                         'Unknown Vpp':'','DMSO (%)':dc['s'],'DMSO Filtered (%)':dc['s'],'DMSO Homo Filtered (%)':dc['fsh'],
                                         'DMSO InHomo Filtered (%)':dc['fsinh'],'FluidThickness':dc['t'],'FluidThickness Filtered (mm)':dc['t'],
                                         'FluidThickness Homo Filtered (mm)':dc['fth'],'FluidThickness InHomo Filtered (mm)':dc['ftinh'],'Outlier':dc['o'],'ActionTaken':dc['a']})
                survd = survdata[['WellName','WellRow','WellColumn','TransducerX (um)','TransducerY (um)','TransducerZ (um)','Wall ToF (us)','Wall Vpp','EW BB ToF (us)','EW BB Vpp','EW TB ToF (us)','EW TB Vpp','FW BB ToF (us)','FW BB Vpp','FW TB1 ToF (us)','FW TB1 Vpp','FW TB2 ToF (us)','FW TB2 Vpp','SR ToF (us)','SR Vpp','Unknown ToF (us)','Unknown Vpp','DMSO (%)','DMSO Filtered (%)','DMSO Homo Filtered (%)','DMSO InHomo Filtered (%)','FluidThickness','FluidThickness Filtered (mm)','FluidThickness Homo Filtered (mm)','FluidThickness InHomo Filtered (mm)','Outlier','ActionTaken']]
                survd.to_csv(outfile, index = False)
                datetime = pd.DataFrame({0:['Date','Time','','PlateType','Barcode',''],1:[date,time,'',plate,plateBC,'']})
                completefile = datetime.append(pd.read_csv(outfile, header = None))
                completefile.to_csv(outfile, index = False, header=False)                 
    return