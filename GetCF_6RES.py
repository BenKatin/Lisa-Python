# -*- coding: utf-8 -*-
"""
Created on Thu May 10 13:35:56 2018
@author: ljungherr
"""
#data mining to get list of Focal Lengths 

import os
import matplotlib.pyplot as plt
import numpy as numpy
import pandas as pandas
import pyCyte.ToolBox.SimpleTools as sbox
import pyCyte.ReadEchoFiles.ReadCSV as csv

#2018
os.chdir ('\\\\mfg\\PROD_INSTRUMENTS\\2018_UNITS')

dirList = os.listdir()

List5xx = []
List525 = []
AllFrame = pandas.DataFrame(columns=['M'])
for item in dirList:
    if 'E5XX' in item:
        List5xx.append(item)
    if 'E525' in item:
        List525.append(item)

for item in List525:
    notes = ''
    subdir1 = '''\\\\mfg\\PROD_INSTRUMENTS\\2018_UNITS\\{0}\\Backups\\MEDMAN'''.format(item)
    subdir2 = '''\\\\mfg\\PROD_INSTRUMENTS\\2018_UNITS\\{0}\\Backups\\MEDMANdb'''.format(item)
    if (os.path.isdir(subdir1)):
        os.chdir (subdir1)
#        print ('Found dir for ',item)
    elif (os.path.isdir(subdir2)):
            os.chdir(subdir2)
#            print ('Found dir in Medmandb for ',item)
    if (os.path.isdir(subdir1)) and (os.path.isdir(subdir2)):
        notes = "   Found 2 subdir, Using MEDMANdb"

# find either single-file .xls or many files .csv 
    if (os.path.isdir(subdir1)) or (os.path.isdir(subdir2)): 
      flx = sbox.getFileList('*.xls*')
      if len (flx)  >= 1 :
        f = flx[-1]
#        print (item, flx)
      if len (flx) >1:
        notes = '''   Found 2 files, using:{0}'''.format (f)
#load MEDMANdb         
      if len (flx) >=1:
        print ('looking at: ' , item)
        cf = ParseXLSSheet(f)  
        plt.plot(cf['X'],cf['Y']) 
        cf['M'] = item
        
        AllFrame = pandas.concat([AllFrame, cf])
        
 # If no wokrbook, look for a list of single sheets.
       
      else:
        fl = sbox.getFileList('*LUT*.csv')
        if len(fl)>0:
            filename = fl[0]
            headerrow = 0
            header = csv.getCSVHeader(filename, headerrow)
            tmpdat = csv.readCSV(filename, True, tuple(header))

            RESCF = [row for row in tmpdat if row['LUTName'] == 'ToneX_CF_MHz' and '6RES' in row['PlateTypeName'] and row['Description'] =='1' ]

            print (item,  'Found', notes)
        else:
            print (item, 'Omitted')
    

    