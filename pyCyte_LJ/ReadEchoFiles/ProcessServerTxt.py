# -*- coding: utf-8 -*-
"""
Created on Mon May 14 15:03:48 2018

@author: lchang
"""

import os
import pandas as pd
import datetime

'''
Use getThroughputData to generate the .csv file with all the parsed information from server logs.  
Server logs can either be in server.txt format (serverFormat = 'Echo') or in the EchoComLog.txt format (serverFormat = 'Tempo')

'''

def getThroughputData(f, serverFormat = 'Echo', outputfile = None):
    alldat = parseRawServerTxt(f, serverFormat = serverFormat)
    df = formatServerTxt(alldat)
    if outputfile == None:
        outputfile = f.replace('.txt','_processed.csv')
    df.to_csv(outputfile, index = False)
    return df
        
def parseRawServerTxt(f, serverFormat = 'Echo'):
    with open(f) as file:
        lines = file.readlines()
    file.close()
    alldat = pd.DataFrame()
    if 'EchoComLog' in os.path.basename(f):
        serverFormat = 'Tempo'
    for i, l in enumerate(lines):
        a = l.split('\t')
        if len(a)>2:
            if 'Tempo' in serverFormat:
                if 'INFO' in a[2]:
                    try:
                        t1 = a[0]
                        t2 = datetime.datetime.strptime(str(t1), '%m/%d/%y %H:%M:%S.%f')
        #                t = time.mktime(t2.timetuple())
                        service = a[1]
                        info = a[2]
                        event = a[3].split(' ')[0]
                        status = a[3].split(' ')[-1].split('\n')[0]
                        alldat = alldat.append([[event, info, service, t1, status]],ignore_index=True)
                    except:
                        pass
            else:
                serverFormat = 'Echo'
                if 'INFO' in a[1]:
                    try:
                        t1 = a[0]
                        t2 = datetime.datetime.strptime(str(t1), '%m/%d/%y %H:%M:%S.%f')
    #                t = time.mktime(t2.timetuple())
                        service = a[-1]
                        info = a[1]
                        event = a[2].split(' ')[0]
                        status = a[2].split(' ')[-1].split('\n')[0]
                        alldat = alldat.append([[event, info, service, t1, status]],ignore_index=True)     
                    except:
                        pass
    alldat.columns = ['Event','Info','Service','Timestamp','Status']
    alldat.to_csv(f.replace('.txt','_RawParsed.csv'), index=False)
    return alldat

def formatServerTxt(alldat):
    df = pd.DataFrame()
    epoch = datetime.datetime.utcfromtimestamp(0)
    for i,e in enumerate(alldat['Event']):
        if alldat['Status'].iloc[i] == 'START':
            selectDat = alldat[alldat['Event']==e] 
            allIndex = selectDat[selectDat['Status']=='END'].index
            Ind = allIndex[allIndex > i][0]
            dt0 = pd.to_datetime(datetime.datetime.strptime(str(alldat['Timestamp'].iloc[i]), '%m/%d/%y %H:%M:%S.%f'))
            dt1 = pd.to_datetime(datetime.datetime.strptime(str(alldat['Timestamp'].iloc[Ind]), '%m/%d/%y %H:%M:%S.%f'))
            ddt0 = (dt1-epoch).total_seconds()*1e3
            ddt1 = (dt0-epoch).total_seconds()*1e3
            delta = (ddt1-ddt0)        
            df = df.append([[alldat['Event'].iloc[i],dt0,dt1,ddt1, ddt0, delta,alldat['Info'].iloc[i]]],ignore_index=True)
    df.columns = ['Event','StartTime','EndTime','StartTime(ms)','EndTime(ms)','Duration(ms)','Info']
#    df.to_csv(f.replace('.txt','_processed.csv'),index=False)
    return df
    


            