# -*- coding: utf-8 -*-
"""
Created on Wed Feb 22 20:28:53 2017

@author: lchang
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 08:15:06 2016

@author: lchang
"""

import sys, getopt
#import argparse
import os
import shutil
import tkinter
import tkinter.filedialog as FD
import errno
import pandas as pd
import datetime
import time
import subprocess
import fnmatch
if __package__ is None or __package__ == '':
    from pyCyte.ToolBox import SimpleTools as st
else:
    from ..ToolBox import SimpleTools as st


def main(argv):
    
    destination = 'C:\\temp'
            
    try:
        opts, args = getopt.getopt(argv,"Dhr:s:pt:st",["RunID=","RunStartDate=","PlateType=", "Style="])
    except getopt.GetoptError:
        print( 'Unknown argument .. please specify: ') 
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print(' Help function .. ')
            sys.exit()
        elif opt in ("-r", "--RunID"):
            runID = arg
            print(runID)
        elif opt in ("-s", "--RunStartDate"):
            runStart = arg
            print(runStart)
        elif opt in ("-pt", "--PlateType"):
            plateType = arg
            print(plateType)

    
    alldata = pd.DataFrame([runID, runStart, plateType])
    alldata.to_csv(destination+('\\')+plateType+'_RunInfo.csv')
        
    return

if __name__ == "__main__":
   main(sys.argv[1:])
