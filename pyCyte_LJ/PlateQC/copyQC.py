# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 15:42:19 2018

@author: ACCESS
"""
import os
import time
import pandas
import shutil
if __package__ is None or __package__ == '':
    from pyCyte.ToolBox import SimpleTools
else:
    from ..ToolBox import SimpleTools

DESTDIR = '//mfg/mfg/PlateQC'
SRCDIR = 'C:\\Labcyte\\Echo\\Reports\\Labcyte Echo Plate Audit'

def copyQC(month=1,year=2018):
    # get list of all 
    os.chdir(SRCDIR)
    ALL = SimpleTools.getFileList('*EPAanalysis.csv')
    datestring = '%d_%02d' % (year,month)
    thisDESTDIR = DESTDIR + '/' + datestring
    if not os.path.exists(thisDESTDIR):
        os.makedirs(thisDESTDIR)
    ALL_DATE = [ f for f in ALL if (time.gmtime(os.path.getctime(f))[0] == year) and (time.gmtime(os.path.getctime(f))[1] == month)]
    if len(ALL_DATE) == 0:
        print(' No files found for year ', year, ' and month ', month)
        return
    print(' --- Copying ' + str(len(ALL_DATE)) + ' folders ----- ' )    
    M = pandas.read_csv(ALL_DATE[0])
    for f in ALL_DATE[1:]:
        m = pandas.read_csv(f)
        M = M.append(m)
        thisfolder = os.path.dirname(f)
        for item in os.listdir(thisfolder):
            s = os.path.join(thisfolder,item)
            d = os.path.join(thisDESTDIR,item)
            shutil.copy2(s,d)
        
    M.to_csv(thisDESTDIR + '/QC_' + datestring + '.csv')    
        