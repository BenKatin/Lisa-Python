# -*- coding: utf-8 -*-
"""
Created on Mon Sep 11 15:33:11 2017

@author: lchang
"""

import os
import fnmatch
import xml.etree.ElementTree as ET
import pandas as pd
import shutil


def getSurveyList():
    filelist = []
    for path, subdirs, files in os.walk(os.getcwd()):
        for name in files:
            if fnmatch.fnmatch(name, '*.xml'):
                filelist.append(os.path.join(path, name))
#    filelist = fnmatch.filter(filelist, '*.xml')
    surveyfiles = []
    for f in filelist:
        xmlfile = ET.parse(f)
        root = xmlfile.getroot()
        for p in root.iter('platesurvey'):
            surveyfiles.append(f)
    return surveyfiles


def getPrintList():
    filelist = fnmatch.filter(os.listdir(), '*.xml')
    transferfiles = []
    for f in filelist:
        xmlfile = ET.parse(f)
        root = xmlfile.getroot()
        for p in root.iter('transfer'):
            transferfiles.append(f)
    return transferfiles


def print2csv(filelist):
    if len(filelist) == 0:
        print('== No valid print xml files found for conversion ==')
        return
    if len(filelist) != 0:
        for pf in filelist:
            outfile = pf.replace('xml', 'csv')
            xmlfile = ET.parse(pf)
            root = xmlfile.getroot()
            for p in root.iter('transfer'):
                print('== Processing <<<'+pf+'>>> ==')
                alldata = []
                headers = []
                date = root.get('date').split(' ')[0]
                time = root.get('date').split(' ')[1]
                for child in root:
                    for i, subchild in enumerate(child):
                        if 'barcode' in subchild.keys():
                            headers.append(subchild.attrib)
                            dh = pd.DataFrame(headers)
                        if 'barcode' not in subchild.keys():
                            alldata.append(subchild.attrib)
                            alld = pd.DataFrame(alldata)
                            if len(alld.columns) < 35:
                                printdata = \
                                    pd.DataFrame({'Time': alld['t'],
                                                  'SrcWell': alld['n'],
                                                  'SrcWellRow': alld['r'],
                                                  'SrcWellCol': alld['c'],
                                                  'DestWell': alld['dn'],
                                                  'DestWellRow': alld['dr'],
                                                  'DestWellCol': alld['dc'],
                                                  'GeometricX': alld['gx'],
                                                  'GeometrixY': alld['gy'],
                                                  'SkipReason': alld['reason'],
                                                  'MeniscusX': alld['dx'],
                                                  'MeniscusY': alld['dy'],
                                                  'DeltaX': alld['dx'],
                                                  'DeltaY': alld['dy'],
                                                  'Membrane Thickness (um)': alld['memt'],
                                                  'FluidComposition': alld['fc'],
                                                  'FluidThickness (mm)': alld['ft'],
                                                  'VolumeTransferred (nL)': alld['avt']})
                            else:
                                printdata = \
                                    pd.DataFrame({'Time': alld['t'],
                                                  'SrcWell': alld['n'],
                                                  'SrcWellRow': alld['r'],
                                                  'SrcWellCol': alld['c'],
                                                  'DestWell': alld['dn'],
                                                  'DestWellRow': alld['dr'],
                                                  'DestWellCol': alld['dc'],
                                                  'GeometricX': alld['gx'],
                                                  'GeometrixY': alld['gy'],
                                                  'SkipReason': alld['reason'],
                                                  'TransducerZ (um)': alld['tz'],
                                                  'MeniscusX': alld['dx'],
                                                  'MeniscusY': alld['dy'],
                                                  'DeltaX': alld['dx'],
                                                  'DeltaY': alld['dy'],
                                                  'Membrane Thickness (um)': alld['memt'],
                                                  'FluidComposition': alld['fc'],
                                                  'FluidThickness (mm)': alld['ft'],
                                                  'FluidSoundVelocity (m/s)': alld['sv'],
                                                  'FocusToF (us)': alld['tof'],
                                                  'EjectionOffset (um)': alld['eo'],
                                                  'ArbAmplitude (Volts)': alld['aa'],
                                                  'CenterFreq (MHz)': alld['cf'],
                                                  'VolumeTransferred (nL)': alld['avt']})
                try:
                    printd = printdata[['Time',
                                    'SrcWell', 'SrcWellRow', 'SrcWellCol',
                                    'DestWell', 'DestWellRow', 'DestWellCol',
                                    'GeometricX', 'GeometrixY', 'SkipReason',
                                    'TransducerZ (um)',
                                    'MeniscusX', 'MeniscusY',
                                    'DeltaX', 'DeltaY',
                                    'Membrane Thickness (um)',
                                    'FluidComposition', 'FluidThickness (mm)',
                                    'FluidSoundVelocity (m/s)',
                                    'FocusToF (us)',
                                    'EjectionOffset (um)',
                                    'ArbAmplitude (Volts)', 'CenterFreq (MHz)',
                                    'VolumeTransferred (nL)']]
                except:
                    printd = printdata
                printd.to_csv(outfile, index=False)
                datetime = pd.DataFrame({0: ['Date', 'Time', '',
                                             'Source Plate Name',
                                             'Source Plate Barcode ID', '',
                                             'Dest Plate Name',
                                             'Dest Plate Barcode ID', ''],
                                         1: [date, time, '',
                                             dh['name'].iloc[0],
                                             dh['barcode'].iloc[0], '',
                                             dh['name'].iloc[1],
                                             dh['barcode'].iloc[1], '']
                                         })
                completefile = \
                    datetime.append(pd.read_csv(outfile, header=None))
                completefile.to_csv(outfile, index=False, header=False)
    return


