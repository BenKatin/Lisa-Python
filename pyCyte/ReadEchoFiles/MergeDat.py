# -*- coding: utf-8 -*-
"""
Created on Thu Apr  5 08:23:47 2018

@author: lchang

Script to extract Echo files and puts them into a dataframe.

"""
import os
import pandas as pd
from ..ReadEchoFiles import ProcessXML as PX
from ..ToolBox import SimpleTools as st

def mergeSurveyXML():
    """ Work in the directory with the files """
    files = PX.getSurveyList()
    PX.survey2csv(files)
    mergeSurveyCSV()
    return
    
def mergeSurveyCSV():
    Timestamp = []
    dat = pd.DataFrame()
    dfName = os.path.split(os.getcwd())[-1]
    parameter = ['TransducerX (um)',
       'TransducerY (um)', 'TransducerZ (um)', 'FW BB ToF (us)', 'FW BB Vpp', 'FW TB1 ToF (us)', 'FW TB1 Vpp',
       'FW TB2 ToF (us)', 'FW TB2 Vpp', 'SR ToF (us)', 'SR Vpp',
       'DMSO (%)', 'FluidThickness','InitialFluidVolume (uL)', 'CurrentEstimatedFluidVolume (uL)',
       'PlateBottomThickness (us)']
    sFiles =  st.getFileList('*.csv')
    if len(sFiles) == 0:
        print('No valid survey .csv files')
        return
    else:
        for p in parameter:
            for s in sFiles:
                try:
                    df = pd.read_csv(s, skiprows = 6)
                    t = pd.to_datetime(s.split('.\\')[-1].split('_')[0].split('-')[0], format = '%m%d%H%M%S')
                    dat = pd.concat([dat,df[p]], axis=1)                
                    Timestamp.append(t)
                except:
                    pass
            dat.columns = Timestamp
            dat.to_csv(p+'_'+dfName+'_surveyMergedData.csv', index=False)
        return
    
def mergeMIPOutput():
    Timestamp = []
    dat = pd.DataFrame()
    dfName = os.path.split(os.getcwd())[-1]
    parameter = ['TransducerZ','FluidHeight','CurrentFluidThickness','Composition','OutputComposition','SubEject Power(dB)','NullSpace(MHz)','SubEjectAmp(Volt)','Calculated Eject Power(dB)','New EjectAmp(Volt)','New EjectAmp+ThreshdB(Volt)','LUT EjectAmp(Volt)','Power Difference(Volt)','Total Iterations','LUT EjectOffset(um)','New EjectOffset(um)']
    files =  st.getFileList('*MIPOutput.csv')
    if len(files) == 0:
        print('No valid MIPOutput .csv files')
        return
    else:
        for p in parameter:
            for f in files:
                df = pd.read_csv(f, skiprows = 6)
                t = pd.to_datetime(f.split('.\\')[-1].split('_')[0]+'_'+f.split('./')[-1].split('_')[1], format = '%Y-%m-%d_%H-%M-%S')
                dat = pd.concat([dat,df[p]], axis=1)                
                Timestamp.append(t)
            dat.columns = Timestamp
            dat.to_csv(p+'_'+dfName+'_MIPMergedData.csv', index=False)
        return
        
        