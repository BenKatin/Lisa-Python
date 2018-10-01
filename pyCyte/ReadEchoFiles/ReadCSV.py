# -*- coding: utf-8 -*-
"""
Created on Thu Jan 28 13:56:36 2016

Helper files to process CSV files

@author: avandenbroucke
"""

import csv
from collections import namedtuple

# just as an example: but fields are invalid for SurveyAnalysis CSV   
def readCSV_Named(filename):
    """ Helper function that will open a CSV file as a named Tuple """
    with open(filename, mode="rU") as infile:
        f_csv = csv.reader(infile)
        Data = namedtuple("Data", next(f_csv))  # get names from column headers
        alldat = []
        for row in f_csv:
            data = Data(*row)
            alldat.append(data)
    return alldat
        
def getCSVHeader(filename, headerpos=0):
    """ Helper function that returns the header list of a file 
     Input Arguments : 
        filename  -- 
        headerpos -- position at which header can be found (e.g. "9" for a typical print.csv)
    """ 
    with open(filename, mode="rU") as infile:
       f_csv = csv.reader(infile)
       return list(f_csv)[headerpos] 
   
def readCSV(filename, readasdict=True, fieldnames=None):
    """ Helper function that processes a CSV file. File can be read as a Dict (preferred), or a list.
     Input Arguments:
        filename   --
        readasdict -- if True a dictionary is returne else a list
        fieldnames -- tuple of header fields in case dictionary mode is specified
    """
    records = []
    with open(filename, mode="rU") as infile:
        if (readasdict):
            if fieldnames:
                #print(fieldnames)
                f_csv = csv.DictReader(infile, fieldnames=fieldnames)
            else:
                f_csv = csv.DictReader(infile)  
        else:
            f_csv = csv.reader(infile)
        for row in f_csv:
            records.append(row)
    return  records
    
