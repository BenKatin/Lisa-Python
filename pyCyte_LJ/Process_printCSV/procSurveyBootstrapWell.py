# -*- coding: utf-8 -*-
"""
Created on Mon Jan  8 14:32:31 2018

@author: ljungherr
"""
import os
import numpy as numpy
import numpy as np
import pyCyte.ReadEchoFiles.ProcessPlateSurveyCSV
import pandas as pd
import matplotlib.pyplot as plt
import pyCyte.ReadEchoFiles.ReadCSV as csv
import pyCyte.ToolBox.SimpleTools as sbox
SOS = 1495 #Speed of Sound m/sec or mm/msec or um/usec
subdir = '20180324_Freeze_Thaw_Heat'
os.chdir('''\\\\seg\\data\\96SP_Feasibility\\Experiments\\{0}\\'''.format(subdir))

field = 'SR ToF (us)';    ylimits = [32,40]
field = 'BottomEchoAmpRatio' ; ylimits = [ 0.5, 1.0]
field = 'Bottom Thickness (us)' ; ylimits = [ 0.8, 1.0]
field = 'BBToF'   # ; ylimits = [30.8,31.8]

fl = sbox.getFileList('*platesurvey.csv')
hook = '2018';   cIndex = -1

colors = ['green', 'blue', 'purple', 'red', 'brown', 'pink',  'orange','lightblue','yellow','cyan',
     'mediumblue','lightgreen','forestgreen', 'yellow','orange','aliceblue','lavender','violet']

title = """{0} -  {2} {1}""".format(field, hook, subdir)
plt.figure(figsize = (10,6))
# plt.xlim(0,8) ; plt.ylim (ylimits)
plt.xlim(31.18,31.38)
plt.title (title, fontsize = '14')
#plt.xlabel('Current Fluid Thickness (mm)', fontsize = 14)
plt.xlabel('Average BB ToF', fontsize = 14)
plt.ylabel("BB TOF (min - Well B4 - max)", fontsize = 14)
valLists = [] 
   
for f in fl:
  Lcolor = 'blue'    
  if 'PBS' in f:
        Lcolor = 'red'
  if '5C' in f:
        Lcolor = 'green'
  if '14C' in f:
        Lcolor = 'purple'
  if hook in f:
    cIndex += 1
    if cIndex == len(colors):
        cIndex = 0
    fsplit = f.split ('\\'); time = fsplit[2][11:19]
    Tag = plt.scatter ([],[], label = time, color = colors[cIndex])
    pdata = ReadEchoPlateSurveyLisa(f, checkfilename = False)
    
    valList = []; colList = []; thkList = []

    for p in pdata:
        BBtof = getBBToF (p)
        p['BBToF'] = BBtof
        SRToF = getSRToF(p) ; TBToF = getTBToF(p)
        if SRToF and TBToF:
            WellRoundTripUs = SRToF - TBToF ; FluidThicknessMm = WellRoundTripUs * SOS / 2000
            thk = FluidThicknessMm
        val = p[field]
#        thk = p['CurrentFluidThickness (mm)']
        if val and thk:
            thkList.append (float(thk))
            valList.append (float(val))  
        if p['WellName'] == 'B4':
            BootstrapToF = BBtof
#    plt.scatter(thkList,valList, color = colors[cIndex] )
#    plt.hist (valList)

    meanBB = numpy.mean(valList); minBB = numpy.min(valList) ; maxBB = numpy.max (valList)
    plt.scatter (meanBB, BootstrapToF)
    plt.plot([meanBB,meanBB], [minBB, maxBB])
    valLists.append (valList)
    print (f, '  ',  BootstrapToF, numpy.round(numpy.mean(valList),4), numpy.round(numpy.mean(thkList),4))
#  plt.legend (loc = 4 )  
    
    
def ReadEchoPlateSurveyCSV(filename, checkfilename=True):
     """This function will return a matrix of all entries in a platesurvey.csv file as a dict.
     Note that the returned dict contains strings, not numbers. """
     headerrow = 6
     if not filename.endswith('platesurvey.csv') and checkfilename:
         print(' Expected a file ending with \'platesurvey.csv\', filename submitted is :', filename)
     # read in header::
     header = ReadCSV.getCSVHeader(filename, headerrow) 
     # read all entries in file:
     tmpdat = ReadCSV.readCSV(filename, True, tuple(header))
     tmdat = [ row for row in tmpdat if row['WellRow'] != None and row['WellColumn'] != None ] 
     surveydat = [ row for row in tmdat if row['WellColumn'].isdigit() and row['WellRow'].isdigit() and not (row['WellName'].isdigit()) ]
     return surveydat

