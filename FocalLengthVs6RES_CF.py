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
import xlrd

#2018
os.chdir ('\\\\mfg\\PROD_INSTRUMENTS\\2018_UNITS')

dirList = os.listdir()

List5xx = []
List525 = []

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
        wb = xlrd.open_workbook(f)
        worksheet = wb.sheet_by_name('FocalSweep')
        FocalToF = worksheet.cell(-1,6).value
        print (item, FocalToF, notes)       
        cf , val = ParseXLSSheet(f)

        plt.scatter(val[1],val[2])
      
      else:
        fl = sbox.getFileList('*FocalSweep*.csv')
        if len(fl)>0:
            filename = sbox.getFileList('*FocalSweep*.csv')[0]
            headerrow = 0
            header = csv.getCSVHeader(filename, headerrow)
            tmpdat = csv.readCSV(filename, True, tuple(header))
            lastCal = tmpdat[-1]
            FocalToF = lastCal['ToFFocus']
            print (item, FocalToF, notes)
        else:
            print (item, 'Omitted')
    

    