def survey2csv(filelist):
    if len(filelist) == 0:
        print('== No valid survey xml files found for conversion ==')
        return
    if len(filelist) != 0:
        for sf in filelist:
            outfile = sf.replace('xml', 'csv')
#            if os.path.isfile(outfile):
            outfile = outfile[:-4] + '_Processed.csv'
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
                        for ii, supersubchild in enumerate(subchild):
                            ss = pd.DataFrame(supersubchild.attrib, index=[0])
                            dss = pd.concat([dss, ss], axis=1)
                        while len(dss.columns) < 9:
                            add = pd.DataFrame({'o': '', 't': 'SR', 'v': ''},
                                               index=[0])
                            dss = pd.concat([dss, add], axis=1)
                        dss1 = pd.concat([dss1, dss])
                        ss = []
                        dss = pd.DataFrame()
                dss1.columns = ('TOF_FWBB', 'BBtype', 'Vpp_FWBB', 'TOF_FWTB1',
                                'FWTB1', 'Vpp_FWTB1', 'TOF_SR', 'SR', 'Vpp_SR')
                survdata = \
                    pd.DataFrame({'WellName': dc['n'],
                                  'WellRow': dc['r'],
                                  'WellColumn': dc['c'],
                                  'TransducerX (um)': ds['x'],
                                  'TransducerY (um)': ds['y'],
                                  'TransducerZ (um)': ds['z'],
                                  'Wall ToF (us)': '', 'Wall Vpp': '',
                                  'EW BB ToF (us)': '', 'EW BB Vpp': '',
                                  'EW TB ToF (us)': '', 'EW TB Vpp': '',
                                  'FW BB ToF (us)': dss1['TOF_FWBB'].values,
                                  'FW BB Vpp': dss1['Vpp_FWBB'].values,
                                  'FW TB1 ToF (us)': dss1['TOF_FWTB1'].values,
                                  'FW TB1 Vpp': dss1['Vpp_FWTB1'].values,
                                  'FW TB2 ToF (us)': '', 'FW TB2 Vpp': '',
                                  'SR ToF (us)': dss1['TOF_SR'].values,
                                  'SR Vpp': dss1['Vpp_SR'].values,
                                  'Unknown ToF (us)': '', 'Unknown Vpp': '',
                                  'DMSO (%)': dc['s'],
                                  'DMSO Filtered (%)': dc['s'],
                                  'DMSO Homo Filtered (%)': dc['fsh'],
                                  'DMSO InHomo Filtered (%)': dc['fsinh'],
                                  'FluidThickness': dc['t'],
                                  'FluidThickness Filtered (mm)': dc['t'],
                                  'FluidThickness Homo Filtered (mm)': dc['fth'],
                                  'FluidThickness InHomo Filtered (mm)': dc['ftinh'],
                                  'Outlier': dc['o'], 'ActionTaken': dc['a'],
                                  'Status': dc['status'], 'InitialFluidVolume (uL)': dc['vl'], 
                                  'CurrentEstimatedFluidVolume (uL)': dc['cvl'],'PlateBottomThickness (us)': dc['b']
                                  })
                survd = survdata[['WellName', 'WellRow', 'WellColumn',
                                  'TransducerX (um)', 'TransducerY (um)',
                                  'TransducerZ (um)',
                                  'Wall ToF (us)', 'Wall Vpp',
                                  'EW BB ToF (us)', 'EW BB Vpp',
                                  'EW TB ToF (us)', 'EW TB Vpp',
                                  'FW BB ToF (us)', 'FW BB Vpp',
                                  'FW TB1 ToF (us)', 'FW TB1 Vpp',
                                  'FW TB2 ToF (us)', 'FW TB2 Vpp',
                                  'SR ToF (us)', 'SR Vpp',
                                  'Unknown ToF (us)', 'Unknown Vpp',
                                  'DMSO (%)', 'DMSO Filtered (%)',
                                  'DMSO Homo Filtered (%)',
                                  'DMSO InHomo Filtered (%)',
                                  'FluidThickness',
                                  'FluidThickness Filtered (mm)',
                                  'FluidThickness Homo Filtered (mm)',
                                  'FluidThickness InHomo Filtered (mm)',
                                  'Outlier', 'ActionTaken', 'Status', 'InitialFluidVolume (uL)', 'CurrentEstimatedFluidVolume (uL)', 
                                  'PlateBottomThickness (us)']]
                survd.to_csv(outfile, index=False)
                datetime = pd.DataFrame({0: ['Date', 'Time', '',
                                             'PlateType', 'Barcode', ''],
                                         1: [date, time, '',
                                             plate, plateBC, '']
                                         })
                completefile = \
                    datetime.append(pd.read_csv(outfile, header=None))
                completefile.to_csv(outfile, index=False, header=False)
            else:
                print(outfile + ' already exists!')
    return
    
