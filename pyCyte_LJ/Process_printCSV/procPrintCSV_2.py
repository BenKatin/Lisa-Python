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

m = 18059
thisDir = '''//fserver/people/Geeta/2017/1020201_384LDVS_Plus_AQ_GP_revamp/RnD_Pilot/E{0}'''.format(m)
os.chdir(thisDir)

field = 'FluidComposition'; ylimits = [0,55]; xlimits = [0,55]
#field = 'ArbAmplitude (Volts)';    ylimits = [1.5,2.1]
#ylimits = [2.4,3.1]     #higher limits needed for A2 plates

fl = sbox.getFileList('*print.csv')
cIndex = -1

colors = ['green', 'blue', 'purple', 'red', 'brown', 'pink','black','darkgrey','cyan','lightblue',
     'mediumblue','lightgreen','forestgreen', 'yellow','orange','aliceblue','lavender','violet']
     
#legends = ['Lot 1', 'Lot 1', 'Lot 1', 'Lot 2','Lot 2','Lot 2','Lot 3','Lot 3','Lot 3',]  #For a specific run

title = """{0}     {1}    {2}""".format(m, 'Pilot', field )
plt.figure(figsize = (10,6))
plt.xlim(xlimits)   #; plt.ylim (ylimits)
plt.title (title, fontsize = '14')
plt.xlabel('Measured Conc.', fontsize = 14)
plt.ylabel(field, fontsize = 14)
    
for f in fl:
  if 'FT' in f:
    cIndex += 1
    fsplit = f.split ('\\'); time = fsplit[2][11:19]
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
    plt.hist(valList, bins = 50)
#    plt.scatter(thkList,valList, color = colors[cIndex] )
    print (f, '    ',  numpy.round(numpy.mean(valList),4), numpy.round(numpy.mean(thkList),4))
  plt.legend (loc = 4 )  
    
    
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

