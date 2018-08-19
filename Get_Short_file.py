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
from openpyxl import load_workbook
import xlrd

def ReadCSVTable(sheetname):
     """This function will return a matrix of all entries in a csv file as a dict.
     Note that the returned dict contains strings, not numbers. """
     headerrow = 0

     # read in header::
     header = csv.getCSVHeader(filename, headerrow) 
     # read all entries in file:
     tmpdat = csv.readCSV(filename, True, tuple(header))
     tmdat = [ row for row in tmpdat if row['LUTName'] != None ]
     printdat = [ row for row in tmdat if row['SrcWellCol'].isdigit() and row['SrcWellRow'].isdigit() and not (row['SrcWell'].isdigit()) ]
     return tmdat

def ParseXLSSheet(fileName):
        xx = pandas.ExcelFile(fileName)
        
        #print(xx.sheet_names)
        tmdat = xx.parse("LUT")

        #print(len(tmdat))
        tmdat = tmdat[tmdat.LUTName == 'ToneX_CF_MHz']
        #print (len(tmdat))
        tmdat = tmdat[tmdat.PlateTypeName == '6RESP_AQ_BP2']
        #print (len(tmdat))
        tmdat = tmdat[tmdat.Description == 1]
        #print (len(tmdat))
            
        tmdat.drop(tmdat.columns[[0,1,2]],axis = 1, inplace = True)

        tmdat = tmdat[['PlateTypeName','X','Y']]
        print (tmdat)        
        return tmdat        
        
        

#2018
os.chdir ('\\\\fserver\\people\\Lisa_Jungherr\\2018\\Python')



# find either single-file .xls or many files .csv  
flx = sbox.getFileList('*.xls*')
if (True):
    if len (flx)  >= 1 :
        f = flx[-1]
#        print (item, flx)
    if len (flx) >1:
        notes = '''   Found 2 files, using:{0}'''.format (f)
#load MEDMANdb         
    if len (flx) >=1:
        
        cf = ParseXLSSheet(f)
           
           
           
     

# Here is where I want to read in the worksheet as a Dictionary; with Keys from Column Names


#        RESCF = [row for row in tmdat if row['LUTName'] == 'ToneX_CF_MHz' and '6RES' in row['PlateTypeName'] and row['Description'] =='1' ]
        
 # If no wokrbook, look for a list of single sheets.
#else:
#        fl = sbox.getFileList('*LUT*.csv')
#        if len(fl)>0:
#            filename = fl[0]
#            headerrow = 0
#            header = csv.getCSVHeader(filename, headerrow)
#            tmpdat = csv.readCSV(filename, True, tuple(header))
#
#            RESCF = [row for row in tmpdat if row['LUTName'] == 'ToneX_CF_MHz' and '6RES' in row['PlateTypeName'] and row['Description'] =='1' ]
#
#            print (item,  'Found', notes)
#        else:
#            print (item, 'Omitted')