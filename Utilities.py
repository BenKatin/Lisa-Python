# -*- coding: utf-8 -*-
"""
Created on Thu Jun  7 11:09:59 2018

@author: ljungherr
"""
import os
import numpy
import numpy as np
import pandas as pd
# %matplotlib inline
import matplotlib.pyplot as plt
import datetime
"""
from pyCyte_EXP.SigPro import FineMipAna
from pyCyte_EXP.ToolBox import SimpleTools
"""
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)
pd.set_option('mode.chained_assignment', None)

# Utils for Lisa's Python

def format_df (new_MI):
    # make uniform  formatting  
    new_MI['NullSpace'] = np.round(new_MI['NullSpace'],4)
    new_MI['MoundWidth'] = np.round(new_MI['MoundWidth'],4)
    new_MI['PeakSeparation'] = np.round(new_MI['PeakSeparation'],4)
    new_MI['PeakFactor'] = np.round(new_MI['PeakFactor'],4)
    new_MI['LeftNull'] = np.round(new_MI['LeftNull'],4)
    new_MI['NullPeak'] = np.round(new_MI['NullPeak'],4)
    new_MI['RightNull'] = np.round(new_MI['RightNull'],4)
    return ()

def countFalseLN(Rold, FFTStarat, GoodNull):
    CountLN = 0
    for i in range (0, len(Rold)):
        wellcombo = gettwellcombo (Rold, i)
        MI_old = g
        if ln == FFTStart:
            CountLN += 1
    return (CountLN)

def getDiffLists(hf, Rold, Rnew):
    fieldList = ['PowerSoln','PowerdB','MoundWidth','PeakSeparation','PeakFactor','NullSpace','LeftNull','NullPeak','RightNull']
    dSet  = [[] for x in range(len(fieldList) )]
    A, B = getCoeff(Echo, hf)
    dp = diff_PowerSolution(h, Rold, Rnew, A, B)
    dSet[0] = dp[1]
    
    if len (Rold) == len(Rnew):       
        for i, field in enumerate (fieldList):
            if i >0:
                diffList = getDiffs(Rold, Rnew, field)
                dSet[i] = diffList
        return (dSet)
            
    if len (Rold) > len(Rnew):
        dSet  = [[] for x in range(len(fieldList) + 1)]
        sDet[0] = dp
        for i in range (0, len(Rold)):
            DW = Rold['DW'][i] ;    SW = Rold['SW'][i]
            wellcombo = '''{0}-{1}'''.format (SW,DW)
            MI_ori = h.getMIPframe(wellcombo=wellcombo)
            MI_ori['PowerMatrix'] = MI_ori['PowerMatrix'].apply(lambda x: int(x) )
            MI_ori['PowerMatrix'] = MI_ori['PowerMatrix'].map('{:02X}'.format)
            MI_ori_iter = getIter(MI_ori)
            Mi_new = h.reprocessMIP(wellcombo=wellcombo)
            Mi_new['PowerMatrix'] = Mi_new['PowerMatrix'].map('{:02X}'.format)
            Mi_new['PowerMatrix'] = '80' + Mi_new['PowerMatrix']
            Mi_new_iter = getIter(Mi_new)
            if Mi_new_iter:
              if ns_ori > 0 and ns_new > 0:
                CEPdB_old = np.log ( ns_ori ) * A + B
                CEPdB_new = np.log ( ns_new ) * A + B
                diffdB = 20* np.log10(Mi_new['Powervolt'][Mi_new_iter]/Rold['Powervolt'][i]) + CEPdB_new - CEPdB_old     
                dSet[0].append (diffdB)
              for j, field in enumerate (fieldList[1:]):
                vOld = MI_ori[field][MI_ori_iter]   #original value for field
                vNew = Mi_new[field][Mi_new_iter]   # value for field after reprocess
                diff = vNew - vOld
                if abs(diff) > 4:
                    print (i, field, wellcombo, diff)
                dSet[j].append(diff)
 
def graphDiffs(Echo, m, hf, dSet, fieldList):

        plt.figure (figsize = (12,9))
        xtargets = [.003, .004, .006, .008, .010, .015, .020, .050, .10, .20, .3, .5, 1,2]
        superTitle = '''  E{1}-{2}\n Rnew value - Rold value for {0}'''.format (hf, Echo, m)
        plt.suptitle (superTitle, fontsize = '14')               
        for k, field in enumerate (fieldList):
            xmin = min(dSet[k])       ;  xmax = max(dSet[k])       
            absmax = max(abs(xmin), abs(xmax), .003) ; newmax = .003
            for i, x in enumerate (xTargets[:-1]):
                if absmax > x:
                    newmax = xTargets [i+1]                   
            xmax = newmax; xmin = -newmax
            print (k,  xmin, '   ', xmax, len(dSet[k]), field)
            ax = plt.subplot(3, 3, k + 1, title = field)
            ax.set_xlim(xmin, xmax)
            ax.set_ylim(0,20)