def extractEchoXML(parameter = 'E6XX-18002',parameterName='serial_number', folderName = 'E6XX-18002'):
#   parameter is the name to parse by, e.g. 'E6XX-18002' or '384PP_DMSO2'
#   parameterName is the field in the xml file to parse by
#   'serial number' for Echo SN 
#   'name' for plate type
    sfiles = getSurveyList()
    tfiles = getPrintList()
    if len(sfiles) == 0:
        print('== No valid survey xml files found ==')
    else:
        for s in sfiles:
            xmlfile = ET.parse(s)
            root = xmlfile.getroot()
            param = root.get(parameterName)
            if param == parameter:
                destdir = os.path.join(os.getcwd(),folderName)
                if not os.path.exists(destdir):
                    os.makedirs(destdir)
                shutil.move(s,destdir)
    if len(tfiles) == 0:
        print('== No valid transfer xml files found ==')
    else:
        for t in tfiles:
            xmlfile = ET.parse(t)
            root = xmlfile.getroot()
            if parameterName == 'serial_number':
                param = root.get(parameterName)
            else:
                try:
                    for child in root:
                        for i, subchild in enumerate(child):
                            if 'name' in subchild.keys():
                                if 'source' in subchild.get('type'):
                                    param = subchild.get(parameterName)
                except:
                    pass
            if param == parameter:
                destdir = os.path.join(os.getcwd(),folderName)
                if not os.path.exists(destdir):
                    os.makedirs(destdir)
                shutil.move(t,destdir)
    return
                
            
        
        
