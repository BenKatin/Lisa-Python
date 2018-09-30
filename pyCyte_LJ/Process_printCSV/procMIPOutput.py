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

subdir = '20180825_E1445_Stability_Xcontam'
os.chdir('''\\\\seg\\data\\96SP_Feasibility\\Experiments\\{0}\\'''.format(subdir))

field = 'ArbAmplitude (Volts)';  ylimits = [1.5,2.1]
field = 'NewEjectAmp (V)';       ylimits = [1.2,1.5] ; xlimits = [0,7]

fl = sbox.getFileList('*MIPOutput.csv')
hook = 'SP';    cIndex = -1

colors = ['green', 'blue', 'cyan', 'purple','red', 'brown', 'pink',  'orange','lightblue','yellow','cyan',
     'mediumblue','lightgreen','forestgreen', 'yellow','orange','aliceblue','lavender','violet']
title = """{2} in {1}""".format(hook, subdir, field)
#title = """{0} -- {1}""".format (subdir, field)
plt.figure(figsize = (9,6))
plt.ylim (ylimits) ; plt.xlim (xlimits)
plt.title (title, fontsize = '15')
plt.xlabel('Current Fluid Thickness (mm)', fontsize = 14)
plt.ylabel(field, fontsize = 14)
    
for f in fl:
  Lcolor = 'blue'    
  if 'BP' in f:
        Lcolor = 'red'
  if 'SP' in f:
        Lcolor = 'green'
  if 'SP_High' in f:
      Lcolor = 'purple'

  if 'BP' in f:
    cIndex += 1
    fsplit = f.split ('\\'); time = fsplit[3][11:19]
    Tag = plt.scatter ([],[], label = time, color = colors[cIndex])
    pdata = ReadMIOutCsv(f, checkfilename = False)
    
    valList = []; colList = []; thkList = []; lutList = []; arbList = []

    for p in pdata:

        NEA = p['New EjectAmp(Volt)']
        LUT = p['LUT EjectAmp(Volt)']
        thk = p['CurrentFluidThickness']
        SRC = p['SrcWell']
        if NEA and thk:
#            colList.append(col)
            thkList.append (float(thk))
            arbList.append (float(NEA)) 
            lutList.append(LUT)
            if float(NEA)  < 1.3:
                print (NEA, SRC, f)                
#                valList.append (val)
    plt.scatter(thkList,arbList, color = colors[cIndex] )

#    plt.scatter (thkList, lutList, color = 'black')
    ValidWells = len(pdata)
#    print (f, '    ',  numpy.round(numpy.mean(arbList),4), numpy.round(numpy.mean(thkList),4))  
plt.legend (loc = 4 )  
  
def ReadMIOutCsv(filename, checkfilename=False):
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
     tmdat = [ row for row in tmpdat if row['Composition'] != None  ]# and tmpdat.index(row) < 400
     surveydat = [ row for row in tmdat if row['Row'].isdigit() and row['Column'].isdigit() ]

     return surveydat