#            ax.xticks = ([xmin,0, xmax)])
            xlabels = ax.xaxis.get_ticklabels()
            print (len(xlabels))
            every_nth = 3
            if len(xlabels) == 10:
                every_nth = 4
            for n, label in enumerate(ax.xaxis.get_ticklabels()):
                    if n % every_nth != 0:
                        label.set_visible(False)
            ax.hist(dSet[k], bins = 50, range = (xmin, xmax))

#            
#            print(field, xmin, xmax)
#            plt.hist(dSet[k])  ; plt.xlim(xmin, xmax)

        return (dSet)
                
def getDiffs(Rold, Rnew, field):
    if len(Rold) == len(Rnew):
        diffList = []
        for i in range (0, len(Rold)):                  
            diff = Rnew[field][i] - Rold[field][i]
            diffList.append (diff)
        return (diffList)

        print('Different list length')
        for i in range (0, len(Rold)):
            vOld = Rold[field][i]       #original value for field
            DW = Rold['DW'][i]
            SW = Rold['SW'][i]
            wellcombo = '''{0}-{1}'''.format (SW,DW)
            Mi_new = h.reprocessMIP(wellcombo=wellcombo)
            Mi_new_iter = getIter(Mi_new)
            vNew = Mi_new[field][Mi_new_iter]  # value for field after reprocess
            diff = vNew - vOld
            diffList.append (diff)
        return (diffList)

        
def outputDiffs(Rold, Rnew,outfilepath):
    fieldList = ['PowerdB','Powervolt','NullSpace','Preamble','MoundWidth','PeakSeparation','PeakFactor','LeftNull','NullPeak','RightNull']
    diffList = []; outfile = ''''\\\\fserver\\people\\Lisa_Jungherr\\2018\\SigLib_output\\{0}.csv'''.format(outfile)
    for i in range (0, len(Rold)):
        pmSame =  ( Rnew_select['PowerMatrix'][i] == Rold_select['PowerMatrix'][i])
        if not (pmSame):
            outfilepath.write (i, 'PowerMatrix', Rold_select['PowerMatrix'][i], Rnew_select['PowerMatrix'][i], Rold['DW'][i])
            outfilepath.write ('\n')
        for field in fieldList:
            Diff = Rnew_select[field][i] - Rold_select[field][i]
            if abs(Diff) > 0.0015:
                outfilepath.write('''{0}  {1}  {2}  {3} {4}  {5}  \n'''.format (i, field, Rold_select[field][i], Rnew_select[field][i],Diff, Rold['DW'][i]))
                outfilepath.write ('\n')

