# -*- coding: utf-8 -*-
import os
if __package__ is None or __package__ == '':
    from pyCyte.Calibration.ExtractPlateSql import *
else:
    from ..Calibration.ExtractPlateSql import *

## Hello user!  Just add this to, e.g. Spyder, and if you have pyCyte in your path, you
## should be able to run the examples below.  Output will land where this file is saved.
## Uncomment the function you want to use and modify the connection/database settings
## in the 'arg' block below.

args = {'Server' : 'ljungherr-dt\labcyte',
  'SourceDatabase' : 'E1240_After_SP_High'}

### This lists all the hidden plates on the system
#print(getListOfHIDPlateTypes(**args))

### This extracts all of the plates to a folder 'ExtractedPlateSQLs' whereever
### this script is saved.
#out = extractAllPlateSql(**args)

### This just extracts one plate and leaves it in the directory where this script is placed.
### You need to type the name of the hidden plate you want to extract. 
out = extractPlateSQL('96PPRE_AQ_SP_High',**args)