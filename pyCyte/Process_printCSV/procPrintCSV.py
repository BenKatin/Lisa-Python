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

m = 1445; hook = '2018'
thisDir = '''\\\\seg\\data\\96SP_Feasibility\\Experiments\\20180913_BP_SP_UCP_FT_Prints\\TransferFiles2'''
os.chdir(thisDir)

field = 'MembraneThickness (mm)'; ylimits = [0.6, 1.0]


field = 'ArbAmplitude (Volts)';    ylimits = [1.5,2.1]
field = 'CurrentFluidThickness (mm)'; ylimits = [0, 9]
#ylimits = [2.4,3.1]     #higher limits needed for A2 plates

fl = sbox.getFileList('*print.csv')
cIndex = -1

colors = ['green', 'blue', 'purple', 'red', 'brown', 'pink','black','darkgrey','cyan','lightblue',
     'mediumblue','lightgreen','forestgreen', 'yellow','orange','aliceblue','lavender','violet']
     

title = """{0}     {1}""".format(m, field)
plt.figure(figsize = (10,6))
plt.xlim(0,8.5) ; plt.ylim (ylimits)
plt.title (title, fontsize = '14')
plt.xlabel('Current Fluid Thickness (mm)', fontsize = 14)
plt.ylabel(field, fontsize = 14)
    
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
    fsplit = f; time = fsplit[2][11:19]
#    Tag = plt.scatter ([],[], label = legends[cIndex], color = colors[cIndex])
    pdata = ReadPrintCsv(f, checkfilename = False)
    
    valList = []; colList = []; thkList = []

    for p in pdata:
        col = p['DestWellCol']
        val = p[field]
        thk = p['CurrentFluidThickness (mm)']
        if val and thk:
            colList.append(col)
            thkList.append (float(thk))
            valList.append (float(val))  
    plt.scatter(thkList,valList, color = colors[cIndex] )
    print (f, '    ',  numpy.round(numpy.mean(valList),4), numpy.round(numpy.mean(thkList),4))
#  plt.legend (loc = 4 )  
    

    
    
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
     surveydat = [ row for row in tmdat if row['SrcWellRow'].isdigit() and row['SrcWellRow'].isdigit() ]

     return surveydat