def diff_PowerSolution(h, Rold, Rnew, A, B):
  hooks = ['PPL_DMSO', '384LDVS_DMSO', 'PPL_AQ_CP', 'PPL_AQ_GP', 'PPL_AQ_BP']
  diffList = []    ; maxDiff = 0; maxDiffCombo = ''
  Columns = '''  {:^10}  {:^12}{:^10} {:^10}  maxDiffWell'''.format('Min (dB)', 'Mean (dB)', 'Max (dB)', 'StdDev')
  if len (Rold) == len(Rnew): 
    #First find Calculated Eject Power for old and new
    for i in range (0,len(Rold)):
        CEPdB_old = np.log ( Rold['NullSpace'][i] ) * A + B
        CEPdB_new = np.log ( Rnew['NullSpace'][i] ) * A + B
        diffdB = 20* np.log10(Rnew['Powervolt'][i]/Rold['Powervolt'][i]) + CEPdB_new - CEPdB_old
        diffList.append(diffdB)
        if abs(diffdB) > .01:
            print (i, Rold['DW'][i], diffdB, Rnew['PowerMatrix'][i])
        if abs(diffdB) > maxDiff:
            maxDiff = abs (diffdB)
            maxDiffCombo = '''{0}-{1}'''.format(Rold['SW'][i],Rold['DW'][i])
    Log1 = sum(abs(d) > .1 for d in diffList)
    Log2 = sum(abs(d) > .01 for d in diffList)
    Log3 = sum(abs(d) > .001 for d in diffList)
    Log4 = sum(abs(d) > .0001 for d in diffList)
    diffStats = '''{:10.4f} {:12.6f} {:10.4f} {:12.6f} {:5} {:5} {:6} {:6}'''.format(np.min(diffList),  np.mean(diffList), 
                   np.max(diffList), np.std(diffList), Log1, Log2, Log3, Log4)
    return (diffStats, diffList, maxDiff, maxDiffCombo)
  else:
      print('Different list length')
      if len(Rnew) == 0:
          print ('No data in Rnew')
          return ('No data in Rnew',0,0,0)
      for i in range (0,len(Rold)):
          DW = Rold['DW'][i]
          SW = Rold['SW'][i]
          wellcombo = '''{0}-{1}'''.format (SW,DW)
          MI_ori = h.getMIPframe(wellcombo=wellcombo)
          ns_ori = Rold['NullSpace'][i] 

          Mi_new = h.reprocessMIP(wellcombo=wellcombo)
          Mi_new['PowerMatrix'] = Mi_new['PowerMatrix'].map('{:02X}'.format)
          Mi_new['PowerMatrix'] = '80' + Mi_new['PowerMatrix']
          Mi_new_iter = getIter(Mi_new)
          if not Mi_new_iter:
              Mi_new_iter = len(Mi_new) - 1
          ns_new = Mi_new['NullSpace'][Mi_new_iter]
          if ns_ori > 0 and ns_new > 0:
              CEPdB_old = np.log ( ns_ori ) * A + B
              CEPdB_new = np.log ( ns_new ) * A + B
              diffdB = 20* np.log10(Mi_new['Powervolt'][Mi_new_iter]/Rold['Powervolt'][i]) + CEPdB_new - CEPdB_old     
              diffList.append(diffdB)  
              if abs(diffdB) > maxDiff:
                  maxDiff = abs (diffdB)
                  maxDiffCombo = '''{0}-{1}'''.format(Rold['SW'][i],Rold['DW'][i])
      if (len(diffList) == 0): 
          print ('No values found in difference List for Power Solution')
          return(0, [], '', '')
      Log1 = sum(abs(d) > .1 for d in diffList) 
      Log2 = sum(abs(d) > .01 for d in diffList)
      Log3 = sum(abs(d) > .001 for d in diffList)
      Log4 = sum(abs(d) > .0001 for d in diffList)      
      diffStats = '''{:10.4f} {:12.6f} {:10.4f} {:12.6f} {:5} {:5} {:6} {:6}'''.format(np.min(diffList),  np.mean(diffList), 
                   np.max(diffList), np.std(diffList), Log1, Log2, Log3, Log4)
#      print(diffStats, maxDiffCombo)
      return (diffStats, diffList, maxDiff, maxDiffCombo)        

def diffSinglePlate(Rold, Rnew):
  if len (Rold) == len(Rnew): 
    #First find Calculated Eject Power for old and new
    for i in range (0,len(Rold)):
        CEPdB_old = np.log ( Rold['NullSpace'][i] ) * A + B
        CEPdB_new = np.log ( Rnew['NullSpace'][i] ) * A + B
        diffdB = 20* np.log10(Rnew['Powervolt'][i]/Rold['Powervolt'][i]) + CEPdB_new - CEPdB_old
        diffLN = Rnew['LeftNull'][i] - Rold['LeftNull'][i]
        diff
        diffList.append(diffdB)
        if abs(diffdB) > maxDiff:
            maxDiff = abs (diffdB)
            maxDiffCombo = '''{0}-{1}'''.format(Rold['SW'][i],Rold['DW'][i])
    diffStats = '''{:10.4f} {:12.6f} {:10.4f} {:12.6f} '''.format(np.min(diffList),  np.mean(diffList), np.max(diffList), np.std(diffList))
    print (Columns)
    print(diffStats)
    return (diffStats, diffList, maxDiff, maxDiffCombo)
  else:
      return('', '', '', '')

def diffSingleWellPower(hf, MI_ori, Mi_new, A, B):
    iterOld = getIter(MI_ori)  ;  iterNew = getIter(Mi_new)
    if not (iterOld == None) and not (iterNew == None):
        ns_ori = MI_ori['NullSpace'][iterOld]       ; vOld = MI_ori['Powervolt'][iterOld]
        ns_new = Mi_new['NullSpace'][iterNew]       ; vNew = Mi_new['Powervolt'][iterNew]
        CEPdB_old = np.log ( ns_ori ) * A + B
        CEPdB_new = np.log ( ns_new ) * A + B
        diffdB = 20* np.log10(vNew/vOld) + CEPdB_new - CEPdB_old
        return (diffdB) 
    else:
        return(None)        

def getWellCombo(Rold, i):
    SW = Rold['SW'][i]
    DW = Rold['DW'][i]
    wc = '''{0}-{1}'''.format(SW, DW)
    return (wc)

