# -*- coding: utf-8 -*-
"""
Created on Wed Mar  2 09:25:00 2016

@author: avandenbroucke
"""

import os
            
def listunits(search525=False):
    """ lists all units in a certain year relative to the current working directory.
    Returns a list of instruments, 525 instruments are recognized by presence of SP_High or 6RES calibrations"""
    instrlist = []
    curdir = os.getcwd()
    # This expression gets all directories in the folder curdir
    for i in next(os.walk(curdir))[1]:
        is525unit = False
        thisdir = curdir + '\\' + i
        dircontent = next(os.walk(thisdir))[1]
        for ii in dircontent:
            if ( "SP_High" in ii ) or ( "6RES_" in ii ):
                is525unit = True
                break
        if is525unit:
            if search525:
                instrlist.append(i)
        else:
            if not search525:
                instrlist.append(i)
    return instrlist
    
    
def processyear(year='2015', search525 = False):
    """ lists all units of a specific year of a certain flavor"""
    wdir = '\\\\mfg\\mfg\\PROD_INSTRUMENTS\\' + str(year) + '_UNITS'
    os.chdir(wdir)
    li = listunits(search525)
    return li    
        