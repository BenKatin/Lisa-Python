# -*- coding: utf-8 -*-
"""
Created on Fri Jul 15 15:15:43 2016

@author: ljungherr
"""
#os.chdir('\\\\mfg\PROD_INSTRUMENTS\\2016_UNITS\\E5XX-1605')
#fl = getListOfPlateSurveyFiles()
#fl = sbox.getFileList('*.csv') 
   
#Open a survey file.  Calculate ClassificationGroup based on encoded algorithm.
import os
import numpy as np
import pyCyte.ReadEchoFiles.ProcessPlateSurveyCSV
import pandas as pd
import matplotlib.pyplot as plt
import pyCyte.ReadEchoFiles.ReadCSV as csv
import pyCyte.ToolBox.SimpleTools as sbox
from Clas import Kernels as kern
from Clas import Kernels_norm as kern_norm
from Clas import PlateProfile as plate
#import numpy.corrcoef as cor

def getListOfPlateSurveyFiles():
     """Finds all *platesurvey.csv files in all subfolders of cwd. Returns list"""      
     return sbox.getFileList('*platesurvey.csv') 
     
def ReadEchoPlateSurveyCSV(filename, checkfilename=True):
     """This function will return a matrix of all entries in a platesurvey.csv file as a dict.
     Note that the returned dict contains strings, not numbers. """
     headerrow = 6
     if not filename.endswith('platesurvey.csv') and checkfilename:
         print(' Expected a file ending with \'platesurvey.csv\', filename submitted is :', filename)
     # read in header::
     header = csv.getCSVHeader(filename, headerrow) 
     # read all entries in file:
     tmpdat = csv.readCSV(filename, True, tuple(header))
     tmdat = [ row for row in tmpdat if row['WellRow'] != None and row['WellColumn'] != None ] 
     surveydat = [ row for row in tmdat if row['WellColumn'].isdigit() and row['WellRow'].isdigit() and not (row['WellName'].isdigit()) ]
     return surveydat

def ReadEchoPlateSurveyLisa(filename, checkfilename=False):
     """This function will return a matrix of all entries in a platesurvey.csv file as a dict.
     Note that the returned dict contains strings, not numbers. """
     headerrow = 6
     if not filename.endswith('platesurvey.csv') and checkfilename:
         print(' Expected a file ending with \'platesurvey.csv\', filename submitted is :', filename)
     # read in header::
     header = csv.getCSVHeader(filename, headerrow)
     #many older platesurvey files have headerrow 6 instead of 7; and column names can vary
     if not 'WellRow' in header:
          headerrow = 5
          header = csv.getCSVHeader(filename, headerrow)
     #make uniform text in header for including older versions of platesurvey
     for i in range (1,len(header)):
         header[i] = str.strip(header[i])       #strip leading and strailing white space.
         header[i] = header[i].replace ('TB1', 'TB')
         header[i] = header[i].replace('WellColumn', 'WellCol')
     # read all entries in file:
     tmpdat = csv.readCSV(filename, True, tuple(header))
     tmdat = [ row for row in tmpdat if row['WellName'] != None and row['WellCol'] != None ] 
     surveydat = [ row for row in tmdat if row['WellCol'].isdigit() and row['WellRow'].isdigit() and not (row['WellName'].isdigit()) ]
     return surveydat
     
def ReadEchoMIPOutput(filename, checkfilename=False):
     """This function will return a matrix of all entries in a MIPOutput.csv file as a dict.
     Note that the returned dict contains strings, not numbers. """
     headerrow = 9
     if not filename.endswith('MIPOutput.csv') and checkfilename:
         print(' Expected a file ending with \'MIPOutput.csv\', filename submitted is :', filename)
     # read in header::
     header = csv.getCSVHeader(filename, headerrow)
     for i in range (1,len(header)):
          header[i] = header[i].replace('OutputComposition', 'DMSO (%)')
          header[i] = header[i].replace('SrcWell', 'WellName')

     # read all entries in file:
     tmpdat = csv.readCSV(filename, True, tuple(header))
     tmdat = [ row for row in tmpdat if row['Row'] != None ] 
     surveydat = [ row for row in tmdat if row['Row'].isdigit() and row['Column'].isdigit() and not (row['WellName'].isdigit()) ]
     return surveydat

