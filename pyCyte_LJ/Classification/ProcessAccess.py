# -*- coding: utf-8 -*-
"""
Created on Sun Nov 20 20:48:58 2016

@author: avandenbroucke
"""

def generateDicts(log_fh):
    currentDict = {}
    for line in log_fh:
        if line.startswith(matchDate(line)):
            if currentDict:
                yield currentDict
            currentDict = {"date":line.split("__")[0][:19],"type":line.split("-",5)[3],"text":line.split("-",5)[-1]}
        else:
            currentDict["text"] += line
    yield currentDict

with open("/Users/stevenlevey/Documents/out_folder/out_loyaltybox/log_CardsReport_20150522164636.logs") as f:
    listNew= list(generateDicts(f))
        
    
def matchDate(line):
        matchThis = ""
        matched = re.match(r'\d\d\d\d-\d\d-\d\d\ \d\d:\d\d:\d\d',line)
        if matched:
            #matches a date and adds it to matchThis            
            matchThis = matched.group() 
        else:
            matchThis = "NONE"
        return matchThis    
        
        

import pandas
cnt = 0
with open('./server.txt') as f:
  for line in f:
     print(line)
      cnt += 1
      if ( cnt  > 10 ) : 
              f.close()      
cnt = 0
with open('./server.txt') as f:
  for line in f:
     print(line)
     cnt += 1
     if ( cnt  > 10 ) : 
              f.close()
         
adf
os.listdir()
os.chdir('C:/TMP/')
os.chdir('C:/TMP')
cd Class_14_Plates/
os.listdir()
cnt = 0
with open('./server.txt') as f:
  for line in f:
     print(line)
     cnt += 1
     if ( cnt  > 10 ) : 
              f.close()
         
cnt = 0
with open('./server.txt') as f:
  for line in f:
     print(line)
     cnt += 1
     if ( cnt  > 10 ) : 
              f.close()

from datetime  import datetime
from datetime import timedelta
import matplotlib.pyplot as plt
       
def readServerTXT(filename):
    serverlog = pandas.read_table(filename, error_bad_lines=False, header=None, names=['TimeStamp','Type','Mess','Misc'])
    serverlog['TimeStamp'] = pandas.to_datetime(serverlog['TimeStamp'],errors='coerce')
    serverlog = serverlog.set_index('TimeStamp')
  #  serverlog = serverlog.drop('TimeStamp',axis=1)
    return serverlog
    
for i,r in serverlog['2016-11-18 16:37:00':'2016-11-18 16:37:20'].iterrows():
    print(r['Type'])      
    
plates = [ '384PPG_DMSO', '384PPL_ETOH', '384PPL_DMSO', '384PPL_H20', '384PPG_HEPES', '384PPG_H20', '384PPL_DMSO', '384PPG_DMSO', '384PPG_ETOH','384PPL_H20','384PPL_HEPES','384PPL_DMSO','384PPG_DMSO','384PPG_H20']    


def parseCL(a):
    scoredict = {}
    la = a.split()
    platetype = la[1]
    scorindex = la.index('Classification')
    totscore = la[scorindex+1]
    scoredict['PlateType']=platetype
    scoredict['TotScore'] = totscore
    for r in ['bbvpp','tbbbtof']:
        index = la.index(r)
        score = la[index + 2].replace(',','') 
        scoredict[r] = score
    return scoredict

def processPlateLoad(startt,a,verbose=False):
    ret = {}
    clasres = []
    for i,r in a[str(startt-timedelta(seconds=60)):str(startt)].iterrows():
        if r['Type'] == 'DEBUG' and 'CLAS' in r['Mess']  :
            clasres.append(r['Mess'])
            if (verbose):
                print(i, ' :: ', r['Mess'])
        if r['Type'] == 'INFO' and 'Class' in r['Misc'] :    
            overall = (r['Mess'])
            if (verbose):
                print(overall)
    if len(clasres) == 4 :    
       s0 = parseCL(clasres[0])
       s1 = parseCL(clasres[1])
       result = overall.split()[-1].replace('[','').split('_')[0]
    else:
       s0 = {}
       s0['PlateType'] = 'UNK'
       s0['TotScore'] = 0
       s0['bbvpp'] = 0
       s0['tbbbtof'] = 0
       s1 = s0
       result  = 'UNK'
       
    ret['ResultType'] = result
    if s0['PlateType'] == s1['PlateType']:
        print(' ERRROR AT TIMESTAMP ', startt)
    if 'PPG' in s0['PlateType'] :
       ppgres = s0
       pplres = s1
    else:
       pplres = s0
       ppgres = s1
    ret['PPG-TOT'] = ppgres['TotScore']
    ret['PPG-BBVPP'] = ppgres['bbvpp'] 
    ret['PPG-TOF'] = ppgres['tbbbtof']
    ret['PPL-TOT'] = pplres['TotScore']
    ret['PPL-BBVPP'] = pplres['bbvpp'] 
    ret['PPL-TOF'] = pplres['tbbbtof']
    return ret

def processfile(filename,idx, serverlog,verbose=False):
   time = filename.split('-')[0] 
   plate = plates[idx]
   startt = datetime.strptime('2016' + time, "%Y%m%d%H%M%S")
   if (verbose):
       print( ' filename : ', filename , ' startt ::', startt)
   clasres = processPlateLoad(startt, serverlog,verbose)
   clasres['SourcePlate'] = plate 
   clasres['SourceType'] = plate.split('_')[0]
   if clasres['SourceType'] == clasres['ResultType']:
       clasres['Success'] = 1
   else:    
       clasres['Success'] = 0
   return clasres

def processRun(serverlog, runid=0):
    ALL = []
    l = [ fo for fo in os.listdir() if fo.endswith('.csv')]
    for i,f in enumerate(l):
        idx = f.split('-')[1].replace('.csv','')
        C = processfile(f,int(idx)-1,serverlog)
        C['PlateID'] = idx
        C['RunID'] = runid
        ALL.append(C)
    return pandas.DataFrame(ALL)

def processRunList(runlist, serverlog):
    ALL = pandas.DataFrame()
    for r in runlist:
        thisdir = os.getcwd()
        os.chdir(r)
        A = processRun(serverlog, int(r.split('Run')[1]))
        os.chdir(thisdir)
        ALL = ALL.append(A)           
    return ALL   
    
def plotClassificationResult(A):
    fig,ax = plt.subplots(nrows=1,ncols=2,figsize=(20,5))   
    A[A['SourceType']=='384PPL'][['PPG-BBVPP','PPG-TOF','PPG-TOT','PPL-BBVPP','PPL-TOF','PPL-TOT']].apply(pandas.to_numeric).plot(kind='box',ax=ax[0])
    A[A['SourceType']=='384PPG'][['PPG-BBVPP','PPG-TOF','PPG-TOT','PPL-BBVPP','PPL-TOF','PPL-TOT']].apply(pandas.to_numeric).plot(kind='box',ax=ax[1])
    ax[0].set_title('PPL')
    ax[1].set_title('PPG')