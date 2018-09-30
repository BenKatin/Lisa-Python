# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 13:56:36 2016

@author: avandenbroucke
"""

import os
import fnmatch
import numpy as np
from ..ReadEchoFiles import ReadCSV 
from ..ToolBox import SimpleTools
import pandas as pd
import matplotlib.pyplot as plt

def getListOfPlateSurveyFiles():
     """Finds all *platesurvey.csv files in all subfolders of cwd. Returns list"""      
     return SimpleTools.getFileList('*platesurvey.csv')        
                   
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
    