def findRowByWellName(wellID, thisdata):
    for row in thisdata:
        if row['WellName'] == wellID:
            return row
    return None

# test survey file for charactetistic ratio of Original PP Cav1/2 Plate
def main_Cav1(sdata): 
    #Define numerator and denominator
    numwells = ["H1", "H2", "I1", "I2"]
    denomwells = ["H6", "H7", "I6", "I7"]
    num = avgBBwells(numwells, sdata)
    denom = avgBBwells(denomwells, sdata)
    if (num and denom):
        return num/denom
    if not (num and denom):
        return None

# test survey file for characteristic ratio of Cavity 0 Plate
def main_Cav0():
    sdata = ReadEchoPlateSurveyCSV(f,checkfilename=True)
    #Define numerator and denominator
    numwells = ["H1", "H2", "I1", "I2"]
    denomwells = ["H9", "H10", "I9", "I10"]
    num = avgBBwells(numwells, sdata)
    denom = avgBBwells(denomwells, sdata)

# calculate average BB Vpp for wells in 'welllist', with survey data in 'thisdata'
def avgBBwells(wellList, thisdata):
    BBsum = thisBBValue = 0
    for well in wellList:
        rowdata = findRowByWellName(well, thisdata)
        if not (rowdata):
            return None
        thisBBVal = getBBValue (rowdata)
        if not (thisBBVal):
            return None
        BBsum += thisBBVal
    return BBsum/len(wellList)

# calculate average BB Vpp (corrected for ToF) for wells in 'welllist', with survey data in 'thisdata'.
#'constants' are parameters from 3rd order fit of focalsweep data
# Does not divide by FindCorrFunction(Survey ToF). Works only if the average will be used in a ratio. 
def avgBBCorrected(wellList, thisdata, constants):
    BBsum = 0
    for well in wellList:
        rowdata = findRowByWellName(well, thisdata)
        BBVpp = getBBValue (rowdata)
        BBToF = getBBToF (rowdata)
        Factor = FindCorrFunction(BBToF, constants)
        BBsum += (BBVpp/Factor)
    return BBsum/len(wellList)

# calculate average membrane thickness for wells in 'welllist', with survey data in 'thisdata'
def avgThick(welllist, thisdata):
    Thicksum = 0
    for well in welllist:
        rowdata = findRowByWellName(well, thisdata)
        Thicksum += getMembraneThickness (rowdata)
    return Thicksum/len(welllist)

#Return BB Vpp from one well record from survey file.    
def getBBValue(welldata):
    """Enter a single record of data for one well; return BB Vpp"""
    if welldata:
        if welldata['EW BB Vpp']:
            BBvalue = float(welldata['EW BB Vpp'])
        if welldata['FW BB Vpp']:
            BBvalue = float(welldata['FW BB Vpp'])
        if welldata['Wall Vpp']:
            BBvalue = float(welldata['Wall Vpp'])
        return BBvalue
    return None

def getTBValue(welldata):
    """Enter a single record of data for one well; return BB Vpp"""
    if welldata:
        if welldata['EW TB Vpp']:
            TBvalue = float(welldata['EW TB Vpp'])
        if welldata['FW TB Vpp']:
            TBvalue = float(welldata['FW TB Vpp'])
        if welldata['Wall Vpp']:
            TBvalue = None
        return TBvalue
    return None
    
#Return BB ToF from one well record from survey file.        
def getBBToF(welldata):
#    """Enter a single record of data for one well; return BB ToF"""
    if welldata:
       if welldata['EW BB ToF (us)']:
          BBToF = float(welldata['EW BB ToF (us)'])
       if welldata['FW BB ToF (us)']:
          BBToF = float(welldata['FW BB ToF (us)'])
       if welldata['Wall Vpp']:
          BBToF = float(welldata['Wall ToF (us)'])
       return BBToF
    return None