def getIter(Mi_one):   
    for i in range (0, len(Mi_one)):
        pm = Mi_one['PowerMatrix'][i][-2:]
        if pm == 'F1' or pm == 'F2' or pm == 'E2' or pm == 'D2':
            iteration = i
            return (iteration)
    return(None)
    
def isPreambleConstant(Mi_one):
    Preamble0 = Mi_one['Preamble'][0] ; startI = 0
    if Preamble0 == 0 and len(Mi_one) > 1 :
        Preamble0 = Mi_one['Preamble'][1] ; startI = 1
    if Preamble0 == 0 and len(Mi_one) >2:
        Preamble0 = Mi_one['Preamble'][2] ; startI = 2
    if Preamble0 == 0 and len(Mi_one) >3:
        Preamble0 = Mi_one['Preamble'][3] ; startI = 3
    for i in range (startI, len(Mi_one)):
        if not (Mi_one['Preamble'][i] == Preamble0):
            failIter = i - 1
            return (False,failIter)
    return (True, len(Mi_one))
    
def isPreambleConstant_X(Mi_one):
    for i in range (0, len(Mi_one)):
        if not Mi_one['Preamble'][i] == 0:
            Preamble0 = Mi_one['Preamble'][i]
            if len(Mi_one) > i:
                for j in range (i+1, len(Mi_one)):                    
                    if not (Mi_one['Preamble'][j] == Preamble0):
                        failIter = j
                        return (False,failIter)
                return (True, len(Mi_one))
        

def getCoeff(Echo, hf):
    if Echo == '5XX': 
        A = 0.57; B = 0.83
        return(A,B)
    if Echo == '525':
        pTypeList = ['384PPL_Plus_AQ_GP', '384PPL_Plus_AQ_GPSA', '384PPL_Plus_AQ_GPSB',
        '384LDV','6RESP_AQ_BP2','6RESP_AQ_GPSA2']
        CoeffA = [0.58, 0.65, 0.72, 0.6,  0.5, 0.6, 0.3258 ]
        CoeffB = [0.6,  0.6,  0.4,  0.83, 1.8, 1.8, 0.8]
        for i, pt in enumerate (pTypeList):
            if pt in hf:
                A = CoeffA[i]
                B = CoeffB[i]
                return (A,B)
        if '6RESP_AQ_GPSB2' in hf:
            Gly_conc = ['0Pct', '10Pct', '20Pct', '30Pct']
            CoeffA = [0.716, 0.793, 0.877, 0.955]
            for i, c in enumerate (Gly_conc):
                if c in hf:
                    A = CoeffA[i]
                    B = 0.8
            return (A, B)
        return (0, 0)
        
def getAllWellCombos():
    colList = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']
    rowList = []
    for i in range (1,25):
        rowList.append(i)
    wellList = []
    for col in colList:
        for row in rowList:
            wellcombo = '''{0}{1}-{0}{1}'''.format(col, row)
            wellList.append (wellcombo)

    return (wellList)
            
def getAllWellCombosFullMI():
    colList = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P']
    rowList = []
    for i in range (1,25):
        rowList.append(i)
    wellList = []
    for col in colList:
        for row in rowList:
            wellcombo = '''{0}{1}-A1'''.format(col, row)
            wellList.append (wellcombo)
            return (wellList)             
            
            
def runManualSearch(h, wellList):
    for wellcombo in wellList:
        MI_ori = h.getMIPframe(wellcombo=wellcombo)
#        if (MI_ori.empty):
#            print ('Empty for ', wellcombo)
        if not (MI_ori.empty):
            ConstPreambleStatus = isPreambleConstant(MI_ori)
            if not ConstPreambleStatus:
                print('Varying Preamble for ', wellcombo)
    return()
           
def ReadPrintCsv(filename, checkfilename=False):
     """This function will return a matrix of all entries in a platesurvey.csv file as a dict.
     Note that the returned dict contains strings, not numbers. """
     headerrow = 9
     if not filename.endswith('platesurvey.csv') and checkfilename:
         print(' Expected a file ending with \'platesurvey.csv\', filename submitted is :', filename)
     # read in header::
     header = csv.getCSVHeader(filename, headerrow)

     for i in range (1,len(header)):
         header[i] = str.strip(header[i])       #strip leading and strailing white space.

     # read all entries in file:
     tmpdat = csv.readCSV(filename, True, tuple(header))
     tmdat = [ row for row in tmpdat if row['FluidComposition'] != None  ]# and tmpdat.index(row) < 400
     surveydat = [ row for row in tmdat if row['Time'] and row['SrcWellRow'].isdigit() ]

     return surveydat

if __name__ == "__main__":
    print(getAllWellCombos())