#Return TB ToF from one well record from survey file.        
def getTBToF(welldata):
    """Enter a single record of data for one well; return TB ToF"""
    if welldata:
        if welldata['EW TB ToF (us)']:
            TBToF = float(welldata['EW TB ToF (us)'])
        if welldata['FW TB ToF (us)']:
            TBToF = float(welldata['FW TB ToF (us)'])
        if welldata['Wall Vpp']:
            TBToF = None
        return TBToF
    return None

#Return SR ToF from one well record from survey file.       
def getSRToF(welldata):
    SRToF = None
    if welldata['SR ToF (us)']:
        SRToF = float(welldata['SR ToF (us)'])
    return SRToF
    
def getFluidThkUs(welldata):
    FluidUs = ""
    TB = getTBToF(welldata)
    SR = getSRToF(welldata)
    if TB and SR:
        FluidUs = round((SR - TB),4)
    return FluidUs
    
def getRowCol(welldata):
    Row = float (welldata['WellRow']) + 1
    Col = float (welldata['WellCol']) + 1
    return Row, Col
    
#Return membrane thickness from one well record from survey file.  
def getMembraneThickness(welldata):
        if welldata:
            if welldata['Wall ToF (us)']:
                return None
            else:
                Thick = getTBToF(welldata) - getBBToF(welldata)
                return Thick
        return None
        
def getTZ(welldata):
    if welldata:
        TZ = float(welldata['TransducerZ'])
        TZ = round(TZ)
        return TZ
    return None
    
def getTX(welldata):
    if welldata:
        TX = float(welldata['GeoX'])
        TX = round(TX)
        return TX
    return None
    
def getTY(welldata):
    if welldata:
        TY = float(welldata['GeoY'])
        TY = round(TY)
        return TY
    return None

def getFocalSweepFilename():
    f = sbox.getFileList('*FocalSweep*.csv')
    return f

def getFocalSweepFit(filename):
    # input Focal Sweep file name; return 3rd order polynomial fit constants  (Headerrow = 8 or 13)
    headerrow = 13
    header = csv.getCSVHeader(filename, headerrow)

    tmpdat = csv.readCSV(filename, True, tuple(header))
    tmdat = [ row for row in tmpdat if row['TransducerZ (um)'] != None and row['BB Amp (Vpp)'] != None ]
    sweepdat = tmdat[1:]

    # get x and y vectors
    x = []; y = []
    for s in sweepdat:
        x.append (s['BB ToF (us)'])
        y.append (s['BB Amp (Vpp)'])

    xx = numpy.array(x, dtype = 'float')
    yy = numpy.array(y, dtype = 'float')
    xlimits = np.linspace (xx[0], xx[-1],3)

    # calculate polynomial
    const = numpy.polyfit(xx, yy, 3)
    ft = np.poly1d(const)
    return (ft, xlimits)

#calculate Correction function from a single ToF value and 3rd order fit contstants.
def findCorrFunction(ToF, constants):
    F = (((constants[0])*ToF+constants[1])*ToF+constants[2])*ToF+constants[3]
    return F

#Calculate Correction function from a single ToF value and linear fit constants.  
def findCorrFunctionLinear(ToF, linearconst):
    F = (linearconst[0] * ToF - linearconst[1])
    return F
if __name__ == "__main__":
    # In Brent's data: Seahorse Article 0:   ToF = 34.761    linearconst = [0.1001, 2.5001]

    OP_92 = [0.5983, 0.6004, 0.6072, 0.6059, 0.5993, 0.5924, 0.5936, 0.6018, 0.6099, 0.6069, 0.6045, 0.6049, 0.6054, 0.6057, 0.6074, 0.6107, 0.6032, 0.5949, 0.5926, 0.6, 0.607, 0.608, 0.6007, 0.5987]

    r6_92 = [0.5905, 0.5898, 0.5931, 0.6067, 0.6086, 0.5888, 0.5926, 0.6103, 0.5995, 0.5972, 0.5985, 0.6057, 0.6111, 0.6003, 0.5988, 0.6002, 0.6117, 0.5946, 0.5932, 0.6128, 0.6088, 0.5944, 0.5916, 0.5925]cl